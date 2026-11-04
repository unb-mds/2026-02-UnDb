"""Regras de negocio para comentarios de avaliacoes (RF20)."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import EstadoComentario
from app.models.usuario import Usuario
from app.repositories import (
    avaliacao_repository,
    comentario_repository,
    turma_repository,
    denuncia_repository,
    moderacao_repository,
)
from app.services.moderacao_service import agora_utc, RETENCAO


class RecursoNaoEncontradoError(Exception):
    pass


class ComentarioNaoAutorizadoError(Exception):
    pass


def listar_publicados(db: Session, professor_id: UUID, disciplina_id: UUID):
    """Lista textos publicados de um professor/disciplina (visitante)."""
    if avaliacao_repository.obter_professor(db, professor_id) is None:
        raise RecursoNaoEncontradoError("professor nao encontrado")
    if avaliacao_repository.obter_disciplina(db, disciplina_id) is None:
        raise RecursoNaoEncontradoError("disciplina nao encontrada")
    if not turma_repository.existe_vinculo_professor_disciplina(
        db, professor_id, disciplina_id
    ):
        raise RecursoNaoEncontradoError(
            "professor nao possui vinculo com a disciplina"
        )
    return comentario_repository.listar_publicados(db, professor_id, disciplina_id)


def listar_do_autor(db: Session, usuario: Usuario, professor_id: UUID | None = None,
                   disciplina_id: UUID | None = None):
    """Lista os comentarios do autor autenticado (todos os estados)."""
    moderacao_repository.descartar_vencidos(db, agora_utc())
    resultado = comentario_repository.listar_por_usuario(db, usuario.id, professor_id, disciplina_id)
    db.commit()
    return resultado


def retirar(db: Session, comentario_id: UUID, usuario: Usuario):
    """Retira um comentario pelo autor (PUBLICADO, PENDENTE ou SUSPENSO)."""
    comentario = comentario_repository.obter_bloqueado(db, comentario_id)
    if comentario is None:
        raise RecursoNaoEncontradoError("comentario nao encontrado")

    if comentario.avaliacao.usuario_id != usuario.id:
        raise ComentarioNaoAutorizadoError(
            "nao autorizado a retirar este comentario"
        )

    if comentario.estado not in (
        EstadoComentario.PENDENTE,
        EstadoComentario.PUBLICADO,
        EstadoComentario.SUSPENSO,
    ):
        raise ComentarioNaoAutorizadoError(
            "nao e possivel retirar este comentario"
        )

    try:
        # Retirada explicita tambem vale quando o autor seleciona seu substituto.
        agora = agora_utc()
        versoes = comentario_repository.listar_ativas_por_avaliacao(db, comentario.avaliacao_id)
        for versao in versoes:
            denuncia_repository.encerrar(db, versao.id, "CONTEUDO_RETIRADO")
            if versao.estado == EstadoComentario.PENDENTE and versao.id != comentario.id:
                comentario_repository.apagar(db, versao)
            else:
                versao.estado = EstadoComentario.RETIRADO
                versao.updated_at = agora
                versao.descartar_em = agora + RETENCAO
        db.commit()
        db.refresh(comentario)
        return comentario
    except Exception:
        db.rollback()
        raise
