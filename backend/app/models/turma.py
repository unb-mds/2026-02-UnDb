from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Turma(Base):
    __tablename__ = "turmas"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    disciplina_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("disciplinas.id"), nullable=False
    )
    professor_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("professores.id"), nullable=False
    )
    semestre: Mapped[str] = mapped_column(String(10), nullable=False)

    disciplina = relationship("Disciplina", back_populates="turmas")
    professor = relationship("Professor", back_populates="turmas")

    __table_args__ = (
        UniqueConstraint(
            "disciplina_id",
            "professor_id",
            "semestre",
            name="uq_turma_disciplina_professor_semestre",
        ),
    )
