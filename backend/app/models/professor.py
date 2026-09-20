from uuid import UUID, uuid4

from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Professor(Base):
    __tablename__ = "professores"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    nome_normalizado: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    departamento: Mapped[str] = mapped_column(String(100), nullable=False)
    siape: Mapped[str | None] = mapped_column(String(30), nullable=True, unique=True)
    identidade_origem: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True
    )
    identidade_confirmada: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    turmas = relationship(
        "Turma", secondary="turmas_professores", back_populates="professores"
    )
    avaliacoes = relationship("Avaliacao", back_populates="professor")
