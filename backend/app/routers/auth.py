from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.auth import (
    definir_cookie_sessao,
    obter_sessao_para_logout,
    remover_cookie_sessao,
)
from app.core.database import get_db
from app.models.sessao_usuario import SessaoUsuario
from app.schemas.auth import (
    CadastroRequest,
    ConfirmacaoEmailRequest,
    LoginRequest,
    MensagemResponse,
)
from app.services import auth_service
from app.services.email_service import EmailDeliveryError, EmailSender, get_email_sender


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/cadastro",
    response_model=MensagemResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def cadastrar(
    dados: CadastroRequest,
    session: Annotated[Session, Depends(get_db)],
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
) -> MensagemResponse:
    try:
        message = auth_service.cadastrar(session, dados, email_sender)
    except EmailDeliveryError as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível enviar o e-mail de confirmação agora.",
        ) from erro
    return MensagemResponse(message=message)


@router.post("/confirmar", response_model=MensagemResponse)
def confirmar_email(
    dados: ConfirmacaoEmailRequest,
    session: Annotated[Session, Depends(get_db)],
) -> MensagemResponse:
    try:
        message = auth_service.confirmar_email(session, dados.token)
    except auth_service.TokenConfirmacaoInvalidoError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro
    return MensagemResponse(message=message)


@router.post("/login", response_model=MensagemResponse)
def login(
    dados: LoginRequest,
    response: Response,
    session: Annotated[Session, Depends(get_db)],
) -> MensagemResponse:
    try:
        autenticacao = auth_service.autenticar(session, dados)
    except auth_service.CredenciaisInvalidasError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(erro),
        ) from erro

    definir_cookie_sessao(response, autenticacao.token)
    return MensagemResponse(message=auth_service.LOGIN_MESSAGE)


@router.post("/logout", response_model=MensagemResponse)
def logout(
    response: Response,
    sessao: Annotated[SessaoUsuario, Depends(obter_sessao_para_logout)],
    session: Annotated[Session, Depends(get_db)],
) -> MensagemResponse:
    message = auth_service.encerrar_sessao(session, sessao)
    remover_cookie_sessao(response)
    return MensagemResponse(message=message)
