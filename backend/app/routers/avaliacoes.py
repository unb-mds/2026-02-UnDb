from fastapi import APIRouter

from app.schemas.avaliacao import AvaliacaoRead

router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])


@router.get("/", response_model=list[AvaliacaoRead])
def listar_avaliacoes() -> list[AvaliacaoRead]:
    # A persistencia sera conectada pelo repositorio e pelo servico da feature.
    return []
