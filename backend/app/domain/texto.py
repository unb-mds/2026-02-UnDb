import unicodedata


def normalizar_busca(valor: str) -> str:
    """Normaliza texto institucional sem depender da extensão unaccent do banco."""
    decomposed = unicodedata.normalize("NFKD", valor)
    sem_acentos = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(sem_acentos.casefold().split())
