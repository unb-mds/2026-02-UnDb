from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import FRONTEND_URL
from app.core.security import (
    gerar_hash_senha,
    gerar_hash_token,
    gerar_token_confirmacao,
    verificar_senha,
)
from app.models.sessao_usuario import SessaoUsuario
from app.models.token_confirmacao_email import TokenConfirmacaoEmail
from app.models.usuario import Usuario
from app.repositories import sessao_repository, usuario_repository
from app.schemas.auth import CadastroRequest, LoginRequest
from app.services.email_service import EmailDeliveryError, EmailSender


CADASTRO_MESSAGE = (
    "Se o endereço informado estiver disponível, enviaremos um link de confirmação."
)
CONFIRMACAO_MESSAGE = "E-mail confirmado. Sua conta já pode registrar avaliações."
TOKEN_INVALIDO_MESSAGE = "Link de confirmação inválido ou expirado."
LOGIN_MESSAGE = "Autenticação realizada com sucesso."
LOGOUT_MESSAGE = "Sessão encerrada com sucesso."
SESSION_INVALIDA_MESSAGE = "Sessão ausente, inválida ou expirada."
EMAIL_NAO_CONFIRMADO_MESSAGE = "Confirme seu e-mail antes de registrar avaliações."
TOKEN_TTL = timedelta(hours=24)
SESSION_TTL = timedelta(days=7)


class TokenConfirmacaoInvalidoError(Exception):
    pass


class CredenciaisInvalidasError(Exception):
    pass


class SessaoInvalidaError(Exception):
    pass


@dataclass(frozen=True)
class Autenticacao:
    usuario: Usuario
    token: str


def _agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def _como_utc(valor: datetime) -> datetime:
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


def cadastrar(
    db: Session,
    dados: CadastroRequest,
    email_sender: EmailSender,
) -> str:
    if usuario_repository.obter_por_email(db, dados.email) is not None:
        return CADASTRO_MESSAGE

    token_aberto = gerar_token_confirmacao()
    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        password_hash=gerar_hash_senha(dados.senha),
        email_confirmado=False,
    )
    token = TokenConfirmacaoEmail(
        usuario=usuario,
        token_hash=gerar_hash_token(token_aberto),
        expires_at=_agora_utc() + TOKEN_TTL,
    )
    usuario_repository.adicionar_usuario(db, usuario)
    usuario_repository.adicionar_token(db, token)

    parametros = urlencode({"token": token_aberto})
    link = f"{FRONTEND_URL.rstrip('/')}/confirmar-email?{parametros}"
    try:
        db.flush()
        email_sender.enviar_confirmacao(dados.email, link)
        db.commit()
    except IntegrityError:
        db.rollback()
        return CADASTRO_MESSAGE
    except EmailDeliveryError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

    return CADASTRO_MESSAGE


def confirmar_email(db: Session, token_aberto: str) -> str:
    token = usuario_repository.obter_token_por_hash(
        db, gerar_hash_token(token_aberto)
    )
    if token is None:
        raise TokenConfirmacaoInvalidoError(TOKEN_INVALIDO_MESSAGE)

    if token.used_at is not None:
        raise TokenConfirmacaoInvalidoError(TOKEN_INVALIDO_MESSAGE)

    if _como_utc(token.expires_at) <= _agora_utc():
        raise TokenConfirmacaoInvalidoError(TOKEN_INVALIDO_MESSAGE)

    token.usuario.email_confirmado = True
    token.used_at = _agora_utc()
    db.commit()
    return CONFIRMACAO_MESSAGE


def autenticar(db: Session, dados: LoginRequest) -> Autenticacao:
    usuario = usuario_repository.obter_por_email(db, dados.email)
    if usuario is None or not verificar_senha(dados.senha, usuario.password_hash):
        raise CredenciaisInvalidasError("E-mail ou senha inválidos.")

    token_aberto = gerar_token_confirmacao()
    sessao = SessaoUsuario(
        usuario=usuario,
        token_hash=gerar_hash_token(token_aberto),
        expires_at=_agora_utc() + SESSION_TTL,
    )
    sessao_repository.adicionar(db, sessao)
    db.commit()
    return Autenticacao(usuario=usuario, token=token_aberto)


def validar_e_renovar_sessao(db: Session, token_aberto: str | None) -> SessaoUsuario:
    if not token_aberto:
        raise SessaoInvalidaError(SESSION_INVALIDA_MESSAGE)

    sessao = sessao_repository.obter_por_token_hash(
        db, gerar_hash_token(token_aberto)
    )
    if sessao is None:
        raise SessaoInvalidaError(SESSION_INVALIDA_MESSAGE)

    agora = _agora_utc()
    if _como_utc(sessao.expires_at) <= agora:
        sessao_repository.remover(db, sessao)
        db.commit()
        raise SessaoInvalidaError(SESSION_INVALIDA_MESSAGE)

    sessao.expires_at = agora + SESSION_TTL
    db.commit()
    return sessao


def encerrar_sessao(db: Session, sessao: SessaoUsuario) -> str:
    sessao_repository.remover(db, sessao)
    db.commit()
    return LOGOUT_MESSAGE
