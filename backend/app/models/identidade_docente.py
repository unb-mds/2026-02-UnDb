from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class IdentidadeDocente(Base):
    __tablename__ = "identidades_docentes"
    identificador: Mapped[str] = mapped_column(String(30), primary_key=True)
    professor_id: Mapped[UUID] = mapped_column(
        ForeignKey("professores.id"), unique=True, nullable=False
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)


class PendenciaIdentidade(Base):
    __tablename__ = "pendencias_identidade"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('PENDENTE','CONFIRMADA','SEPARADA','APLICADA')",
            name="ck_pendencia_identidade_estado",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    chave: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    professor_id: Mapped[UUID] = mapped_column(ForeignKey("professores.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    unidade: Mapped[str] = mapped_column(String(100), nullable=False)
    periodo: Mapped[str] = mapped_column(String(10), nullable=False)
    disciplina: Mapped[str] = mapped_column(String(30), nullable=False)
    turma: Mapped[str] = mapped_column(String(30), nullable=False)
    motivo: Mapped[str] = mapped_column(String(80), nullable=False)
    candidatos: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    estado: Mapped[str] = mapped_column(String(15), nullable=False, default="PENDENTE")
    identificador_destino: Mapped[str | None] = mapped_column(String(30))
    versao: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    humana: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class DecisaoIdentidade(Base):
    __tablename__ = "decisoes_identidade"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    pendencia_id: Mapped[UUID] = mapped_column(
        ForeignKey("pendencias_identidade.id"), index=True, nullable=False
    )
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    acao: Mapped[str] = mapped_column(String(15), nullable=False)
    justificativa: Mapped[str] = mapped_column(String(500), nullable=False)
    identificador: Mapped[str | None] = mapped_column(String(30))
    versao: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
