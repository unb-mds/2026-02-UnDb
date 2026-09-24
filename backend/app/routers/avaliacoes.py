from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import obter_usuario_confirmado
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.avaliacao import AvaliacaoCreate, AvaliacaoResponse
from app.services import avaliacao_service

router = APIRouter(prefix="/api/avaliacoes", tags=["avaliacoes"])


@router.post("", response_model=AvaliacaoResponse)
def registrar_avaliacao(
    dados: AvaliacaoCreate,
    usuario: Annotated[Usuario, Depends(obter_usuario_confirmado)],
    session: Annotated[Session, Depends(get_db)],
) -> AvaliacaoResponse:
    try:
        avaliacao = avaliacao_service.registrar_avaliacao(session, usuario, dados)
    except avaliacao_service.RecursoNaoEncontradoError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro
    return AvaliacaoResponse.model_validate(avaliacao)
