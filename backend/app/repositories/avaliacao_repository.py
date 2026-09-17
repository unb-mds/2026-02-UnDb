from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.professor import Professor


def obter_professor(db: Session, professor_id: UUID) -> Professor | None:
    return db.get(Professor, professor_id)


def obter_disciplina(db: Session, disciplina_id: UUID) -> Disciplina | None:
    return db.get(Disciplina, disciplina_id)


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
