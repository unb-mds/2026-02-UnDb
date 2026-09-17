from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import TypeVar


class Dificuldade(str, Enum):
    FACIL = "FACIL"
    MEDIO = "MEDIO"
    DIFICIL = "DIFICIL"


class QualidadeMaterial(str, Enum):
    RUIM = "RUIM"
    MEDIO = "MEDIO"
    BOM = "BOM"


class ResultadoFactual(str, Enum):
    CONFLITANTE = "CONFLITANTE"


@dataclass(frozen=True)
class AvaliacaoParaAgregacao:
    didatica: int
    dificuldade: Dificuldade
    chamada: bool
    disponibiliza_material: bool
    qualidade_material: QualidadeMaterial | None
    recomenda: bool


@dataclass(frozen=True)
class ResultadoAgregado:
    didatica: float
    dificuldade: Dificuldade
    chamada: bool | ResultadoFactual
    disponibiliza_material: bool | ResultadoFactual
    qualidade_material: QualidadeMaterial | None
    recomenda: int


EnumT = TypeVar("EnumT", bound=Enum)


def _maioria(valores: list[bool]) -> bool | ResultadoFactual:
    positivos = sum(valores)
    negativos = len(valores) - positivos
    if positivos == negativos:
        return ResultadoFactual.CONFLITANTE
    return positivos > negativos


def _moda_com_desempate(
    valores: list[EnumT],
    ordem: dict[EnumT, int],
) -> EnumT:
    contagens = Counter(valores)
    maior_contagem = max(contagens.values())
    empatados = [valor for valor, contagem in contagens.items() if contagem == maior_contagem]
    return max(empatados, key=ordem.__getitem__)


def agregar_avaliacoes(avaliacoes: list[AvaliacaoParaAgregacao]) -> ResultadoAgregado:
    if not avaliacoes:
        raise ValueError("a agregacao exige ao menos uma avaliacao")

    disponibiliza_material = _maioria(
        [avaliacao.disponibiliza_material for avaliacao in avaliacoes]
    )
    qualidades = [
        avaliacao.qualidade_material
        for avaliacao in avaliacoes
        if avaliacao.disponibiliza_material
    ]
    if any(qualidade is None for qualidade in qualidades):
        raise ValueError("avaliacao com material deve informar sua qualidade")

    qualidade_material = None
    if disponibiliza_material is True:
        qualidade_material = _moda_com_desempate(
            [qualidade for qualidade in qualidades if qualidade is not None],
            {
                QualidadeMaterial.RUIM: 1,
                QualidadeMaterial.MEDIO: 2,
                QualidadeMaterial.BOM: 3,
            },
        )

    total = len(avaliacoes)
    media_didatica = (sum(avaliacao.didatica for avaliacao in avaliacoes) / Decimal(total)).quantize(
        Decimal("0.1"),
        rounding=ROUND_HALF_UP,
    )
    percentual_recomendacao = (
        Decimal(sum(avaliacao.recomenda for avaliacao in avaliacoes) * 100) / Decimal(total)
    ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    return ResultadoAgregado(
        didatica=float(media_didatica),
        dificuldade=_moda_com_desempate(
            [avaliacao.dificuldade for avaliacao in avaliacoes],
            {
                Dificuldade.FACIL: 1,
                Dificuldade.MEDIO: 2,
                Dificuldade.DIFICIL: 3,
            },
        ),
        chamada=_maioria([avaliacao.chamada for avaliacao in avaliacoes]),
        disponibiliza_material=disponibiliza_material,
        qualidade_material=qualidade_material,
        recomenda=int(percentual_recomendacao),
    )
