from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.core.auth import obter_usuario_confirmado
from app.core.database import get_db
from app.core.protecao_fluxos import titular, registrar_bypass
from app.models.usuario import Usuario
from app.repositories import solicitacao_titular_repository as repo
from app.schemas.solicitacao_titular import (
    AtenderSolicitacao,
    ComplementarSolicitacao,
    ConsultarSolicitacao,
    CriarSolicitacao,
    ReciboSolicitacao,
    ResumoSolicitacao,
    ConsultaPublica,
    ConsultaInterna,
    Disponibilidade,
    Permissao,
)
from app.services import solicitacao_titular_service as service


def privado(response: Response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"


router = APIRouter(tags=["solicitacoes"], dependencies=[Depends(privado)])
Db = Annotated[Session, Depends(get_db)]
UsuarioConfirmado = Annotated[Usuario, Depends(obter_usuario_confirmado)]


@router.get("/api/solicitacoes/disponibilidade", response_model=Disponibilidade)
def disponibilidade():
    return {"ativo": service.ativo()}


@router.post(
    "/api/solicitacoes",
    status_code=201,
    dependencies=[Depends(titular("titular.criar"))],
    response_model=ReciboSolicitacao,
)
def criar(dados: CriarSolicitacao, db: Db):
    return service.criar(db, dados)


@router.post(
    "/api/solicitacoes/consultar",
    dependencies=[Depends(titular("titular.consultar"))],
    response_model=ConsultaPublica,
)
def consultar(dados: ConsultarSolicitacao, db: Db):
    return service.apresentar(db, service.autenticar_pedido(db, dados))


@router.post(
    "/api/solicitacoes/complementos",
    dependencies=[Depends(titular("titular.complementar"))],
    response_model=ConsultaPublica,
)
def complementar(dados: ComplementarSolicitacao, db: Db):
    return service.complementar(db, dados)


@router.get("/api/atendimento/permissao", response_model=Permissao)
def permissao(usuario: UsuarioConfirmado):
    registrar_bypass()
    service.autorizar(usuario)
    from app.core.config import CANAL_TITULARES_ATENDENTES

    return {"responder": str(usuario.id) in CANAL_TITULARES_ATENDENTES}


@router.get("/api/atendimento", response_model=list[ResumoSolicitacao])
def listar(db: Db, usuario: UsuarioConfirmado, offset: int = Query(default=0, ge=0)):
    registrar_bypass()
    service.autorizar(usuario)
    return [
        {"protocolo": str(i.id), "categoria": i.categoria, "recebido_em": i.created_at}
        for i in repo.listar(db, offset)
    ]


@router.get("/api/atendimento/{protocolo}", response_model=ConsultaInterna)
def detalhe(protocolo: UUID, db: Db, usuario: UsuarioConfirmado):
    registrar_bypass()
    service.autorizar(usuario)
    item = repo.buscar(db, protocolo)
    if not item:
        raise HTTPException(404, "Solicitação não encontrada.")
    return service.apresentar(db, item, interno=True)


@router.post("/api/atendimento/{protocolo}/eventos", response_model=ConsultaInterna)
def atender(protocolo: UUID, dados: AtenderSolicitacao, db: Db, usuario: UsuarioConfirmado):
    registrar_bypass()
    return service.atender(db, protocolo, usuario, dados)
