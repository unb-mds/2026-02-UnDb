from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.unidade import Unidade


def get_by_fonte_codigo(db: Session, fonte: str, codigo: str) -> Unidade | None:
    return db.scalar(
        select(Unidade).where(Unidade.fonte == fonte, Unidade.codigo == codigo)
    )


def get_or_create(
    db: Session,
    fonte: str,
    codigo: str,
    nome: str,
    identificador_externo: str | None = None,
) -> Unidade:
    unidade = get_by_fonte_codigo(db, fonte, codigo)
    if unidade is None:
        unidade = Unidade(
            fonte=fonte,
            codigo=codigo,
            nome=nome,
            identificador_externo=identificador_externo,
        )
        db.add(unidade)
        db.flush()
    else:
        unidade.nome = nome
        if identificador_externo is not None:
            unidade.identificador_externo = identificador_externo
    return unidade
