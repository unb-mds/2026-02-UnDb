from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import Dificuldade, QualidadeMaterial


class AvaliacaoBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    professor_id: UUID
    disciplina_id: UUID
    didatica: int = Field(ge=1, le=5)
    dificuldade: Dificuldade
    chamada: bool
    disponibiliza_material: bool
    qualidade_material: QualidadeMaterial | None = None
    recomenda: bool

    @model_validator(mode="after")
    def validar_qualidade_material(self) -> Self:
        if self.disponibiliza_material != (self.qualidade_material is not None):
            raise ValueError(
                "qualidade_material deve ser informada somente quando "
                "disponibiliza_material for verdadeiro"
            )
        return self


class AvaliacaoCreate(AvaliacaoBase):
    pass


class AvaliacaoRead(AvaliacaoBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    created_at: datetime
    updated_at: datetime
