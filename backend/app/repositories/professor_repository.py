from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.professor import Professor
from app.models.turma import Turma


def get_by_nome_e_departamento(
    db: Session, nome: str, departamento: str
) -> Professor | None:
    return (
        db.query(Professor)
        .filter_by(nome=nome, departamento=departamento)
        .first()
    )


def create(db: Session, nome: str, departamento: str) -> Professor:
    professor = Professor(nome=nome, departamento=departamento)
    db.add(professor)
    db.flush()
    return professor


def listar_por_disciplina(db: Session, disciplina_id: UUID) -> list[Professor]:
    consulta = (
        select(Professor)
        .join(Turma, Turma.professor_id == Professor.id)
        .where(Turma.disciplina_id == disciplina_id)
        .distinct()
    )
    return list(db.scalars(consulta).all())
