from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, JSON, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ImportacaoExecucao(Base):
    __tablename__ = "importacao_execucoes"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    iniciada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    finalizada_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    ano: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
    )

    periodo: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    departamentos: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    ofertas_extraidas: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    ofertas_processadas: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    erro: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    resultado_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
