from typing import Annotated, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.core.auth import obter_usuario_confirmado
from app.core.database import get_db
from app.models.usuario import Usuario
from app.repositories import identidade_docente_repository as repo
from app.schemas.identidade_docente import (
    PreviaResponse,
    PendenciaResponse,
    DecidirRequest,
    DecisaoResponse,
)
from app.services import identidade_docente_service as service

router = APIRouter(prefix="/api/moderacao/identidades", tags=["identidades"])
Db = Annotated[Session, Depends(get_db)]


def autorizado(usuario: Annotated[Usuario, Depends(obter_usuario_confirmado)]):
    try:
        service.autorizar(usuario)
    except service.IdentidadeError as erro:
        raise HTTPException(erro.status_code, str(erro)) from erro
    return usuario


Revisor = Annotated[Usuario, Depends(autorizado)]


@router.get("", response_model=list[PendenciaResponse])
def listar(
    db: Db,
    usuario: Revisor,
    response: Response,
    estado: Literal["PENDENTE", "CONFIRMADA", "SEPARADA", "APLICADA"] = "PENDENTE",
    offset: int = Query(default=0, ge=0),
):
    response.headers["Cache-Control"] = "no-store"
    return repo.listar(db, estado, offset=offset)


@router.get("/{id}/decisoes", response_model=list[DecisaoResponse])
def historico(id: UUID, db: Db, usuario: Revisor, response: Response):
    response.headers["Cache-Control"] = "no-store"
    if repo.por_id(db, id) is None:
        raise HTTPException(404, "Pendência não encontrada.")
    return repo.decisoes(db, id)


@router.post("/{id}/decisoes", response_model=PendenciaResponse)
def decidir(id: UUID, dados: DecidirRequest, db: Db, usuario: Revisor, response: Response):
    response.headers["Cache-Control"] = "no-store"
    try:
        return service.decidir(db, usuario, id, dados)
    except service.IdentidadeError as erro:
        raise HTTPException(erro.status_code, str(erro)) from erro


@router.get("/{id}/previa", response_model=PreviaResponse)
def previa(id: UUID, identificador: str, db: Db, usuario: Revisor, response: Response):
    response.headers["Cache-Control"] = "no-store"
    item = repo.por_id(db, id)
    if item is None:
        raise HTTPException(404, "Pendência não encontrada.")
    try:
        return service.previa(db, item, identificador)
    except service.IdentidadeError as erro:
        raise HTTPException(erro.status_code, str(erro)) from erro
