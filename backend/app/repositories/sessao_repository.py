from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sessao_usuario import SessaoUsuario


def obter_por_token_hash(db: Session, token_hash: str) -> SessaoUsuario | None:
    return db.scalar(
        select(SessaoUsuario).where(SessaoUsuario.token_hash == token_hash)
    )


def adicionar(db: Session, sessao: SessaoUsuario) -> None:
    db.add(sessao)


def remover(db: Session, sessao: SessaoUsuario) -> None:
    db.delete(sessao)
