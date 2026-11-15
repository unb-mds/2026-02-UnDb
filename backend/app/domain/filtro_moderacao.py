"""Complemento lexical opcional; nunca altera o texto nem decide publicação."""

import re
import unicodedata

from app.domain.texto import normalizar_busca
from app.domain.triagem_comentario import LISTA, categorias_lexicais

VERSAO_FILTRO_ATUAL = "239-lexical-v1"
VERSAO_DISFARCES = "252-disfarces-v1"
INVISIVEIS = str.maketrans("", "", "\u200b\u200c\u200d\ufeff\u2060")
# Mapa explícito e limitado. Não é uma implementação geral de UTS #39.
HOMOGLIFOS = str.maketrans({"а": "a", "е": "e", "о": "o", "і": "i", "с": "c"})
SEPARADORES = r"[\s.\-_*]"


class FiltroIndisponivel(Exception):
    pass


def normalizar_disfarces(texto: str) -> str:
    # Mesma técnica NFKD da busca, mas sem compactar espaços: isso apagaria
    # o limite de três separadores entre posições antes de verificar o padrão.
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(c for c in decomposto if not unicodedata.combining(c))
    return sem_acentos.casefold().translate(INVISIVEIS).translate(HOMOGLIFOS)


def _padrao(termo: str) -> re.Pattern:
    partes = []
    for parte in re.split(r"(\s+|-)", normalizar_busca(termo)):
        if not parte:
            continue
        if parte.isspace():
            partes.append(SEPARADORES + "{1,3}")
        elif parte == "-":
            # Hífen que já pertence ao termo não acumula separadores opcionais
            # dos dois lados (o que permitiria ultrapassar o limite de três).
            partes.append(r"\-{1,3}")
        else:
            letras = [re.escape(c) + "{1,4}" for c in parte]
            partes.append((SEPARADORES + "{0,3}").join(letras))
    corpo = "".join(partes)
    return re.compile(r"(?<!\w)" + corpo + r"(?!\w)")


# Compilação única da lista versionada, sem cache de comentários/autores.
PADROES = tuple((_padrao(item["termo"]), item["categoria"]) for item in LISTA["termos"])


def categorias_para_triagem(texto: str, *, disfarces_ativos: bool = False) -> list[str]:
    try:
        # A união é obrigatória: normalizar_busca preserva Mn de classe zero,
        # como U+FE0F/U+034F, que o filtro vigente já remove e detecta.
        categorias = set(categorias_lexicais(texto))
        if disfarces_ativos:
            derivado = normalizar_disfarces(texto)
            categorias.update(categoria for padrao, categoria in PADROES if padrao.search(derivado))
        return sorted(categorias)
    except Exception:
        # Falha não pode virar ausência de sinal nem expor o texto em erro/log.
        raise FiltroIndisponivel("filtro indisponivel; manter revisao humana") from None


def versao_filtro(disfarces_ativos: bool) -> str:
    return VERSAO_DISFARCES if disfarces_ativos else VERSAO_FILTRO_ATUAL
