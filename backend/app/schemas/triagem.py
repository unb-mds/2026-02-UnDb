from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import MotivoDenuncia


class CategoriaOpenAI(str, Enum):
    HARASSMENT = "harassment"
    HARASSMENT_THREATENING = "harassment/threatening"
    HATE = "hate"
    HATE_THREATENING = "hate/threatening"
    ILLICIT = "illicit"
    ILLICIT_VIOLENT = "illicit/violent"
    SELF_HARM = "self-harm"
    SELF_HARM_INTENT = "self-harm/intent"
    SELF_HARM_INSTRUCTIONS = "self-harm/instructions"
    SEXUAL = "sexual"
    SEXUAL_MINORS = "sexual/minors"
    VIOLENCE = "violence"
    VIOLENCE_GRAPHIC = "violence/graphic"


class ResultadoModeracaoOpenAI(BaseModel):
    model_config = ConfigDict(strict=True)
    flagged: bool
    categories: dict[CategoriaOpenAI, bool]

    @model_validator(mode="after")
    def categorias_completas(self):
        if set(self.categories) != set(CategoriaOpenAI):
            raise ValueError("categorias incompletas")
        return self


class RespostaModeracaoOpenAI(BaseModel):
    model_config = ConfigDict(strict=True)
    model: str = Field(pattern=r"^omni-moderation-[a-zA-Z0-9.-]+$", max_length=100)
    results: list[ResultadoModeracaoOpenAI] = Field(min_length=1, max_length=1)


class ClassificacaoIA(BaseModel):
    model_config = ConfigDict(extra="forbid")
    categorias: list[CategoriaOpenAI]
    sinalizado: bool
    modelo: str


class TriagemResponse(BaseModel):
    comentario_versao_id: UUID
    status: Literal["CONCLUIDA", "DESATIVADA", "DADOS_SENSIVEIS", "LIMITE", "INDISPONIVEL"]
    filtro_ativo: bool
    versao_lista: str
    categorias_locais: list[MotivoDenuncia]
    categorias_ia: list[CategoriaOpenAI] = Field(default_factory=list)
    sinalizado: bool | None = None
    modelo: str | None = None
    versao_integracao: str
