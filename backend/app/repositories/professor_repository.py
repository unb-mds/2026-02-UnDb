from sqlalchemy.orm import Session

from app.models.professor import Professor


def get_by_nome(db: Session, nome: str) -> Professor | None:
    return db.query(Professor).filter_by(nome=nome).first()


def create(db: Session, nome: str, departamento: str) -> Professor:
    professor = Professor(nome=nome, departamento=departamento)
    db.add(professor)
    db.flush() 
    return professor