from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email_confirmado: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    avaliacoes = relationship("Avaliacao", back_populates="usuario")
    tokens_confirmacao_email = relationship(
        "TokenConfirmacaoEmail", back_populates="usuario"
    )
