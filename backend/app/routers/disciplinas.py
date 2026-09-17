from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.institucional import (
    DisciplinaDetalheResponse,
    TurmaInstitucionalResponse,
)
from app.services import institucional_service


router = APIRouter(prefix="/api/disciplinas", tags=["disciplinas"])


@router.get("", response_model=list[DisciplinaDetalheResponse])
def listar_disciplinas(
    session: Annotated[Session, Depends(get_db)],
    codigo: str | None = None,
    nome: str | None = None,
) -> list[DisciplinaDetalheResponse]:
    return institucional_service.listar_disciplinas(session, codigo, nome)


@router.get("/{disciplina_id}", response_model=DisciplinaDetalheResponse)
def obter_disciplina(
    disciplina_id: UUID,
    session: Annotated[Session, Depends(get_db)],
) -> DisciplinaDetalheResponse:
    try:
        return institucional_service.obter_disciplina(session, disciplina_id)
    except institucional_service.RecursoInstitucionalNaoEncontradoError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro


@router.get(
    "/{disciplina_id}/turmas",
    response_model=list[TurmaInstitucionalResponse],
)
def listar_turmas_da_disciplina(
    disciplina_id: UUID,
    session: Annotated[Session, Depends(get_db)],
) -> list[TurmaInstitucionalResponse]:
    try:
        return institucional_service.listar_turmas_da_disciplina(
            session, disciplina_id
        )
    except institucional_service.RecursoInstitucionalNaoEncontradoError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro
