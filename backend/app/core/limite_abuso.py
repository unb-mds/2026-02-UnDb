"""Conexão isolada e derivação de chaves do limitador. Não inspeciona IP/cookies."""

import hashlib
import hmac
from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core import config
from app.domain.email import normalizar_email


class TipoIdentidade(StrEnum):
    EMAIL = "email"
    CONTA = "conta"
    TOKEN = "token"


@dataclass(frozen=True)
class IdentidadeAbuso:
    tipo: TipoIdentidade
    valor: str = field(repr=False)

    def __post_init__(self):
        object.__setattr__(self, "tipo", TipoIdentidade(self.tipo))
        if self.tipo == TipoIdentidade.EMAIL:
            object.__setattr__(self, "valor", normalizar_email(self.valor))
        elif self.tipo == TipoIdentidade.TOKEN:
            object.__setattr__(self, "valor", hashlib.sha256(self.valor.encode()).hexdigest())
        elif self.tipo == TipoIdentidade.CONTA:
            object.__setattr__(self, "valor", str(UUID(self.valor)))


def derivar_chave(segredo: str, operacao: str, identidade: IdentidadeAbuso | None) -> str:
    if not segredo:
        raise ValueError("Segredo específico do limitador não configurado.")
    partes = (
        ["abuso-v1", operacao, "global"]
        if identidade is None
        else ["abuso-v1", operacao, "identidade", identidade.tipo.value, identidade.valor]
    )
    mensagem = b"".join(len(p.encode()).to_bytes(4, "big") + p.encode() for p in partes)
    return hmac.new(segredo.encode(), mensagem, hashlib.sha256).hexdigest()


@lru_cache(maxsize=1)
def engine_limitador():
    if make_url(config.DATABASE_URL).drivername != "postgresql+psycopg2":
        raise ValueError("O limitador exige PostgreSQL e psycopg2.")
    valores = (
        config.ABUSO_STATEMENT_TIMEOUT_MS,
        config.ABUSO_LOCK_TIMEOUT_MS,
        config.ABUSO_CONNECT_TIMEOUT_SEGUNDOS,
        config.ABUSO_POOL_TIMEOUT_SEGUNDOS,
        config.ABUSO_POOL_TAMANHO,
    )
    if any(valor <= 0 for valor in valores):
        raise ValueError("Timeouts e pool devem ser positivos.")
    return create_engine(
        config.DATABASE_URL,
        hide_parameters=True,
        pool_size=config.ABUSO_POOL_TAMANHO,
        max_overflow=0,
        pool_timeout=config.ABUSO_POOL_TIMEOUT_SEGUNDOS,
        # Sem ping antes dos timeouts; a operação classifica conexão obsoleta como falha.
        connect_args={
            "connect_timeout": config.ABUSO_CONNECT_TIMEOUT_SEGUNDOS,
            "options": (
                f"-c statement_timeout={config.ABUSO_STATEMENT_TIMEOUT_MS} "
                f"-c lock_timeout={config.ABUSO_LOCK_TIMEOUT_MS}"
            ),
        },
    )


def sessao_limitador() -> Session:
    return Session(engine_limitador(), autoflush=False, expire_on_commit=False)
