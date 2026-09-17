from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator

from app.models.enums import Dificuldade, QualidadeMaterial


class AvaliacaoBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    professor_id: UUID = Field(description="Professor avaliado")
    disciplina_id: UUID = Field(description="Disciplina avaliada")
    didatica: int = Field(
        strict=True,
        ge=1,
        le=5,
        description="Nota inteira de didatica, de 1 a 5",
    )
    dificuldade: Dificuldade = Field(
        description="Dificuldade percebida: FACIL, MEDIO ou DIFICIL"
    )
    chamada: StrictBool = Field(description="Se o professor realiza chamada")
    disponibiliza_material: StrictBool = Field(
        description="Se o professor disponibiliza material"
    )
    qualidade_material: QualidadeMaterial | None = Field(
        default=None,
        description=(
            "Qualidade do material: RUIM, MEDIO ou BOM; nulo quando nao ha material"
        ),
    )
    recomenda: StrictBool = Field(description="Se o estudante recomenda a materia")

    @model_validator(mode="after")
    def validar_qualidade_material(self) -> Self:
        if self.disponibiliza_material != (self.qualidade_material is not None):
            raise ValueError(
                "qualidade_material e obrigatoria quando disponibiliza_material for "
                "verdadeiro e deve ser nula quando for falso"
            )
        return self


class AvaliacaoCreate(AvaliacaoBase):
    pass
