"""Dependência reutilizável; nenhum router de produto a utiliza no bloco 1."""

from collections.abc import Callable

from fastapi import Depends

from app.core.limite_abuso import IdentidadeAbuso
from app.domain.limite_abuso import FalhaLimite, ResultadoLimite
from app.services.limite_abuso_service import LimitadorAbuso, carregar_politica


class AbusoExcedido(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = max(1, retry_after)


class LimitadorIndisponivel(AbusoExcedido):
    pass


def obter_limitador() -> LimitadorAbuso:
    return LimitadorAbuso()


def _somente_global() -> None:
    return None


def exigir_limite(
    operacao: str,
    resolver_identidade: Callable = _somente_global,
    fallback_local: Callable[[], ResultadoLimite] | None = None,
):
    def dependencia(
        identidade: IdentidadeAbuso | None = Depends(resolver_identidade),
        limitador: LimitadorAbuso = Depends(obter_limitador),
    ) -> ResultadoLimite:
        try:
            politica = carregar_politica(operacao)
        except (KeyError, TypeError, ValueError):
            resultado = limitador.falha()
        else:
            resultado = limitador.consumir(politica, identidade)
        if resultado.indisponivel and resultado.acao_falha == FalhaLimite.LOCAL and fallback_local:
            resultado = fallback_local()
        if not resultado.permitido:
            erro = LimitadorIndisponivel if resultado.indisponivel else AbusoExcedido
            raise erro(resultado.retry_after)
        return resultado

    return dependencia
