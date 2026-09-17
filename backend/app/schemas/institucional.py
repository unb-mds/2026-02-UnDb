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
