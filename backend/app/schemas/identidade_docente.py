from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CandidatoResponse(BaseModel):
    identificador: str
    nome: str
    perfil_url: str
    compativel: bool


class PendenciaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    professor_id: UUID
    nome: str
    unidade: str
    periodo: str
    disciplina: str
    turma: str
    motivo: str
    candidatos: list[CandidatoResponse]
    estado: Literal["PENDENTE", "CONFIRMADA", "SEPARADA", "APLICADA"]
    identificador_destino: str | None
    versao: int
    humana: bool
    created_at: datetime


class DecidirRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    acao: Literal["CONFIRMAR", "SEPARAR"]
    versao: int = Field(ge=1)
    identificador: str | None = Field(default=None, pattern=r"^\d{1,30}$")
    justificativa: str = Field(min_length=1, max_length=500)

    @field_validator("justificativa")
    @classmethod
    def justificar(cls, valor):
        if not valor.strip():
            raise ValueError("Justificativa obrigatória.")
        return valor.strip()


class DecisaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    usuario_id: UUID
    acao: str
    justificativa: str
    identificador: str | None
    versao: int
    created_at: datetime


class PreviaResponse(BaseModel):
    colisoes: int
    uniao_necessaria: bool
    bloqueada: bool
    turmas: int | None = None
    avaliacoes: int | None = None
