from uuid import UUID

from sqlalchemy.orm import Session

from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.turma import Turma
from app.repositories import disciplina_repository, professor_repository


class RecursoInstitucionalNaoEncontradoError(Exception):
    pass


def listar_professores(db: Session, nome: str | None = None) -> list[Professor]:
    return professor_repository.listar(db, nome)


def obter_professor(db: Session, professor_id: UUID) -> Professor:
    professor = db.get(Professor, professor_id)
    if professor is None:
        raise RecursoInstitucionalNaoEncontradoError("professor nao encontrado")
    return professor


def listar_disciplinas_do_professor(
    db: Session, professor_id: UUID
) -> list[Disciplina]:
    obter_professor(db, professor_id)
    return professor_repository.listar_disciplinas(db, professor_id)


def listar_disciplinas(
    db: Session, codigo: str | None = None, nome: str | None = None
) -> list[Disciplina]:
    return disciplina_repository.listar(db, codigo=codigo, nome=nome)


def obter_disciplina(db: Session, disciplina_id: UUID) -> Disciplina:
    disciplina = db.get(Disciplina, disciplina_id)
    if disciplina is None:
        raise RecursoInstitucionalNaoEncontradoError("disciplina nao encontrada")
    return disciplina


def listar_turmas_da_disciplina(db: Session, disciplina_id: UUID) -> list[Turma]:
    obter_disciplina(db, disciplina_id)
    return disciplina_repository.listar_turmas(db, disciplina_id)
