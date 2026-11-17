from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint(
            "(termos_versao IS NULL AND termos_ciencia_em IS NULL) OR "
            "(termos_versao IS NOT NULL AND termos_versao <> '' AND termos_ciencia_em IS NOT NULL)",
            name="ck_usuario_ciencia_termos_completa",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_confirmado: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    moderador: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    reconciliador: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    excluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def estado(self):
        return "EXCLUIDA" if self.excluido_em else "ATIVA"

    termos_versao: Mapped[str | None] = mapped_column(String(32), nullable=True)
    termos_ciencia_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    avaliacoes = relationship("Avaliacao", back_populates="usuario")
    tokens_confirmacao_email = relationship("TokenConfirmacaoEmail", back_populates="usuario")
    sessoes = relationship("SessaoUsuario", back_populates="usuario")
