from uuid import UUID, uuid4

from sqlalchemy import SmallInteger, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.unidade import Unidade


class Disciplina(Base):
    __tablename__ = "disciplinas"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    identificador_externo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    nome_normalizado: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    departamento: Mapped[str] = mapped_column(String(100), nullable=False)
    creditos: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    unidade_institucional: Mapped[Unidade | None] = relationship(
        primaryjoin=(
            "and_(foreign(Disciplina.departamento) == Unidade.codigo, Unidade.fonte == 'SIGAA')"
        ),
        viewonly=True,
        lazy="joined",
    )

    @property
    def departamento_nome(self) -> str | None:
        return self.unidade_institucional.nome if self.unidade_institucional else None

    turmas = relationship("Turma", back_populates="disciplina")
    avaliacoes = relationship("Avaliacao", back_populates="disciplina")
