from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import DEBUG
from app.core.database import get_db
from app.models.sessao_usuario import SessaoUsuario
from app.models.usuario import Usuario
from app.services import auth_service


SESSION_COOKIE_NAME = "undb_session"
SESSION_MAX_AGE_SECONDS = int(auth_service.SESSION_TTL.total_seconds())


def definir_cookie_sessao(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=not DEBUG,
        samesite="lax",
        path="/",
    )


def remover_cookie_sessao(response: Response) -> None:
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        secure=not DEBUG,
        samesite="lax",
        path="/",
    )


def _validar_sessao(
    request: Request,
    response: Response,
    db: Session,
    *,
    renovar_cookie: bool,
) -> SessaoUsuario:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    try:
        sessao = auth_service.validar_e_renovar_sessao(db, token)
    except auth_service.SessaoInvalidaError as erro:
        remover_cookie_sessao(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(erro),
        ) from erro

    if renovar_cookie:
        definir_cookie_sessao(response, token)
    return sessao


def obter_sessao_autenticada(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> SessaoUsuario:
    return _validar_sessao(request, response, db, renovar_cookie=True)


def obter_sessao_opcional(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> SessaoUsuario | None:
    try:
        return _validar_sessao(request, response, db, renovar_cookie=True)
    except HTTPException:
        return None


def obter_sessao_para_logout(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> SessaoUsuario:
    return _validar_sessao(request, response, db, renovar_cookie=False)


def obter_usuario_autenticado(
    sessao: Annotated[SessaoUsuario, Depends(obter_sessao_autenticada)],
) -> Usuario:
    return sessao.usuario


def obter_usuario_confirmado(
    usuario: Annotated[Usuario, Depends(obter_usuario_autenticado)],
) -> Usuario:
    if not usuario.email_confirmado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=auth_service.EMAIL_NAO_CONFIRMADO_MESSAGE,
        )
    return usuario
