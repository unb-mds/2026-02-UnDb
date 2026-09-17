from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.professor import Professor


def professor_existe(db: Session, professor_id: UUID) -> bool:
    return db.get(Professor, professor_id) is not None


def disciplina_existe(db: Session, disciplina_id: UUID) -> bool:
    return db.get(Disciplina, disciplina_id) is not None


def listar_por_professor_e_disciplina(
    db: Session,
    professor_id: UUID,
    disciplina_id: UUID,
) -> list[Avaliacao]:
    consulta = select(Avaliacao).where(
        Avaliacao.professor_id == professor_id,
        Avaliacao.disciplina_id == disciplina_id,
    )
    return list(db.scalars(consulta).all())
