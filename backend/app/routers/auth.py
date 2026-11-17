import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.auth import (
    definir_cookie_sessao,
    obter_sessao_opcional,
    obter_sessao_para_logout,
    remover_cookie_sessao,
)
from app.core.database import get_db
from app.core.dependencia_auth_abuso import obter_protecao_auth
from app.models.sessao_usuario import SessaoUsuario
from app.schemas.auth import (
    RecuperarSenhaRequest,
    RedefinirSenhaRequest,
    CadastroRequest,
    ConfirmacaoEmailRequest,
    LoginRequest,
    MensagemResponse,
    SessaoResponse,
    ReenvioConfirmacaoRequest,
)
from app.services import auth_service
from app.services.auth_abuso_service import ProtecaoAuth
from app.services.email_service import EmailDeliveryError, EmailSender, get_email_sender


router = APIRouter(prefix="/api/auth", tags=["auth"])
Protecao = Annotated[ProtecaoAuth, Depends(obter_protecao_auth)]
RESPOSTAS_ABUSO = {
    429: {"description": "Restrição temporária; consultar Retry-After."},
    503: {"description": "Proteção temporariamente indisponível; consultar Retry-After."},
}


@router.post(
    "/cadastro",
    response_model=MensagemResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses=RESPOSTAS_ABUSO,
)
def cadastrar(
    dados: CadastroRequest,
    session: Annotated[Session, Depends(get_db)],
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
    protecao: Protecao,
) -> MensagemResponse:
    protecao.email("auth.cadastro", dados.email)
    try:
        message = auth_service.cadastrar(session, dados, email_sender)
    except EmailDeliveryError:
        logging.getLogger(__name__).error("auth.confirmacao.envio_falhou")
        message = auth_service.CADASTRO_MESSAGE
    return MensagemResponse(message=message)


@router.post("/confirmar", response_model=MensagemResponse, responses=RESPOSTAS_ABUSO)
def confirmar_email(
    dados: ConfirmacaoEmailRequest,
    session: Annotated[Session, Depends(get_db)],
    protecao: Protecao,
) -> MensagemResponse:
    protecao.token("auth.confirmacao", dados.token)
    try:
        message = auth_service.confirmar_email(session, dados.token)
    except auth_service.TokenConfirmacaoInvalidoError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro
    return MensagemResponse(message=message)


@router.post("/login", response_model=MensagemResponse, responses=RESPOSTAS_ABUSO)
def login(
    dados: LoginRequest,
    response: Response,
    session: Annotated[Session, Depends(get_db)],
    protecao: Protecao,
) -> MensagemResponse:
    protecao.login(dados.email)
    try:
        autenticacao = auth_service.autenticar(
            session, dados, antes_de_criar_sessao=lambda: protecao.sucesso_login(dados.email)
        )
    except auth_service.CredenciaisInvalidasError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(erro),
        ) from erro

    definir_cookie_sessao(response, autenticacao.token)
    return MensagemResponse(message=auth_service.LOGIN_MESSAGE)


@router.get("/sessao", response_model=SessaoResponse)
def consultar_sessao(
    sessao: Annotated[SessaoUsuario | None, Depends(obter_sessao_opcional)],
) -> SessaoResponse:
    return SessaoResponse(autenticado=sessao is not None)


@router.post("/logout", response_model=MensagemResponse)
def logout(
    response: Response,
    sessao: Annotated[SessaoUsuario, Depends(obter_sessao_para_logout)],
    session: Annotated[Session, Depends(get_db)],
) -> MensagemResponse:
    message = auth_service.encerrar_sessao(session, sessao)
    remover_cookie_sessao(response)
    return MensagemResponse(message=message)


@router.post(
    "/recuperar-senha",
    response_model=MensagemResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses=RESPOSTAS_ABUSO,
)
def recuperar_senha(
    dados: RecuperarSenhaRequest,
    session: Annotated[Session, Depends(get_db)],
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
    protecao: Protecao,
) -> MensagemResponse:
    protecao.email("auth.recuperacao", dados.email)
    try:
        auth_service.solicitar_recuperacao_senha(session, dados.email, email_sender)
    except EmailDeliveryError:
        # Não diferenciar conta existente nem expor detalhes do provedor.
        logging.getLogger(__name__).error("auth.recuperacao.envio_falhou")
    return MensagemResponse(message=auth_service.RECUPERACAO_MESSAGE)


@router.post("/redefinir-senha", response_model=MensagemResponse, responses=RESPOSTAS_ABUSO)
def redefinir_senha(
    dados: RedefinirSenhaRequest,
    response: Response,
    session: Annotated[Session, Depends(get_db)],
    protecao: Protecao,
) -> MensagemResponse:
    protecao.token("auth.redefinicao", dados.token)
    try:
        message = auth_service.redefinir_senha(
            session,
            dados.token,
            dados.senha,
            antes_de_confirmar=lambda usuario: protecao.sucesso_login(usuario.email),
        )
    except auth_service.TokenRecuperacaoInvalidoError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro)) from erro
    remover_cookie_sessao(response)
    return MensagemResponse(message=message)


@router.post(
    "/reenviar-confirmacao",
    response_model=MensagemResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses=RESPOSTAS_ABUSO,
)
def reenviar_confirmacao(
    dados: ReenvioConfirmacaoRequest,
    session: Annotated[Session, Depends(get_db)],
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
    protecao: Protecao,
) -> MensagemResponse:
    protecao.email("auth.reenvio", dados.email)
    try:
        auth_service.reenviar_confirmacao(session, dados.email, email_sender, dados.return_to)
    except EmailDeliveryError:
        logging.getLogger(__name__).error("auth.confirmacao.envio_falhou")
    return MensagemResponse(message=auth_service.REENVIO_MESSAGE)
