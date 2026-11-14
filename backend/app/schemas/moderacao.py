from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import AcaoModeracao, EstadoComentario


class AcaoModeracaoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    acao: AcaoModeracao
    motivo: str

    @field_validator("motivo")
    @classmethod
    def motivo_obrigatorio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("motivo obrigatorio")
        return valor.strip()


class IdentidadeInterna(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    email: str


class ComentarioModeracaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    texto: str | None
    estado: EstadoComentario
    autor: IdentidadeInterna
    substitui_id: UUID | None
    created_at: datetime


class DecisaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    comentario_versao_id: UUID
    moderador_id: UUID | None
    acao: AcaoModeracao
    motivo: str
    estado_anterior: EstadoComentario
    estado_posterior: EstadoComentario
    created_at: datetime
