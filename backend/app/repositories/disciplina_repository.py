from sqlalchemy.orm import Session

from app.models.disciplina import Disciplina


def get_by_codigo(db: Session, codigo: str) -> Disciplina | None:
    return db.query(Disciplina).filter_by(codigo=codigo).first()


def create(db: Session, codigo: str, nome: str, departamento: str) -> Disciplina:
    disciplina = Disciplina(codigo=codigo, nome=nome, departamento=departamento)
    db.add(disciplina)
    db.flush()
    return disciplina
