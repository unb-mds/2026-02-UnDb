from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.auth import obter_moderador
from app.core.database import get_db
from app.models.enums import EstadoComentario
from app.models.usuario import Usuario
from app.schemas.moderacao import AcaoModeracaoRequest, ComentarioModeracaoResponse, DecisaoResponse
from app.services import moderacao_service, triagem_service
from app.schemas.triagem import TriagemResponse

router = APIRouter(prefix="/api/moderacao/comentarios", tags=["moderacao"])
Db = Annotated[Session, Depends(get_db)]
Moderador = Annotated[Usuario, Depends(obter_moderador)]


def executar(operacao, *args):
    try:
        return operacao(*args)
    except moderacao_service.ModeracaoError as erro:
        raise HTTPException(erro.status_code, str(erro)) from erro


@router.get("", response_model=list[ComentarioModeracaoResponse])
def listar(db: Db, usuario: Moderador, estado: EstadoComentario | None = None):
    return executar(moderacao_service.listar, db, usuario, estado)


@router.get("/{versao_id}", response_model=ComentarioModeracaoResponse)
def consultar(versao_id: UUID, db: Db, usuario: Moderador):
    return executar(moderacao_service.consultar, db, usuario, versao_id)


@router.get("/{versao_id}/decisoes", response_model=list[DecisaoResponse])
def decisoes(versao_id: UUID, db: Db, usuario: Moderador):
    return executar(moderacao_service.decisoes, db, usuario, versao_id)


@router.post("/{versao_id}/acoes", response_model=DecisaoResponse)
def decidir(versao_id: UUID, dados: AcaoModeracaoRequest, db: Db, usuario: Moderador):
    return executar(moderacao_service.decidir, db, usuario, versao_id, dados)


@router.post("/{versao_id}/triagem", response_model=TriagemResponse)
def analisar_com_apoio(versao_id: UUID, db: Db, usuario: Moderador, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return executar(triagem_service.analisar, db, usuario, versao_id)
