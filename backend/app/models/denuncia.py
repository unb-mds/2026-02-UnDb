from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import MotivoDenuncia


class Denuncia(Base):
    """Only open reports exist; closure deletes the row (R2-DEC-14)."""

    __tablename__ = "denuncias"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    comentario_versao_id: Mapped[UUID] = mapped_column(
        ForeignKey("comentario_versoes.id"), nullable=False
    )
    denunciante_id: Mapped[UUID | None] = mapped_column(ForeignKey("usuarios.id"))
    motivo: Mapped[MotivoDenuncia] = mapped_column(
        Enum(MotivoDenuncia, name="motivo_denuncia", native_enum=False, create_constraint=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    denunciante = relationship("Usuario")
    __table_args__ = (
        UniqueConstraint("comentario_versao_id", "denunciante_id", name="uq_denuncia_conta_versao"),
    )


class Agradecimento(Base):
    __tablename__ = "agradecimentos"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    comentario_versao_id: Mapped[UUID] = mapped_column(
        ForeignKey("comentario_versoes.id"), nullable=False
    )
    evento: Mapped[str] = mapped_column(
        Enum(
            "SUSPENSAO",
            "REMOCAO",
            name="evento_agradecimento",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
