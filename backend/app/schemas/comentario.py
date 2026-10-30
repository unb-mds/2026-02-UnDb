from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import EstadoComentario


class ComentarioCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texto: str = Field(description="Texto do comentário, entre 1 e 500 caracteres")

    @field_validator("texto")
    @classmethod
    def normalizar_texto(cls, valor: str) -> str:
        texto = valor.strip()
        if not 1 <= len(texto) <= 500:
            raise ValueError("comentario deve conter entre 1 e 500 caracteres")
        return texto


class ComentarioPublicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    texto: str
    created_at: datetime


class ComentarioDoAutorResponse(ComentarioPublicoResponse):
    estado: EstadoComentario
    avaliacao_id: UUID
    substitui_id: UUID | None
    updated_at: datetime
