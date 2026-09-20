from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.unidade import Unidade


def get_by_fonte_codigo(db: Session, fonte: str, codigo: str) -> Unidade | None:
    return db.scalar(
        select(Unidade).where(Unidade.fonte == fonte, Unidade.codigo == codigo)
    )


def get_by_fonte_identificador_externo(
    db: Session, fonte: str, identificador_externo: str
) -> Unidade | None:
    return db.scalar(
        select(Unidade).where(
            Unidade.fonte == fonte,
            Unidade.identificador_externo == identificador_externo,
        )
    )


def get_or_create(
    db: Session,
    fonte: str,
    codigo: str,
    nome: str,
    identificador_externo: str | None = None,
) -> Unidade:
    unidade = get_by_fonte_codigo(db, fonte, codigo)
    unidade_por_identificador = (
        get_by_fonte_identificador_externo(db, fonte, identificador_externo)
        if identificador_externo is not None
        else None
    )

    if unidade_por_identificador is not None and unidade_por_identificador is not unidade:
        raise ValueError(
            "identificador externo da unidade ja pertence a outro codigo: "
            f"fonte={fonte!r}, identificador={identificador_externo!r}, "
            f"persistido={unidade_por_identificador.codigo!r}, recebido={codigo!r}"
        )

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
        if (
            unidade.identificador_externo is not None
            and identificador_externo is not None
            and unidade.identificador_externo != identificador_externo
        ):
            raise ValueError(
                "conflito de identidade da unidade: "
                f"fonte={fonte!r}, codigo={codigo!r}, "
                f"persistido={unidade.identificador_externo!r}, "
                f"recebido={identificador_externo!r}"
            )
        unidade.nome = nome
        if identificador_externo is not None:
            unidade.identificador_externo = identificador_externo
    return unidade
