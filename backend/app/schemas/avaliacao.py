from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator

from app.models.enums import Dificuldade, QualidadeMaterial
from app.schemas.institucional import (
    DisciplinaInstitucionalResponse,
    ProfessorInstitucionalResponse,
)


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


class AvaliacaoAgregadaBaseResponse(BaseModel):
    professor_id: UUID
    disciplina_id: UUID
    professor: ProfessorInstitucionalResponse
    disciplina: DisciplinaInstitucionalResponse
    total_avaliacoes: int = Field(ge=0)


class AvaliacaoAgregadaInsuficienteResponse(AvaliacaoAgregadaBaseResponse):
    dados_suficientes: Literal[False]


class AvaliacaoAgregadaSuficienteResponse(AvaliacaoAgregadaBaseResponse):
    dados_suficientes: Literal[True]
    didatica: float
    dificuldade: Dificuldade
    chamada: bool | Literal["CONFLITANTE"]
    disponibiliza_material: bool | Literal["CONFLITANTE"]
    qualidade_material: QualidadeMaterial | None
    recomenda: int = Field(ge=0, le=100)


AvaliacaoAgregadaResponse = (
    AvaliacaoAgregadaSuficienteResponse | AvaliacaoAgregadaInsuficienteResponse
)


class ComparacaoProfessoresResponse(BaseModel):
    disciplina: DisciplinaInstitucionalResponse
    professores: list[AvaliacaoAgregadaResponse]
