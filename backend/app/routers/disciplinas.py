from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.avaliacao import (
    AvaliacaoAgregadaInsuficienteResponse,
    AvaliacaoAgregadaResponse,
    AvaliacaoAgregadaSuficienteResponse,
    ComparacaoProfessoresResponse,
)
from app.services import avaliacao_service


router = APIRouter(prefix="/api/disciplinas", tags=["disciplinas"])


@router.get("/{disciplina_id}/professores", response_model=ComparacaoProfessoresResponse)
def comparar_professores_da_disciplina(
    disciplina_id: UUID,
    session: Annotated[Session, Depends(get_db)],
    ordenar_por: Annotated[Literal["recomendacao"], Query()],
) -> ComparacaoProfessoresResponse:
    try:
        comparacao = avaliacao_service.comparar_professores(session, disciplina_id)
    except avaliacao_service.RecursoNaoEncontradoError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    return ComparacaoProfessoresResponse(
        disciplina=comparacao.disciplina,
        professores=[_para_resposta(resultado) for resultado in comparacao.professores],
    )


def _para_resposta(consulta: avaliacao_service.ConsultaAgregada) -> AvaliacaoAgregadaResponse:
    if consulta.criterios is None:
        return AvaliacaoAgregadaInsuficienteResponse(
            professor_id=consulta.professor_id,
            disciplina_id=consulta.disciplina_id,
            professor=consulta.professor,
            disciplina=consulta.disciplina,
            total_avaliacoes=consulta.total_avaliacoes,
            dados_suficientes=False,
        )

    return AvaliacaoAgregadaSuficienteResponse(
        professor_id=consulta.professor_id,
        disciplina_id=consulta.disciplina_id,
        professor=consulta.professor,
        disciplina=consulta.disciplina,
        total_avaliacoes=consulta.total_avaliacoes,
        dados_suficientes=True,
        didatica=consulta.criterios.didatica,
        dificuldade=consulta.criterios.dificuldade,
        chamada=consulta.criterios.chamada,
        disponibiliza_material=consulta.criterios.disponibiliza_material,
        qualidade_material=consulta.criterios.qualidade_material,
        recomenda=consulta.criterios.recomenda,
    )
