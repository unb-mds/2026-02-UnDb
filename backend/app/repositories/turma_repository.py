from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.turma import Turma, turmas_professores


def existe_vinculo_professor_disciplina(
    db: Session, professor_id: UUID, disciplina_id: UUID
) -> bool:
    return (
        db.query(Turma.id)
        .join(
            turmas_professores,
            turmas_professores.c.turma_id == Turma.id,
        )
        .filter(
            turmas_professores.c.professor_id == professor_id,
            Turma.disciplina_id == disciplina_id,
            Turma.ativa.is_(True),
        )
        .first()
        is not None
    )


def get_by_disciplina_professor_semestre(
    db: Session, disciplina_id: UUID, professor_id: UUID, semestre: str
) -> Turma | None:
    return (
        db.query(turmas_professores.c.turma_id)
        .join(Turma, Turma.id == turmas_professores.c.turma_id)
        .filter(
            turmas_professores.c.professor_id == professor_id,
            Turma.disciplina_id == disciplina_id,
            Turma.ativa.is_(True),
        )
        .first()
        is not None
    )


def get_by_identidade(
    db: Session,
    fonte: str,
    unidade_id: UUID,
    disciplina_id: UUID,
    semestre: str,
    codigo: str,
) -> Turma | None:
    return db.scalar(
        select(Turma).where(
            Turma.fonte == fonte,
            Turma.unidade_id == unidade_id,
            Turma.disciplina_id == disciplina_id,
            Turma.semestre == semestre,
            Turma.codigo == codigo,
        )
    )


def create(
    db: Session,
    fonte: str,
    unidade_id: UUID,
    disciplina_id: UUID,
    semestre: str,
    codigo: str,
) -> Turma:
    turma = Turma(
        fonte=fonte,
        unidade_id=unidade_id,
        disciplina_id=disciplina_id,
        semestre=semestre,
        codigo=codigo,
        ativa=True,
    )
    db.add(turma)
    db.flush()
    return turma


def inativar_ausentes(
    db: Session,
    fonte: str,
    unidade_id: UUID,
    semestre: str,
    ids_observados: set[UUID],
) -> None:
    consulta = update(Turma).where(
        Turma.fonte == fonte,
        Turma.unidade_id == unidade_id,
        Turma.semestre == semestre,
    )
    if ids_observados:
        consulta = consulta.where(Turma.id.not_in(ids_observados))
    db.execute(consulta.values(ativa=False))
