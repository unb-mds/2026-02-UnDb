from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.comentario_versao import ComentarioVersao
from app.models.enums import EstadoComentario
from app.models.avaliacao import Avaliacao


def bloquear_avaliacao(db: Session, avaliacao_id: UUID) -> None:
    db.scalar(select(Avaliacao).where(Avaliacao.id == avaliacao_id).with_for_update()
              .execution_options(populate_existing=True))


def apagar(db: Session, comentario: ComentarioVersao) -> None:
    db.delete(comentario)


def obter_bloqueado(db: Session, comentario_id: UUID) -> ComentarioVersao | None:
    avaliacao_id = db.scalar(select(ComentarioVersao.avaliacao_id).where(ComentarioVersao.id == comentario_id))
    if avaliacao_id is None:
        return None
    bloquear_avaliacao(db, avaliacao_id)
    return db.scalar(select(ComentarioVersao).where(ComentarioVersao.id == comentario_id)
                     .with_for_update().execution_options(populate_existing=True))


def obter_atual_por_avaliacao(db: Session, avaliacao_id: UUID) -> ComentarioVersao | None:
    return db.scalar(select(ComentarioVersao).where(
        ComentarioVersao.avaliacao_id == avaliacao_id,
        ComentarioVersao.estado.in_((EstadoComentario.PUBLICADO, EstadoComentario.SUSPENSO, EstadoComentario.REMOVIDO)),
    ).order_by(ComentarioVersao.created_at.desc()))


def listar_ativas_por_avaliacao(db: Session, avaliacao_id: UUID) -> list[ComentarioVersao]:
    return list(db.scalars(select(ComentarioVersao).where(
        ComentarioVersao.avaliacao_id == avaliacao_id,
        ComentarioVersao.estado.in_((EstadoComentario.PUBLICADO, EstadoComentario.SUSPENSO, EstadoComentario.PENDENTE)),
    ).order_by(ComentarioVersao.id).with_for_update()))


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


def listar_por_usuario(db: Session, usuario_id: UUID, professor_id: UUID | None = None,
                      disciplina_id: UUID | None = None) -> list[ComentarioVersao]:
    filtros = [Avaliacao.usuario_id == usuario_id]
    if professor_id is not None:
        filtros.append(Avaliacao.professor_id == professor_id)
    if disciplina_id is not None:
        filtros.append(Avaliacao.disciplina_id == disciplina_id)
    return list(
        db.scalars(
            select(ComentarioVersao)
            .where(ComentarioVersao.avaliacao.has(and_(*filtros)))
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
