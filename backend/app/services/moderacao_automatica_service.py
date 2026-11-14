"""Publica somente versão nova sem sinais locais/externos; falhas preservam pendência."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.core import config
from app.domain.triagem_comentario import VERSAO_LISTA, categorias_lexicais, contem_dados_sensiveis
from app.models.enums import EstadoComentario
from app.repositories import comentario_repository, denuncia_repository, moderacao_repository
from app.services import openai_triagem
from app.services.moderacao_service import RETENCAO, agora_utc
from app.services.triagem_service import limite


def processar(db: Session, versao_id: UUID) -> EstadoComentario | None:
    """Executado depois do commit de critérios/texto, nunca dentro da escrita inicial."""
    if not (
        config.MODERACAO_AUTOMATICA_ATIVA
        and config.MODERACAO_FILTRO_ATIVO
        and config.MODERACAO_IA_ATIVA
        and config.MODERACAO_IA_DADOS_APROVADOS
        and config.OPENAI_API_KEY
    ):
        return EstadoComentario.PENDENTE
    try:
        versao = comentario_repository.obter_por_id(db, versao_id)
        if versao is None or versao.estado != EstadoComentario.PENDENTE:
            return None
        texto = versao.texto
        autor = versao.avaliacao.usuario
        if (
            not texto
            or len(texto) > 500
            or categorias_lexicais(texto)
            or contem_dados_sensiveis(texto, (autor.nome, autor.email))
        ):
            return EstadoComentario.PENDENTE
        # Sem locks/transação aberta durante o acesso à OpenAI.
        db.rollback()
        if not limite.reservar(config.MODERACAO_IA_POR_MINUTO, config.MODERACAO_IA_POR_DIA):
            return EstadoComentario.PENDENTE
        resultado = openai_triagem.classificar(
            texto,
            chave=config.OPENAI_API_KEY,
            modelo=config.OPENAI_MODERACAO_MODEL,
            timeout=max(1, min(config.MODERACAO_IA_TIMEOUT, 30)),
        )
        if resultado.sinalizado or resultado.categorias:
            return EstadoComentario.PENDENTE
        versao = comentario_repository.obter_bloqueado(db, versao_id)
        if versao is None or versao.estado != EstadoComentario.PENDENTE or versao.texto != texto:
            db.rollback()
            return None
        atual = comentario_repository.obter_atual_por_avaliacao(db, versao.avaliacao_id)
        if atual is not None and (
            atual.id != versao.substitui_id
            or atual.estado != EstadoComentario.PUBLICADO
            or denuncia_repository.listar(db, atual.id)
        ):
            db.rollback()
            return EstadoComentario.PENDENTE
        agora = agora_utc()
        if atual is not None:
            atual.estado = EstadoComentario.SUBSTITUIDO
            atual.texto = None
            atual.descartar_em = None
            atual.updated_at = agora
        versao.estado = EstadoComentario.PUBLICADO
        versao.updated_at = agora
        moderacao_repository.registrar_decisao(
            db,
            comentario_versao_id=versao.id,
            moderador_id=None,
            acao="APROVAR",
            motivo=f"Publicação automática sem sinais. {openai_triagem.VERSAO_INTEGRACAO}; lista {VERSAO_LISTA}; modelo {resultado.modelo}",
            estado_anterior=EstadoComentario.PENDENTE.value,
            estado_posterior=EstadoComentario.PUBLICADO.value,
            created_at=agora,
            descartar_em=agora + RETENCAO,
        )
        db.commit()
        return EstadoComentario.PUBLICADO
    except Exception:
        # Não propagar falha da triagem como perda de critérios já confirmados.
        # Nunca registrar a exceção bruta, que pode incluir dados do comentário.
        db.rollback()
        return EstadoComentario.PENDENTE
