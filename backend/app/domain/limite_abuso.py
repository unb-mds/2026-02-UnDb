"""Contratos e cálculo puro do limitador; não conhece HTTP, ORM ou identidade real."""

import re
from dataclasses import dataclass
from enum import StrEnum


class ModoLimite(StrEnum):
    ENFORCE = "enforce"
    OBSERVE = "observe"


class FalhaLimite(StrEnum):
    FECHAR = "fechar"
    SEGUIR = "seguir"
    LOCAL = "local"


class MotivoLimite(StrEnum):
    PERMITIDO = "permitido"
    IDENTIDADE = "limite_identidade"
    GLOBAL = "limite_global"
    ATRASO = "atraso"
    INDISPONIVEL = "indisponivel"


@dataclass(frozen=True)
class PoliticaAbuso:
    operacao: str
    quantidade: int
    janela_segundos: int
    quantidade_global: int
    janela_global_segundos: int
    modo: ModoLimite = ModoLimite.ENFORCE
    falha: FalhaLimite = FalhaLimite.FECHAR
    atraso_apos: int = 0
    atraso_inicial_segundos: int = 0
    atraso_maximo_segundos: int = 0

    def __post_init__(self):
        if not re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", self.operacao):
            raise ValueError("Operação inválida na configuração do limitador.")
        for valor in (
            self.quantidade,
            self.janela_segundos,
            self.quantidade_global,
            self.janela_global_segundos,
        ):
            if type(valor) is not int or valor <= 0:
                raise ValueError("Limites e janelas devem ser inteiros positivos.")
        # Strings vindas do JSON também são validadas/congeladas como enums.
        object.__setattr__(self, "modo", ModoLimite(self.modo))
        object.__setattr__(self, "falha", FalhaLimite(self.falha))
        for valor in (self.atraso_apos, self.atraso_inicial_segundos, self.atraso_maximo_segundos):
            if type(valor) is not int or valor < 0:
                raise ValueError("Configuração de atraso inválida.")
        if self.atraso_inicial_segundos > self.atraso_maximo_segundos:
            raise ValueError("Atraso inicial maior que o máximo.")


@dataclass(frozen=True)
class ResultadoLimite:
    permitido: bool
    retry_after: int
    motivo: MotivoLimite
    excedido: bool = False
    indisponivel: bool = False
    acao_falha: FalhaLimite = FalhaLimite.FECHAR


def atraso_progressivo(quantidade: int, politica: PoliticaAbuso) -> int:
    if not politica.atraso_inicial_segundos or quantidade < politica.atraso_apos:
        return 0
    # Evita exponenciação não limitada mesmo após muitas tentativas.
    teto_expoente = politica.atraso_maximo_segundos.bit_length()
    expoente = min(quantidade - politica.atraso_apos, teto_expoente)
    return min(politica.atraso_inicial_segundos * (2**expoente), politica.atraso_maximo_segundos)
