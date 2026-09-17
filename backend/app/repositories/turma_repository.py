from uuid import UUID

from sqlalchemy.orm import Session

from app.models.turma import Turma


def get_by_disciplina_professor_semestre(
    db: Session, disciplina_id: UUID, professor_id: UUID, semestre: str
) -> Turma | None:
    return (
        db.query(Turma)
        .filter_by(
            disciplina_id=disciplina_id,
            professor_id=professor_id,
            semestre=semestre,
        )
        .first()
    )


def create(
    db: Session, disciplina_id: UUID, professor_id: UUID, semestre: str
) -> Turma:
    turma = Turma(
        disciplina_id=disciplina_id,
        professor_id=professor_id,
        semestre=semestre,
    )
    db.add(turma)
    db.flush()
    return turma
