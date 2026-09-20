import hashlib
import secrets

from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def gerar_hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def gerar_token_confirmacao() -> str:
    return secrets.token_urlsafe(32)


def gerar_hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
