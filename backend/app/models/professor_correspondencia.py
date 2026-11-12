from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProfessorCorrespondencia(Base):
    """Correspondência operacional explícita; mantém o registro e a origem antigos."""

    __tablename__ = "professor_correspondencias"

    origem_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("professores.id"), primary_key=True
    )
    destino_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("professores.id"), nullable=False, index=True
    )
    evidencia: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint("origem_id <> destino_id", name="ck_correspondencia_distinta"),
        CheckConstraint("length(trim(evidencia)) > 0", name="ck_correspondencia_evidencia"),
    )
