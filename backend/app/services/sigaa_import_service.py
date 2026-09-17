from sqlalchemy.orm import Session

from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.turma import Turma
from app.repositories import (
    disciplina_repository,
    professor_repository,
    turma_repository,
)
from app.scrapers.sigaa_poc import Oferta


class OfertaNaoPersistivelError(ValueError):
    """A oferta depende de informação que o modelo ainda não representa."""


def _get_or_create_professor(
    db: Session, nome: str, departamento: str
) -> Professor:
    professor = professor_repository.get_by_nome_e_departamento(
        db, nome, departamento
    )
    if professor is None:
        professor = professor_repository.create(db, nome, departamento)
    return professor


def _get_or_create_disciplina(
    db: Session, oferta: Oferta, departamento: str
) -> Disciplina:
    disciplina = disciplina_repository.get_by_codigo(db, oferta.componente_codigo)
    if disciplina is None:
        disciplina = disciplina_repository.create(
            db,
            codigo=oferta.componente_codigo,
            nome=oferta.componente_nome,
            departamento=departamento,
        )
    return disciplina


def salvar_oferta(db: Session, oferta: Oferta, departamento: str) -> Turma:
    """Persiste uma oferta cujo vínculo cabe no modelo relacional atual.

    Ofertas sem docente ou com múltiplos docentes permanecem pendentes de decisão
    de modelo na Issue #25 e são recusadas antes de qualquer escrita.
    """
    departamento = departamento.strip()
    if not departamento:
        raise OfertaNaoPersistivelError("A oferta não informa o departamento.")
    if len(oferta.docentes) != 1:
        raise OfertaNaoPersistivelError(
            "A oferta deve possuir exatamente um docente para o modelo atual; "
            f"turma {oferta.turma_codigo!r} possui {len(oferta.docentes)}."
        )

    disciplina = _get_or_create_disciplina(db, oferta, departamento)
    professor = _get_or_create_professor(db, oferta.docentes[0], departamento)

    turma = turma_repository.get_by_disciplina_professor_semestre(
        db, disciplina.id, professor.id, oferta.periodo
    )
    if turma is None:
        turma = turma_repository.create(
            db, disciplina.id, professor.id, oferta.periodo
        )
    return turma
