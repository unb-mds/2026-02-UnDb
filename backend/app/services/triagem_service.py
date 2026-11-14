"""Análise sob demanda: não persiste conteúdo, pareceres ou decisões."""

from collections import deque
from threading import Lock
from time import monotonic
from uuid import UUID

from sqlalchemy.orm import Session

from app.core import config
from app.domain.triagem_comentario import VERSAO_LISTA, categorias_lexicais, contem_dados_sensiveis
from app.models.enums import EstadoComentario
from app.models.usuario import Usuario
from app.repositories import comentario_repository, denuncia_repository
from app.schemas.triagem import TriagemResponse
from app.services import moderacao_service, openai_triagem


class LimiteChamadas:
    """Orçamento por processo, sem texto/ID. Reiniciar processo reinicia limites."""

    def __init__(self):
        self.chamadas = deque()
        self.lock = Lock()

    def reservar(self, por_minuto: int, por_dia: int) -> bool:
        agora = monotonic()
        with self.lock:
            while self.chamadas and self.chamadas[0] <= agora - 86400:
                self.chamadas.popleft()
            if len(self.chamadas) >= min(por_dia, 1000) or sum(
                t > agora - 60 for t in self.chamadas
            ) >= min(por_minuto, 30):
                return False
            self.chamadas.append(agora)
            return True


limite = LimiteChamadas()


def obter_elegivel(db: Session, usuario: Usuario, versao_id: UUID):
    moderacao_service.autorizar(usuario)
    versao = comentario_repository.obter_por_id(db, versao_id)
    if versao is None:
        raise moderacao_service.ModeracaoError(404, "comentario nao encontrado")
    if versao.avaliacao.usuario_id == usuario.id:
        raise moderacao_service.ModeracaoError(403, "moderador impedido por autoria")
    if denuncia_repository.existe_da_conta(db, versao.id, usuario.id):
        raise moderacao_service.ModeracaoError(403, "moderador impedido por denuncia propria")
    if versao.substitui_id and denuncia_repository.existe_da_conta(
        db, versao.substitui_id, usuario.id
    ):
        raise moderacao_service.ModeracaoError(
            403, "moderador impedido por denuncia da versao anterior"
        )
    if (
        versao.estado
        not in (EstadoComentario.PENDENTE, EstadoComentario.PUBLICADO, EstadoComentario.SUSPENSO)
        or not versao.texto
    ):
        raise moderacao_service.ModeracaoError(409, "versao indisponivel para triagem")
    return versao


def analisar(db: Session, usuario: Usuario, versao_id: UUID) -> TriagemResponse:
    versao = obter_elegivel(db, usuario, versao_id)
    texto, estado = versao.texto, versao.estado
    autor = versao.avaliacao.usuario
    sensivel = contem_dados_sensiveis(texto, (autor.nome, autor.email))
    resposta = TriagemResponse(
        comentario_versao_id=versao_id,
        status="DESATIVADA",
        filtro_ativo=config.MODERACAO_FILTRO_ATIVO,
        versao_lista=VERSAO_LISTA,
        categorias_locais=categorias_lexicais(texto) if config.MODERACAO_FILTRO_ATIVO else [],
        versao_integracao=openai_triagem.VERSAO_INTEGRACAO,
    )
    if not config.MODERACAO_IA_ATIVA or not config.MODERACAO_IA_DADOS_APROVADOS:
        return resposta
    if len(texto) > 500 or sensivel:
        resposta.status = "DADOS_SENSIVEIS"
        return resposta
    if not config.OPENAI_API_KEY or not config.OPENAI_MODERACAO_MODEL:
        resposta.status = "INDISPONIVEL"
        return resposta
    if not limite.reservar(config.MODERACAO_IA_POR_MINUTO, config.MODERACAO_IA_POR_DIA):
        resposta.status = "LIMITE"
        return resposta
    # Libera a transação antes do acesso externo; a versão é conferida novamente.
    db.rollback()
    try:
        resultado = openai_triagem.classificar(
            texto,
            chave=config.OPENAI_API_KEY,
            modelo=config.OPENAI_MODERACAO_MODEL,
            timeout=max(1, min(config.MODERACAO_IA_TIMEOUT, 30)),
        )
    except openai_triagem.TriagemIndisponivel:
        resposta.status = "INDISPONIVEL"
    else:
        atual = obter_elegivel(db, usuario, versao_id)
        if atual.texto != texto or atual.estado != estado:
            raise moderacao_service.ModeracaoError(409, "versao mudou; atualize a fila")
        resposta.status = "CONCLUIDA"
        resposta.modelo = resultado.modelo
        resposta.categorias_ia = resultado.categorias
        resposta.sinalizado = resultado.sinalizado
    return resposta
