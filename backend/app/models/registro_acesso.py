from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class RegistroAcesso(Base):
    __tablename__ = "registros_acesso"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    ocorrido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    operacao: Mapped[str] = mapped_column(String(80), nullable=False)
    usuario_id: Mapped[UUID | None] = mapped_column(Uuid)
    ip_conexao: Mapped[str | None] = mapped_column(Text)
    encaminhado_nao_confiavel: Mapped[str | None] = mapped_column(Text)
    resultado: Mapped[str] = mapped_column(String(10), nullable=False)
    requisicao_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
