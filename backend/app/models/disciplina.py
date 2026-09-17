from uuid import UUID, uuid4

from sqlalchemy import SmallInteger, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Disciplina(Base):
    __tablename__ = "disciplinas"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    identificador_externo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    nome_normalizado: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    departamento: Mapped[str] = mapped_column(String(100), nullable=False)
    creditos: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    turmas = relationship("Turma", back_populates="disciplina")
    avaliacoes = relationship("Avaliacao", back_populates="disciplina")
