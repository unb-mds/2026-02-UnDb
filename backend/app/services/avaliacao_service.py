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
from app.repositories import avaliacao_repository


MIN_AVALIACOES_EXIBICAO = 3


class RecursoNaoEncontradoError(Exception):
    pass


@dataclass(frozen=True)
class ConsultaAgregada:
    professor_id: UUID
    disciplina_id: UUID
    total_avaliacoes: int
    dados_suficientes: bool
    criterios: ResultadoAgregado | None = None


def consultar_agregado(
    db: Session,
    professor_id: UUID,
    disciplina_id: UUID,
) -> ConsultaAgregada:
    if not avaliacao_repository.professor_existe(db, professor_id):
        raise RecursoNaoEncontradoError("professor nao encontrado")
    if not avaliacao_repository.disciplina_existe(db, disciplina_id):
        raise RecursoNaoEncontradoError("disciplina nao encontrada")

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
        total_avaliacoes=total,
        dados_suficientes=True,
        criterios=criterios,
    )
