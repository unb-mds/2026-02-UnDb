from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum


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


@dataclass(frozen=True)
class ContagensAvaliacoes:
    total: int
    soma_didatica: int
    dificuldades: tuple[int, int, int]
    chamadas: int
    materiais: int
    qualidades: tuple[int, int, int]
    recomendacoes: int


def _maioria(positivos: int, total: int) -> bool | ResultadoFactual:
    negativos = total - positivos
    if positivos == negativos:
        return ResultadoFactual.CONFLITANTE
    return positivos > negativos


def _indice_da_moda(contagens: tuple[int, int, int]) -> int:
    return max(range(len(contagens)), key=lambda indice: (contagens[indice], indice))


def agregar_contagens(contagens: ContagensAvaliacoes) -> ResultadoAgregado:
    total = contagens.total
    if not total:
        raise ValueError("a agregacao exige ao menos uma avaliacao")

    disponibiliza_material = _maioria(contagens.materiais, total)
    if sum(contagens.qualidades) != contagens.materiais:
        raise ValueError("avaliacao com material deve informar sua qualidade")

    qualidade_material = None
    if disponibiliza_material is True:
        qualidade_material = tuple(QualidadeMaterial)[_indice_da_moda(contagens.qualidades)]

    dificuldade = tuple(Dificuldade)[_indice_da_moda(contagens.dificuldades)]
    media_didatica = (Decimal(contagens.soma_didatica) / total).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )
    percentual_recomendacao = (Decimal(contagens.recomendacoes * 100) / total).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )

    return ResultadoAgregado(
        didatica=float(media_didatica),
        dificuldade=dificuldade,
        chamada=_maioria(contagens.chamadas, total),
        disponibiliza_material=disponibiliza_material,
        qualidade_material=qualidade_material,
        recomenda=int(percentual_recomendacao),
    )


def agregar_avaliacoes(avaliacoes: list[AvaliacaoParaAgregacao]) -> ResultadoAgregado:
    dificuldades = Counter(avaliacao.dificuldade for avaliacao in avaliacoes)
    qualidades = Counter(
        avaliacao.qualidade_material for avaliacao in avaliacoes if avaliacao.disponibiliza_material
    )
    return agregar_contagens(
        ContagensAvaliacoes(
            total=len(avaliacoes),
            soma_didatica=sum(avaliacao.didatica for avaliacao in avaliacoes),
            dificuldades=(
                dificuldades[Dificuldade.FACIL],
                dificuldades[Dificuldade.MEDIO],
                dificuldades[Dificuldade.DIFICIL],
            ),
            chamadas=sum(avaliacao.chamada for avaliacao in avaliacoes),
            materiais=sum(avaliacao.disponibiliza_material for avaliacao in avaliacoes),
            qualidades=(
                qualidades[QualidadeMaterial.RUIM],
                qualidades[QualidadeMaterial.MEDIO],
                qualidades[QualidadeMaterial.BOM],
            ),
            recomendacoes=sum(avaliacao.recomenda for avaliacao in avaliacoes),
        )
    )
