from dataclasses import dataclass
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from functools import lru_cache
import secrets
from urllib.parse import urlencode

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import config
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
from app.models.token_recuperacao_senha import TokenRecuperacaoSenha
from app.repositories import recuperacao_senha_repository
from app.repositories import sessao_repository, usuario_repository
from app.schemas.auth import CadastroRequest, LoginRequest
from app.services.email_service import EmailDeliveryError, EmailSender


CADASTRO_MESSAGE = "Se o endereço informado estiver disponível, enviaremos um link de confirmação."
CONFIRMACAO_MESSAGE = "E-mail confirmado. Sua conta já pode registrar avaliações."
TOKEN_INVALIDO_MESSAGE = "Link de confirmação inválido ou expirado."
LOGIN_MESSAGE = "Autenticação realizada com sucesso."
LOGOUT_MESSAGE = "Sessão encerrada com sucesso."
SESSION_INVALIDA_MESSAGE = "Sessão ausente, inválida ou expirada."
EMAIL_NAO_CONFIRMADO_MESSAGE = "Confirme seu e-mail antes de registrar avaliações."
TOKEN_TTL = timedelta(hours=config.AUTH_CONFIRMACAO_TTL_HORAS)
SESSION_TTL = timedelta(days=config.AUTH_SESSAO_TTL_DIAS)


class TokenConfirmacaoInvalidoError(Exception):
    pass


class CredenciaisInvalidasError(Exception):
    pass


class SessaoInvalidaError(Exception):
    pass


RECUPERACAO_MESSAGE = (
    "Se o endereço informado possuir uma conta, enviaremos um link para redefinir a senha."
)
REDEFINICAO_MESSAGE = "Senha redefinida. Entre novamente com sua nova senha."
RECUPERACAO_TOKEN_INVALIDO_MESSAGE = (
    "Link de recuperação inválido ou expirado. Solicite um novo link."
)
RECUPERACAO_TTL = timedelta(minutes=config.AUTH_RECUPERACAO_TTL_MINUTOS)
REENVIO_MESSAGE = (
    "Se o endereço informado possuir uma conta pendente, enviaremos um link de confirmação."
)


class TokenRecuperacaoInvalidoError(Exception):
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

    parametros = {"token": token_aberto}
    if dados.return_to:
        parametros["returnTo"] = dados.return_to
    link = f"{FRONTEND_URL.rstrip('/')}/confirmar-email?{urlencode(parametros)}"
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
    token = usuario_repository.obter_token_por_hash(db, gerar_hash_token(token_aberto))
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


@lru_cache(maxsize=1)
def _hash_ficticio_login() -> str:
    return gerar_hash_senha(secrets.token_urlsafe(32))


def autenticar(
    db: Session,
    dados: LoginRequest,
    *,
    antes_de_criar_sessao: Callable[[], None] | None = None,
) -> Autenticacao:
    ficticio = _hash_ficticio_login()
    usuario = usuario_repository.obter_para_login(db, dados.email)
    credencial_valida = verificar_senha(dados.senha, usuario.password_hash if usuario else ficticio)
    if usuario is None or not credencial_valida:
        raise CredenciaisInvalidasError("E-mail ou senha inválidos.")

    if antes_de_criar_sessao:
        antes_de_criar_sessao()

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

    sessao = sessao_repository.obter_por_token_hash(db, gerar_hash_token(token_aberto))
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


def solicitar_recuperacao_senha(db: Session, email: str, email_sender: EmailSender) -> str:
    usuario = usuario_repository.obter_por_email(db, email)
    if usuario is None:
        return RECUPERACAO_MESSAGE

    token_aberto = gerar_token_confirmacao()
    token = TokenRecuperacaoSenha(
        usuario_id=usuario.id,
        token_hash=gerar_hash_token(token_aberto),
        expires_at=_agora_utc() + RECUPERACAO_TTL,
    )
    recuperacao_senha_repository.adicionar(db, token)
    link = f"{FRONTEND_URL.rstrip('/')}/redefinir-senha?{urlencode({'token': token_aberto})}"
    try:
        db.flush()
        email_sender.enviar_recuperacao_senha(email, link)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return RECUPERACAO_MESSAGE


def redefinir_senha(
    db: Session,
    token_aberto: str,
    senha: str,
    *,
    antes_de_confirmar: Callable[[Usuario], None] | None = None,
) -> str:
    token_hash = gerar_hash_token(token_aberto)
    try:
        usuario = recuperacao_senha_repository.obter_usuario_por_token(db, token_hash)
        token = recuperacao_senha_repository.obter_token(db, token_hash)
        agora = _agora_utc()
        if (
            usuario is None
            or token is None
            or token.used_at is not None
            or _como_utc(token.expires_at) <= agora
        ):
            raise TokenRecuperacaoInvalidoError(RECUPERACAO_TOKEN_INVALIDO_MESSAGE)
        usuario.password_hash = gerar_hash_senha(senha)
        recuperacao_senha_repository.invalidar_links_e_sessoes(db, usuario, agora)
        if antes_de_confirmar:
            antes_de_confirmar(usuario)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return REDEFINICAO_MESSAGE


def reenviar_confirmacao(
    db: Session, email: str, email_sender: EmailSender, return_to: str | None = None
) -> str:
    try:
        usuario = usuario_repository.obter_para_login(db, email)
        if usuario is None or usuario.email_confirmado:
            return REENVIO_MESSAGE
        token_aberto = gerar_token_confirmacao()
        usuario_repository.adicionar_token(
            db,
            TokenConfirmacaoEmail(
                usuario_id=usuario.id,
                token_hash=gerar_hash_token(token_aberto),
                expires_at=_agora_utc() + TOKEN_TTL,
            ),
        )
        parametros = {"token": token_aberto}
        if return_to:
            parametros["returnTo"] = return_to
        link = f"{FRONTEND_URL.rstrip('/')}/confirmar-email?{urlencode(parametros)}"
        db.flush()
        email_sender.enviar_confirmacao(email, link)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return REENVIO_MESSAGE
