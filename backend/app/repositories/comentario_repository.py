from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comentario_versao import ComentarioVersao
from app.models.enums import EstadoComentario


def obter_por_id(db: Session, comentario_id: UUID) -> ComentarioVersao | None:
    return db.get(ComentarioVersao, comentario_id)


def obter_pendente_por_avaliacao(
    db: Session, avaliacao_id: UUID
) -> ComentarioVersao | None:
    return db.scalar(
        select(ComentarioVersao)
        .where(
            ComentarioVersao.avaliacao_id == avaliacao_id,
            ComentarioVersao.estado == EstadoComentario.PENDENTE,
        )
        .order_by(ComentarioVersao.created_at.desc())
    )


def obter_publicado_por_avaliacao(
    db: Session, avaliacao_id: UUID
) -> ComentarioVersao | None:
    return db.scalar(
        select(ComentarioVersao)
        .where(
            ComentarioVersao.avaliacao_id == avaliacao_id,
            ComentarioVersao.estado == EstadoComentario.PUBLICADO,
        )
        .order_by(ComentarioVersao.created_at.desc())
    )


def listar_publicados(
    db: Session, professor_id: UUID, disciplina_id: UUID
) -> list[ComentarioVersao]:
    return list(
        db.scalars(
            select(ComentarioVersao)
            .join(ComentarioVersao.avaliacao)
            .where(
                ComentarioVersao.estado == EstadoComentario.PUBLICADO,
                ComentarioVersao.avaliacao.has(
                    professor_id=professor_id, disciplina_id=disciplina_id
                ),
            )
            .order_by(ComentarioVersao.created_at.desc())
        ).all()
    )


def criar(
    db: Session,
    *,
    avaliacao_id: UUID,
    texto: str,
    substitui_id: UUID | None,
) -> ComentarioVersao:
    comentario = ComentarioVersao(
        avaliacao_id=avaliacao_id,
        texto=texto,
        estado=EstadoComentario.PENDENTE,
        substitui_id=substitui_id,
    )
    db.add(comentario)
    db.flush()
    return comentario


def listar_por_usuario(db: Session, usuario_id: UUID) -> list[ComentarioVersao]:
    return list(
        db.scalars(
            select(ComentarioVersao)
            .where(ComentarioVersao.avaliacao.has(usuario_id=usuario_id))
            .order_by(ComentarioVersao.created_at.desc())
        ).all()
    )


def obter_pendente_que_substitui(
    db: Session, comentario_id: UUID
) -> ComentarioVersao | None:
    return db.scalar(
        select(ComentarioVersao).where(
            ComentarioVersao.substitui_id == comentario_id,
            ComentarioVersao.estado == EstadoComentario.PENDENTE,
        )
    )


def retirar(db: Session, comentario: ComentarioVersao) -> ComentarioVersao:
    comentario.estado = EstadoComentario.RETIRADO
    db.flush()
    return comentario
