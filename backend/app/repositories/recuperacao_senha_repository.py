from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.models.sessao_usuario import SessaoUsuario
from app.models.token_recuperacao_senha import TokenRecuperacaoSenha
from app.models.usuario import Usuario


def obter_usuario_por_token(db: Session, token_hash: str) -> Usuario | None:
    # Serializa trocas concorrentes, inclusive com links diferentes da mesma conta.
    return db.scalar(
        select(Usuario)
        .where(
            Usuario.id.in_(
                select(TokenRecuperacaoSenha.usuario_id).where(
                    TokenRecuperacaoSenha.token_hash == token_hash
                )
            )
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )


def obter_token(db: Session, token_hash: str) -> TokenRecuperacaoSenha | None:
    return db.scalar(
        select(TokenRecuperacaoSenha)
        .where(TokenRecuperacaoSenha.token_hash == token_hash)
        .execution_options(populate_existing=True)
    )


def adicionar(db: Session, token: TokenRecuperacaoSenha) -> None:
    db.add(token)


def invalidar_links_e_sessoes(db: Session, usuario: Usuario, agora: datetime) -> None:
    db.execute(
        update(TokenRecuperacaoSenha)
        .where(
            TokenRecuperacaoSenha.usuario_id == usuario.id,
            TokenRecuperacaoSenha.used_at.is_(None),
        )
        .values(used_at=agora)
    )
    db.execute(delete(SessaoUsuario).where(SessaoUsuario.usuario_id == usuario.id))
