from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    SmallInteger,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import Dificuldade, QualidadeMaterial


class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    usuario_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
    professor_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("professores.id"), nullable=False
    )
    disciplina_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("disciplinas.id"), nullable=False
    )
    didatica: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dificuldade: Mapped[Dificuldade] = mapped_column(
        Enum(Dificuldade, name="dificuldade"), nullable=False
    )
    chamada: Mapped[bool] = mapped_column(Boolean, nullable=False)
    disponibiliza_material: Mapped[bool] = mapped_column(Boolean, nullable=False)
    qualidade_material: Mapped[QualidadeMaterial | None] = mapped_column(
        Enum(QualidadeMaterial, name="qualidade_material"), nullable=True
    )
    recomenda: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    usuario = relationship("Usuario", back_populates="avaliacoes")
    professor = relationship("Professor", back_populates="avaliacoes")
    disciplina = relationship("Disciplina", back_populates="avaliacoes")

    __table_args__ = (
        CheckConstraint("didatica BETWEEN 1 AND 5", name="ck_avaliacao_didatica"),
        CheckConstraint(
            "(disponibiliza_material AND qualidade_material IS NOT NULL) OR "
            "(NOT disponibiliza_material AND qualidade_material IS NULL)",
            name="ck_avaliacao_qualidade_material",
        ),
        UniqueConstraint(
            "usuario_id",
            "professor_id",
            "disciplina_id",
            name="uq_avaliacao_usuario_professor_disciplina",
        ),
    )
