"""Regras de negocio para comentarios de avaliacoes (RF20)."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.avaliacao import Avaliacao
from app.models.enums import EstadoComentario
from app.models.usuario import Usuario
from app.repositories import (
    avaliacao_repository,
    comentario_repository,
    turma_repository,
)


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


def listar_do_autor(db: Session, usuario: Usuario):
    """Lista os comentarios do autor autenticado (todos os estados)."""
    return comentario_repository.listar_por_usuario(db, usuario.id)


def retirar(db: Session, comentario_id: UUID, usuario: Usuario):
    """Retira um comentario pelo autor (PUBLICADO ou PENDENTE)."""
    comentario = comentario_repository.obter_por_id(db, comentario_id)
    if comentario is None:
        raise RecursoNaoEncontradoError("comentario nao encontrado")

    avaliacao = db.get(Avaliacao, comentario.avaliacao_id)
    if avaliacao is None or avaliacao.usuario_id != usuario.id:
        raise ComentarioNaoAutorizadoError(
            "nao autorizado a retirar este comentario"
        )

    if comentario.estado not in (
        EstadoComentario.PENDENTE,
        EstadoComentario.PUBLICADO,
    ):
        raise ComentarioNaoAutorizadoError(
            "nao e possivel retirar este comentario"
        )

    # Cancela eventuais substitutos pendentes deste comentario.
    pendente = comentario_repository.obter_pendente_que_substitui(
        db, comentario_id
    )
    if pendente is not None:
        db.delete(pendente)

    comentario_repository.retirar(db, comentario)
    db.commit()
    db.refresh(comentario)
    return comentario