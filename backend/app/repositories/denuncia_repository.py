from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.denuncia import Agradecimento, Denuncia
from app.models.enums import MotivoDenuncia

MotivoEncerramento = Literal[
    "MANTIDO", "RESTAURADO", "REMOVIDO", "CONTEUDO_RETIRADO", "VERSAO_SUBSTITUIDA"
]


def existe_da_conta(db: Session, versao_id: UUID, usuario_id: UUID) -> bool:
    return (
        db.scalar(
            select(Denuncia.id)
            .where(
                Denuncia.comentario_versao_id == versao_id, Denuncia.denunciante_id == usuario_id
            )
            .limit(1)
        )
        is not None
    )


def criar(
    db: Session, versao_id: UUID, usuario_id: UUID | None, motivo: MotivoDenuncia, agora: datetime
) -> Denuncia:
    denuncia = Denuncia(
        comentario_versao_id=versao_id, denunciante_id=usuario_id, motivo=motivo, created_at=agora
    )
    db.add(denuncia)
    db.flush()
    return denuncia


def listar(db: Session, versao_id: UUID) -> list[Denuncia]:
    return list(
        db.scalars(
            select(Denuncia)
            .where(Denuncia.comentario_versao_id == versao_id)
            .order_by(Denuncia.created_at, Denuncia.id)
        )
    )


def contar_contas(db: Session, versao_id: UUID) -> int:
    return (
        db.scalar(
            select(func.count(func.distinct(Denuncia.denunciante_id))).where(
                Denuncia.comentario_versao_id == versao_id
            )
        )
        or 0
    )


def encerrar(db: Session, versao_id: UUID, motivo: MotivoEncerramento) -> None:
    if motivo not in (
        "MANTIDO",
        "RESTAURADO",
        "REMOVIDO",
        "CONTEUDO_RETIRADO",
        "VERSAO_SUBSTITUIDA",
    ):
        raise ValueError("motivo de encerramento invalido")
    db.execute(delete(Denuncia).where(Denuncia.comentario_versao_id == versao_id))


def agradecer(db: Session, versao_id: UUID, evento: str, agora: datetime) -> None:
    contas = db.scalars(
        select(Denuncia.denunciante_id)
        .where(
            Denuncia.comentario_versao_id == versao_id,
            Denuncia.denunciante_id.is_not(None),
        )
        .distinct()
    )
    db.add_all(
        Agradecimento(
            usuario_id=conta, comentario_versao_id=versao_id, evento=evento, created_at=agora
        )
        for conta in contas
    )
    db.flush()


def listar_agradecimentos(db: Session, usuario_id: UUID) -> list[Agradecimento]:
    return list(
        db.scalars(
            select(Agradecimento)
            .where(Agradecimento.usuario_id == usuario_id)
            .order_by(Agradecimento.created_at, Agradecimento.id)
        )
    )


def apagar_agradecimento(db: Session, usuario_id: UUID, mensagem_id: UUID) -> bool:
    resultado = db.execute(
        delete(Agradecimento).where(
            Agradecimento.id == mensagem_id, Agradecimento.usuario_id == usuario_id
        )
    )
    return resultado.rowcount == 1
