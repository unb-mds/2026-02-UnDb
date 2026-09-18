from uuid import UUID, uuid4

from sqlalchemy import String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Unidade(Base):
    __tablename__ = "unidades"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    fonte: Mapped[str] = mapped_column(String(30), nullable=False, default="SIGAA")
    codigo: Mapped[str] = mapped_column(String(30), nullable=False)
    identificador_externo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)

    turmas = relationship("Turma", back_populates="unidade")

    __table_args__ = (
        UniqueConstraint("fonte", "codigo", name="uq_unidade_fonte_codigo"),
        UniqueConstraint(
            "fonte",
            "identificador_externo",
            name="uq_unidade_fonte_identificador_externo",
        ),
    )
