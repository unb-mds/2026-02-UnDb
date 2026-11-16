from sqlalchemy import select

from app.models.solicitacao_titular import EventoSolicitacao, SolicitacaoTitular


def buscar(db, protocolo):
    return db.get(SolicitacaoTitular, protocolo)


def listar(db, offset):
    return db.scalars(
        select(SolicitacaoTitular)
        .order_by(SolicitacaoTitular.created_at.desc(), SolicitacaoTitular.id)
        .offset(offset)
        .limit(50)
    ).all()


def historico(db, protocolo):
    return db.scalars(
        select(EventoSolicitacao)
        .where(EventoSolicitacao.solicitacao_id == protocolo)
        .order_by(EventoSolicitacao.created_at, EventoSolicitacao.id)
    ).all()


def salvar(db, item):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
