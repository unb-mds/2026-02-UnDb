"""Isolamento explícito do limitador nos testes legados de outros contratos."""

from unittest.mock import Mock

from app.domain.limite_abuso import MotivoLimite, ResultadoLimite
from app.services.auth_abuso_service import ProtecaoAuth
from app.services.limite_abuso_service import LimitadorAbuso


def protecao_permitida() -> ProtecaoAuth:
    limitador = Mock(spec=LimitadorAbuso)
    limitador.consumir.return_value = ResultadoLimite(True, 0, MotivoLimite.PERMITIDO)
    limitador.reiniciar_identidade.return_value = True
    limitador.falha.return_value = ResultadoLimite(
        False, 5, MotivoLimite.INDISPONIVEL, indisponivel=True
    )
    return ProtecaoAuth(limitador)
