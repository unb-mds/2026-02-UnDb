from sqlalchemy import delete, select
from app.models.registro_acesso import RegistroAcesso


def gravar(db, dados):
    db.add(RegistroAcesso(**dados))
    db.commit()


def purgar(db, agora, lote):
    ids = select(RegistroAcesso.id).where(RegistroAcesso.expira_em <= agora).limit(lote)
    return db.execute(delete(RegistroAcesso).where(RegistroAcesso.id.in_(ids))).rowcount
