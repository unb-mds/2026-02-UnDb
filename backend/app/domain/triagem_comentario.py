"""Sinais locais, sem decisão de publicação nem promessa de detectar todo abuso."""

import json
import re
import unicodedata
from pathlib import Path

LISTA = json.loads((Path(__file__).resolve().parents[1] / "data/termos_moderacao.json").read_text())
VERSAO_LISTA = LISTA["versao"]


def normalizar(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto.casefold()) if unicodedata.category(c) != "Mn"
    )


def categorias_lexicais(texto: str) -> list[str]:
    texto = normalizar(texto)
    categorias = set()
    for item in LISTA["termos"]:
        palavras = [re.escape(p) for p in normalizar(item["termo"]).split()]
        if re.search(r"(?<!\w)" + r"\s+".join(palavras) + r"(?!\w)", texto):
            categorias.add(item["categoria"])
    return sorted(categorias)


# Barreira conservadora: evita enviar contatos, documentos, links e credenciais
# reconhecíveis. Não é anonimização geral: nomes e dados disfarçados podem escapar.
SENSIVEL = re.compile(
    r"[\w.+-]+\s*@\s*[\w.-]+|https?://|www\.|"
    r"(?:\d[\s().+-]*){8,}|"
    r"\b(?:cpf|matricula|senha|password|token|endereco|telefone|whatsapp)\b|"
    r"\bsk-[a-z0-9_-]+",
    re.IGNORECASE,
)


def contem_dados_sensiveis(texto: str, identidades: tuple[str, ...] = ()) -> bool:
    texto = normalizar(texto)
    if SENSIVEL.search(texto):
        return True
    # Se o próprio autor se identificar no texto, não enviar nem fragmentos de nome.
    return any(
        re.search(r"(?<!\w)" + re.escape(parte) + r"(?!\w)", texto)
        for identidade in identidades
        for parte in normalizar(identidade).split()
        if len(parte) > 2
    )
