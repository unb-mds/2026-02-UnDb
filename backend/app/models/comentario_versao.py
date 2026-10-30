from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EstadoComentario


class ComentarioVersao(Base):
    __tablename__ = "comentario_versoes"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    avaliacao_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("avaliacoes.id"), nullable=False
    )
    substitui_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("comentario_versoes.id"), nullable=True
    )
    texto: Mapped[str] = mapped_column(String(500), nullable=False)
    estado: Mapped[EstadoComentario] = mapped_column(
        Enum(EstadoComentario, name="estado_comentario"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    avaliacao = relationship("Avaliacao", back_populates="comentarios")
    substitui = relationship("ComentarioVersao", remote_side=[id])

    __table_args__ = (
        CheckConstraint(
            "length(texto) BETWEEN 1 AND 500", name="ck_comentario_versao_tamanho"
        ),
    )
