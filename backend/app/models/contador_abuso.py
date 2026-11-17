"""Estado descartável do limitador; persistência UNLOGGED definida pela migration."""

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ContadorAbuso(Base):
    __tablename__ = "contadores_abuso"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_contador_abuso_quantidade"),
        CheckConstraint("length(chave) = 64", name="ck_contador_abuso_chave"),
        CheckConstraint("expira_em > inicio_em", name="ck_contador_abuso_janela"),
        Index("ix_contadores_abuso_expira_em", "expira_em"),
        # SQLite só materializa o mapping nos testes existentes. Não é backend do limitador.
        {"info": {"unlogged": True}},
    )

    operacao: Mapped[str] = mapped_column(String(64), primary_key=True)
    chave: Mapped[str] = mapped_column(String(64), primary_key=True)
    quantidade: Mapped[int] = mapped_column(BigInteger, nullable=False)
    inicio_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    proxima_tentativa_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
