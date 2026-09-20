from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProfessorInstitucionalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    departamento: str


class DisciplinaInstitucionalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    codigo: str
    nome: str
    departamento: str


class ProfessorDetalheResponse(ProfessorInstitucionalResponse):
    siape: str | None
    identidade_confirmada: bool


class DisciplinaDetalheResponse(DisciplinaInstitucionalResponse):
    identificador_externo: str | None
    creditos: int | None


class TurmaInstitucionalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    fonte: str
    codigo: str
    semestre: str
    ativa: bool
    professores: list[ProfessorDetalheResponse]
