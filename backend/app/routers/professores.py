from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.avaliacao import (
    AvaliacaoAgregadaInsuficienteResponse,
    AvaliacaoAgregadaResponse,
    AvaliacaoAgregadaSuficienteResponse,
)
from app.services import avaliacao_service


router = APIRouter(prefix="/api/professores", tags=["professores"])


@router.get(
    "/{professor_id}/disciplinas/{disciplina_id}",
    response_model=AvaliacaoAgregadaResponse,
)
def consultar_avaliacoes_professor_disciplina(
    professor_id: UUID,
    disciplina_id: UUID,
    session: Annotated[Session, Depends(get_db)],
) -> AvaliacaoAgregadaResponse:
    try:
        consulta = avaliacao_service.consultar_agregado(
            session,
            professor_id,
            disciplina_id,
        )
    except avaliacao_service.RecursoNaoEncontradoError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    if consulta.criterios is None:
        return AvaliacaoAgregadaInsuficienteResponse(
            professor_id=consulta.professor_id,
            disciplina_id=consulta.disciplina_id,
            total_avaliacoes=consulta.total_avaliacoes,
            dados_suficientes=False,
        )

    return AvaliacaoAgregadaSuficienteResponse(
        professor_id=consulta.professor_id,
        disciplina_id=consulta.disciplina_id,
        total_avaliacoes=consulta.total_avaliacoes,
        dados_suficientes=True,
        didatica=consulta.criterios.didatica,
        dificuldade=consulta.criterios.dificuldade,
        chamada=consulta.criterios.chamada,
        disponibiliza_material=consulta.criterios.disponibiliza_material,
        qualidade_material=consulta.criterios.qualidade_material,
        recomenda=consulta.criterios.recomenda,
    )
