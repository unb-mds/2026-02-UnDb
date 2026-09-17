from sqlalchemy.orm import Session

from app.models.professor import Professor
from app.models.disciplina import Disciplina
from app.models.turma import Turma
from app.repositories import (
    disciplina_repository,
    professor_repository,
    turma_repository,
)
from app.scrapers.sigaa_poc import Oferta

# Proposta, não decisão definida — ver Pending Decisions abaixo.
DEPARTAMENTO_PADRAO = "DEPTO CIÊNCIAS DA COMPUTAÇÃO"


def _get_or_create_professor(db: Session, nome: str) -> Professor:
    professor = professor_repository.get_by_nome(db, nome)
    if professor is None:
        professor = professor_repository.create(db, nome, DEPARTAMENTO_PADRAO)
    return professor


def _get_or_create_disciplina(db: Session, oferta: Oferta) -> Disciplina:
    disciplina = disciplina_repository.get_by_codigo(db, oferta.componente_codigo)
    if disciplina is None:
        disciplina = disciplina_repository.create(
            db,
            codigo=oferta.componente_codigo,
            nome=oferta.componente_nome,
            departamento=DEPARTAMENTO_PADRAO,
        )
    return disciplina


def salvar_oferta(db: Session, oferta: Oferta) -> list[Turma]:
    """Persiste uma Oferta extraída do SIGAA como Disciplina, Professor(es) e Turma(s).

    Proposta (Pending Decision, ver handoff): uma Turma é criada por docente da
    oferta, já que o modelo atual não suporta múltiplos professores por Turma.
    `turma_codigo` da Oferta é descartado — não há campo correspondente no modelo.
    """
    disciplina = _get_or_create_disciplina(db, oferta)

    turmas: list[Turma] = []
    for nome_docente in oferta.docentes:
        professor = _get_or_create_professor(db, nome_docente)

        turma = turma_repository.get_by_disciplina_professor_semestre(
            db, disciplina.id, professor.id, oferta.periodo
        )
        if turma is None:
            turma = turma_repository.create(
                db, disciplina.id, professor.id, oferta.periodo
            )
        turmas.append(turma)

    return turmas