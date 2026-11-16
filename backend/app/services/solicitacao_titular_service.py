import secrets

from fastapi import HTTPException

from app.core import config
from app.core.security import gerar_hash_token
from app.models.solicitacao_titular import EventoSolicitacao, SolicitacaoTitular
from app.repositories import solicitacao_titular_repository as repo


def ativo():
    return bool(
        config.CANAL_TITULARES_ATIVO
        and config.CANAL_TITULARES_RETENCAO_APROVADA
        and config.CANAL_TITULARES_ATENDENTES
    )


def autorizar(usuario, escrita=False):
    atendentes = config.CANAL_TITULARES_ATENDENTES
    permitidos = atendentes if escrita else [*atendentes, *config.CANAL_TITULARES_LEITORES]
    if str(usuario.id) not in permitidos:
        raise HTTPException(403, "Acesso restrito ao atendimento.")
    return usuario


def criar(db, dados):
    if not ativo():
        raise HTTPException(503, "Recebimento ainda indisponível. Tente novamente mais tarde.")
    chave = secrets.token_urlsafe(32)
    item = SolicitacaoTitular(chave_hash=gerar_hash_token(chave), **dados.model_dump())
    repo.salvar(db, item)
    return {"protocolo": str(item.id), "chave": chave, "recebido_em": item.created_at}


def autenticar_pedido(db, dados):
    item = repo.buscar(db, dados.protocolo)
    esperado = item.chave_hash if item else "0" * 64
    valido = secrets.compare_digest(esperado, gerar_hash_token(dados.chave))
    if not item or not valido:
        raise HTTPException(404, "Protocolo ou chave inválidos.")
    return item


def apresentar(db, item, interno=False):
    eventos = repo.historico(db, item.id)
    return {
        "protocolo": str(item.id),
        "categoria": item.categoria,
        "alvo": item.alvo,
        "descricao": item.descricao,
        "evidencia": item.evidencia,
        "recebido_em": item.created_at,
        "historico": [
            {
                "tipo": e.tipo,
                "texto": e.texto,
                "data": e.created_at,
                **({"responsavel_id": str(e.autor_id) if e.autor_id else None} if interno else {}),
            }
            for e in eventos
            if interno or e.tipo in ("RESPOSTA", "COMPLEMENTO")
        ],
    }


def complementar(db, dados):
    item = autenticar_pedido(db, dados)
    repo.salvar(
        db, EventoSolicitacao(solicitacao_id=item.id, tipo="COMPLEMENTO", texto=dados.texto)
    )
    return apresentar(db, item)


def atender(db, protocolo, usuario, dados):
    autorizar(usuario, escrita=True)
    item = repo.buscar(db, protocolo)
    if not item:
        raise HTTPException(404, "Solicitação não encontrada.")
    repo.salvar(
        db,
        EventoSolicitacao(
            solicitacao_id=item.id, autor_id=usuario.id, tipo=dados.tipo, texto=dados.texto
        ),
    )
    return apresentar(db, item, interno=True)
