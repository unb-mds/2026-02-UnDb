from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.core.auth import obter_usuario_confirmado
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.comentario import ComentarioDoAutorResponse
from app.services import comentario_service


router = APIRouter(prefix="/api/comentarios", tags=["comentarios"])


@router.get(
    "/meu",
    response_model=list[ComentarioDoAutorResponse],
)
def listar_meus_comentarios(
    usuario: Annotated[Usuario, Depends(obter_usuario_confirmado)],
    session: Annotated[Session, Depends(get_db)],
) -> list[ComentarioDoAutorResponse]:
    """Lista os comentarios do autor autenticado (todos os estados)."""
    return comentario_service.listar_do_autor(session, usuario)


@router.patch(
    "/{comentario_id}/retirar",
    response_model=ComentarioDoAutorResponse,
)
def retirar_comentario(
    comentario_id: Annotated[UUID, Path()],
    usuario: Annotated[Usuario, Depends(obter_usuario_confirmado)],
    session: Annotated[Session, Depends(get_db)],
) -> ComentarioDoAutorResponse:
    """Retira um comentario pelo autor (PUBLICADO, PENDENTE ou SUSPENSO)."""
    try:
        return comentario_service.retirar(session, comentario_id, usuario)
    except comentario_service.RecursoNaoEncontradoError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro
    except comentario_service.ComentarioNaoAutorizadoError as erro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(erro),
        ) from erro
