from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.core.auth import obter_usuario_autenticado, obter_moderador, remover_cookie_sessao
from app.core.database import get_db
from app.core.protecao_fluxos import registrar_bypass
from app.models.usuario import Usuario
from app.services import retencao_service

router = APIRouter(tags=["exclusao"])
Db = Annotated[Session, Depends(get_db)]
Autenticado = Annotated[Usuario, Depends(obter_usuario_autenticado)]


@router.delete("/api/auth/conta", status_code=204)
def excluir_conta(db: Db, usuario: Autenticado):
    registrar_bypass()
    retencao_service.excluir_conta(db, usuario)
    response = Response(status_code=204)
    remover_cookie_sessao(response)
    return response


@router.delete("/api/avaliacoes/{id}", status_code=204)
def excluir_avaliacao(id: UUID, db: Db, usuario: Autenticado):
    registrar_bypass()
    retencao_service.excluir_avaliacao(db, usuario, id)
    return Response(status_code=204)


@router.delete("/api/moderacao/avaliacoes/{id}", status_code=204)
def remover_avaliacao(id: UUID, db: Db, usuario: Annotated[Usuario, Depends(obter_moderador)]):
    registrar_bypass()
    retencao_service.excluir_avaliacao(db, usuario, id, moderacao=True)
    return Response(status_code=204)
