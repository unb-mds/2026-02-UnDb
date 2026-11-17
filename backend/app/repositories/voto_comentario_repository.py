from uuid import UUID

from sqlalchemy import case, delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models.voto_comentario import VotoComentario


def resumir(db: Session, versao_id: UUID, usuario_id: UUID | None) -> dict:
    uteis, nao_uteis, meu_voto = db.execute(
        select(
            func.count(case((VotoComentario.voto == "UTIL", 1))),
            func.count(case((VotoComentario.voto == "NAO_UTIL", 1))),
            func.max(case((VotoComentario.usuario_id == usuario_id, VotoComentario.voto))),
        ).where(VotoComentario.comentario_versao_id == versao_id)
    ).one()
    return {"uteis": uteis, "nao_uteis": nao_uteis, "meu_voto": meu_voto}


def definir(db: Session, versao_id: UUID, usuario_id: UUID, voto: str | None) -> None:
    if voto is None:
        db.execute(
            delete(VotoComentario).where(
                VotoComentario.comentario_versao_id == versao_id,
                VotoComentario.usuario_id == usuario_id,
            )
        )
    else:
        # O mesmo contrato é exercitado em SQLite nos testes determinísticos.
        inserir = pg_insert if db.get_bind().dialect.name == "postgresql" else sqlite_insert
        db.execute(
            inserir(VotoComentario)
            .values(
                comentario_versao_id=versao_id,
                usuario_id=usuario_id,
                voto=voto,
            )
            .on_conflict_do_update(
                index_elements=["comentario_versao_id", "usuario_id"],
                set_={"voto": voto},
            )
        )


def apagar_da_versao(db: Session, versao_id: UUID) -> None:
    db.execute(delete(VotoComentario).where(VotoComentario.comentario_versao_id == versao_id))
