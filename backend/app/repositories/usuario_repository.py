from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.token_confirmacao_email import TokenConfirmacaoEmail
from app.models.usuario import Usuario


def obter_por_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email))


def obter_token_por_hash(db: Session, token_hash: str) -> TokenConfirmacaoEmail | None:
    return db.scalar(
        select(TokenConfirmacaoEmail).where(
            TokenConfirmacaoEmail.token_hash == token_hash
        )
    )


def adicionar_usuario(db: Session, usuario: Usuario) -> None:
    db.add(usuario)


def adicionar_token(db: Session, token: TokenConfirmacaoEmail) -> None:
    db.add(token)
