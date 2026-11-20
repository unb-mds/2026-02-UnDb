"""Injeção explícita da proteção HTTP; chamadas administrativas fora do HTTP não a usam."""

from typing import Annotated

from fastapi import Depends

from app.core.dependencia_limite_abuso import obter_limitador
from app.services.auth_abuso_service import ProtecaoAuth
from app.services.limite_abuso_service import LimitadorAbuso


def obter_protecao_auth(
    limitador: Annotated[LimitadorAbuso, Depends(obter_limitador)],
) -> ProtecaoAuth:
    return ProtecaoAuth(limitador)
