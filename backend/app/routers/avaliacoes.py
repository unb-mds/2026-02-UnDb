from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import obter_usuario_confirmado, obter_usuario_autenticado
from app.core.database import get_db
from app.core.protecao_fluxos import avaliar
from app.models.usuario import Usuario
from app.schemas.avaliacao import AvaliacaoCreate, AvaliacaoResponse, MinhasAvaliacoesResponse
from app.services import avaliacao_service

router = APIRouter(prefix="/api/avaliacoes", tags=["avaliacoes"])


@router.post("", response_model=AvaliacaoResponse, dependencies=[Depends(avaliar)])
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
    resposta = AvaliacaoResponse.model_validate(avaliacao)
    resposta.comentario_erro = dados.comentario_erro
    resposta.comentario_estado = getattr(avaliacao, "_comentario_estado", None)
    return resposta


@router.get("/minhas", response_model=MinhasAvaliacoesResponse)
def listar_minhas_avaliacoes(
    usuario: Annotated[Usuario, Depends(obter_usuario_autenticado)],
    session: Annotated[Session, Depends(get_db)],
    pagina: Annotated[int, Query(ge=1, le=100000)] = 1,
) -> MinhasAvaliacoesResponse:
    return avaliacao_service.listar_minhas_avaliacoes(session, usuario, pagina)
