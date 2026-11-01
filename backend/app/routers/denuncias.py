from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.auth import obter_moderador, obter_sessao_opcional, obter_usuario_autenticado
from app.core.database import get_db
from app.models.sessao_usuario import SessaoUsuario
from app.models.usuario import Usuario
from app.schemas.denuncia import AgradecimentoResponse, ConfirmacaoDenuncia, DenunciaCreate, DenunciasDaVersao
from app.services import denuncia_service
from app.services.moderacao_service import ModeracaoError

router = APIRouter(prefix="/api", tags=["denuncias"])
Db = Annotated[Session, Depends(get_db)]
UsuarioAutenticado = Annotated[Usuario, Depends(obter_usuario_autenticado)]


def executar(operacao, *args):
    try:
        return operacao(*args)
    except ModeracaoError as erro:
        raise HTTPException(erro.status_code, str(erro)) from erro


@router.post("/comentarios/{versao_id}/denuncias", response_model=ConfirmacaoDenuncia, status_code=201)
def registrar(versao_id: UUID, dados: DenunciaCreate, db: Db,
              sessao: Annotated[SessaoUsuario | None, Depends(obter_sessao_opcional)]):
    return executar(denuncia_service.registrar, db, versao_id, sessao.usuario if sessao else None, dados)


@router.get("/moderacao/comentarios/{versao_id}/denuncias", response_model=DenunciasDaVersao)
def consultar(versao_id: UUID, db: Db, usuario: Annotated[Usuario, Depends(obter_moderador)]):
    return executar(denuncia_service.consultar, db, usuario, versao_id)


@router.get("/agradecimentos", response_model=list[AgradecimentoResponse])
def listar_agradecimentos(db: Db, usuario: UsuarioAutenticado):
    return executar(denuncia_service.listar_agradecimentos, db, usuario)


@router.post("/agradecimentos/{mensagem_id}/exibido", status_code=204)
def confirmar_exibicao(mensagem_id: UUID, db: Db, usuario: UsuarioAutenticado, response: Response):
    executar(denuncia_service.confirmar_exibicao, db, usuario, mensagem_id)
    response.status_code = 204
    return response
