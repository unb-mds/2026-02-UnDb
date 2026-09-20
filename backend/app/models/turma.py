from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


turmas_professores = Table(
    "turmas_professores",
    Base.metadata,
    Column("turma_id", Uuid(as_uuid=True), ForeignKey("turmas.id"), primary_key=True),
    Column(
        "professor_id",
        Uuid(as_uuid=True),
        ForeignKey("professores.id"),
        primary_key=True,
    ),
)


class Turma(Base):
    __tablename__ = "turmas"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    disciplina_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("disciplinas.id"), nullable=False
    )
    unidade_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("unidades.id"), nullable=False
    )
    fonte: Mapped[str] = mapped_column(String(30), nullable=False, default="SIGAA")
    codigo: Mapped[str] = mapped_column(String(30), nullable=False)
    semestre: Mapped[str] = mapped_column(String(10), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ultima_observacao_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    disciplina = relationship("Disciplina", back_populates="turmas")
    unidade = relationship("Unidade", back_populates="turmas")
    professores = relationship(
        "Professor", secondary=turmas_professores, back_populates="turmas"
    )

    __table_args__ = (
        UniqueConstraint(
            "disciplina_id",
            "fonte",
            "unidade_id",
            "semestre",
            "codigo",
            name="uq_turma_identidade_sigaa",
        ),
    )
