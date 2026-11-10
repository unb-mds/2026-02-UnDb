from uuid import UUID

from sqlalchemy.orm import Session

from app.models.importacao_execucao import ImportacaoExecucao


def obter_por_id(db: Session, execucao_id: UUID) -> ImportacaoExecucao | None:
    return db.get(ImportacaoExecucao, execucao_id)
