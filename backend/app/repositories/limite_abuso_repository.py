"""SQL exclusivo PostgreSQL; a transação pertence ao serviço do limitador."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import and_, case, delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.contador_abuso import ContadorAbuso


@dataclass(frozen=True)
class EstadoContador:
    quantidade: int
    expira_em: datetime
    proxima_tentativa_em: datetime | None


def agora_banco(db: Session) -> datetime:
    return db.scalar(select(func.clock_timestamp()))


def incrementar(
    db: Session,
    operacao: str,
    chave: str,
    janela_segundos: int,
    agora: datetime,
    respeitar_espera: bool = True,
) -> EstadoContador:
    tabela = ContadorAbuso.__table__
    vencido = tabela.c.expira_em <= agora
    aguardando = and_(respeitar_espera, tabela.c.proxima_tentativa_em > agora)
    comando = insert(tabela).values(
        operacao=operacao,
        chave=chave,
        quantidade=1,
        inicio_em=agora,
        expira_em=agora + timedelta(seconds=janela_segundos),
        proxima_tentativa_em=None,
    )
    comando = comando.on_conflict_do_update(
        index_elements=[tabela.c.operacao, tabela.c.chave],
        set_={
            "quantidade": case(
                (vencido, 1), (aguardando, tabela.c.quantidade), else_=tabela.c.quantidade + 1
            ),
            "inicio_em": case((vencido, comando.excluded.inicio_em), else_=tabela.c.inicio_em),
            "expira_em": case((vencido, comando.excluded.expira_em), else_=tabela.c.expira_em),
            "proxima_tentativa_em": case((vencido, None), else_=tabela.c.proxima_tentativa_em),
        },
    ).returning(tabela.c.quantidade, tabela.c.expira_em, tabela.c.proxima_tentativa_em)
    linha = db.execute(comando).one()
    return EstadoContador(*linha)


def definir_proxima_tentativa(db: Session, operacao: str, chave: str, proxima: datetime):
    db.execute(
        update(ContadorAbuso)
        .where(ContadorAbuso.operacao == operacao, ContadorAbuso.chave == chave)
        .values(proxima_tentativa_em=proxima)
    )


def reiniciar_identidade(db: Session, operacao: str, chave: str):
    db.execute(
        delete(ContadorAbuso).where(
            ContadorAbuso.operacao == operacao, ContadorAbuso.chave == chave
        )
    )


def limpar_expirados(db: Session, agora: datetime, lote: int) -> int:
    # SKIP LOCKED permite vários executores sem aguardar um contador em uso.
    tabela = ContadorAbuso.__table__
    vencidos = (
        select(tabela.c.operacao, tabela.c.chave)
        .where(tabela.c.expira_em <= agora)
        .order_by(tabela.c.expira_em)
        .limit(lote)
        .with_for_update(skip_locked=True)
        .cte("vencidos")
    )
    comando = delete(tabela).where(
        and_(tabela.c.operacao == vencidos.c.operacao, tabela.c.chave == vencidos.c.chave)
    )
    return db.execute(comando).rowcount
