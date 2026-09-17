from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.avaliacoes import (
    AvaliacaoParaAgregacao,
    Dificuldade,
    QualidadeMaterial,
    ResultadoAgregado,
    agregar_avaliacoes,
)
from app.repositories import avaliacao_repository, turma_repository


MIN_AVALIACOES_EXIBICAO = 3


class RecursoNaoEncontradoError(Exception):
    pass


@dataclass(frozen=True)
class ProfessorInstitucional:
    id: UUID
    nome: str
    departamento: str


@dataclass(frozen=True)
class DisciplinaInstitucional:
    id: UUID
    codigo: str
    nome: str
    departamento: str


@dataclass(frozen=True)
class ConsultaAgregada:
    professor_id: UUID
    disciplina_id: UUID
    professor: ProfessorInstitucional
    disciplina: DisciplinaInstitucional
    total_avaliacoes: int
    dados_suficientes: bool
    criterios: ResultadoAgregado | None = None


def consultar_agregado(
    db: Session,
    professor_id: UUID,
    disciplina_id: UUID,
) -> ConsultaAgregada:
    professor = avaliacao_repository.obter_professor(db, professor_id)
    if professor is None:
        raise RecursoNaoEncontradoError("professor nao encontrado")
    disciplina = avaliacao_repository.obter_disciplina(db, disciplina_id)
    if disciplina is None:
        raise RecursoNaoEncontradoError("disciplina nao encontrada")
    if not turma_repository.existe_vinculo_professor_disciplina(
        db, professor_id, disciplina_id
    ):
        raise RecursoNaoEncontradoError(
            "professor nao possui vinculo com a disciplina"
        )

    professor_institucional = ProfessorInstitucional(
        id=professor.id,
        nome=professor.nome,
        departamento=professor.departamento,
    )
    disciplina_institucional = DisciplinaInstitucional(
        id=disciplina.id,
        codigo=disciplina.codigo,
        nome=disciplina.nome,
        departamento=disciplina.departamento,
    )

    registros = avaliacao_repository.listar_por_professor_e_disciplina(
        db,
        professor_id,
        disciplina_id,
    )
    total = len(registros)
    if total < MIN_AVALIACOES_EXIBICAO:
        return ConsultaAgregada(
            professor_id=professor_id,
            disciplina_id=disciplina_id,
            professor=professor_institucional,
            disciplina=disciplina_institucional,
            total_avaliacoes=total,
            dados_suficientes=False,
        )

    criterios = agregar_avaliacoes(
        [
            AvaliacaoParaAgregacao(
                didatica=registro.didatica,
                dificuldade=Dificuldade(registro.dificuldade.value),
                chamada=registro.chamada,
                disponibiliza_material=registro.disponibiliza_material,
                qualidade_material=(
                    QualidadeMaterial(registro.qualidade_material.value)
                    if registro.qualidade_material is not None
                    else None
                ),
                recomenda=registro.recomenda,
            )
            for registro in registros
        ]
    )
    return ConsultaAgregada(
        professor_id=professor_id,
        disciplina_id=disciplina_id,
        professor=professor_institucional,
        disciplina=disciplina_institucional,
        total_avaliacoes=total,
        dados_suficientes=True,
        criterios=criterios,
    )
