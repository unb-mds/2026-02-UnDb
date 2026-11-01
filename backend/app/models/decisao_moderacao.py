from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DecisaoModeracao(Base):
    __tablename__ = "decisoes_moderacao"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    comentario_versao_id: Mapped[UUID] = mapped_column(
        ForeignKey("comentario_versoes.id"), nullable=False, index=True
    )
    moderador_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    acao: Mapped[str] = mapped_column(String(20), nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    estado_anterior: Mapped[str] = mapped_column(String(20), nullable=False)
    estado_posterior: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    descartar_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
