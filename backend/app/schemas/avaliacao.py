from datetime import datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    StrictBool,
    model_validator,
)

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
    _comentario_erro: str | None = PrivateAttr(default=None)

    comentario: str | None = Field(
        default=None,
        description=(
            "Texto opcional do comentário (1 a 500 caracteres após "
            "desconsiderar espaços iniciais e finais)"
        ),
    )

    @property
    def comentario_erro(self) -> str | None:
        return self._comentario_erro

    @model_validator(mode="after")
    def normalizar_comentario(self) -> Self:
        if self.comentario is not None:
            texto = self.comentario.strip()
            if not 1 <= len(texto) <= 500:
                self._comentario_erro = "comentario deve conter entre 1 e 500 caracteres"
                self.comentario = None
            else:
                self._comentario_erro = None
                self.comentario = texto
        return self


class AvaliacaoResponse(AvaliacaoBase):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    comentario_erro: str | None = Field(
        default=None,
        description="Motivo do descarte de um comentario invalido; os criterios foram salvos",
    )


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
