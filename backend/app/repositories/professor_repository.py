from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.domain.texto import normalizar_busca
from app.models.professor import Professor
from app.models.disciplina import Disciplina
from app.models.turma import Turma, turmas_professores


def get_by_identidade_origem(db: Session, identidade: str) -> Professor | None:
    return db.scalar(
        select(Professor).where(Professor.identidade_origem == identidade)
    )


def get_or_create_provisorio(
    db: Session, nome: str, departamento: str, identidade: str
) -> Professor:
    professor = get_by_identidade_origem(db, identidade)
    if professor is None:
        professor = Professor(
            nome=nome,
            nome_normalizado=normalizar_busca(nome),
            departamento=departamento,
            identidade_origem=identidade,
            identidade_confirmada=False,
        )
        db.add(professor)
        db.flush()
    else:
        professor.nome = nome
        professor.nome_normalizado = normalizar_busca(nome)
        professor.departamento = departamento
    return professor


def listar(db: Session, nome: str | None = None) -> list[Professor]:
    consulta = select(Professor).order_by(Professor.nome, Professor.id)
    if nome is not None:
        termos = normalizar_busca(nome).split()
        if termos:
            consulta = consulta.where(
                and_(*(Professor.nome_normalizado.contains(termo) for termo in termos))
            )
    return list(db.scalars(consulta).all())


def listar_disciplinas(db: Session, professor_id) -> list[Disciplina]:
    consulta = (
        select(Disciplina)
        .join(Turma, Turma.disciplina_id == Disciplina.id)
        .join(
            turmas_professores,
            turmas_professores.c.turma_id == Turma.id,
        )
        .where(
            turmas_professores.c.professor_id == professor_id,
            Turma.ativa.is_(True),
        )
        .distinct()
        .order_by(Disciplina.codigo)
    )
    return list(db.scalars(consulta).all())
