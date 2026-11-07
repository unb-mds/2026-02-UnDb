from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update, or_, exists
from sqlalchemy.orm import Session

from app.models.comentario_versao import ComentarioVersao
from app.models.decisao_moderacao import DecisaoModeracao
from app.models.enums import EstadoComentario
from app.models.usuario import Usuario
from app.models.denuncia import Denuncia


def descartar_vencidos(db: Session, agora: datetime) -> None:
    db.execute(delete(DecisaoModeracao).where(DecisaoModeracao.descartar_em <= agora))
    db.execute(
        update(ComentarioVersao)
        .where(
            ComentarioVersao.descartar_em <= agora,
            ComentarioVersao.estado.in_((EstadoComentario.RETIRADO, EstadoComentario.REMOVIDO)),
        )
        .values(texto=None, descartar_em=None)
    )


def listar_fila(db: Session, estado: EstadoComentario | None = None) -> list[ComentarioVersao]:
    consulta = select(ComentarioVersao).where(
        or_(
            ComentarioVersao.estado.in_((EstadoComentario.PENDENTE, EstadoComentario.SUSPENSO)),
            (ComentarioVersao.estado == EstadoComentario.PUBLICADO)
            & exists().where(Denuncia.comentario_versao_id == ComentarioVersao.id),
        )
    )
    if estado is not None:
        consulta = consulta.where(ComentarioVersao.estado == estado)
    return list(db.scalars(consulta.order_by(ComentarioVersao.created_at, ComentarioVersao.id)))


def registrar_decisao(db: Session, **dados) -> DecisaoModeracao:
    decisao = DecisaoModeracao(**dados)
    db.add(decisao)
    db.flush()
    return decisao


def listar_decisoes(db: Session, versao_id: UUID) -> list[DecisaoModeracao]:
    return list(
        db.scalars(
            select(DecisaoModeracao)
            .where(
                DecisaoModeracao.comentario_versao_id == versao_id,
            )
            .order_by(DecisaoModeracao.created_at, DecisaoModeracao.id)
        )
    )


def definir_papel(db: Session, email: str, conceder: bool) -> Usuario:
    usuario = db.scalar(select(Usuario).where(Usuario.email == email).with_for_update())
    if usuario is None or (conceder and not usuario.email_confirmado):
        raise ValueError("conta inexistente ou email nao confirmado")
    usuario.moderador = conceder
    db.flush()
    return usuario
