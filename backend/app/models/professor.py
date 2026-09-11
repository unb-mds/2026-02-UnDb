from uuid import UUID, uuid4

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Professor(Base):
    __tablename__ = "professores"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    departamento: Mapped[str] = mapped_column(String(100), nullable=False)

    turmas = relationship("Turma", back_populates="professor")
    avaliacoes = relationship("Avaliacao", back_populates="professor")
