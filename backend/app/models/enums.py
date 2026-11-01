from enum import Enum


class Dificuldade(str, Enum):
    FACIL = "FACIL"
    MEDIO = "MEDIO"
    DIFICIL = "DIFICIL"


class QualidadeMaterial(str, Enum):
    RUIM = "RUIM"
    MEDIO = "MEDIO"
    BOM = "BOM"


class EstadoComentario(str, Enum):
    PENDENTE = "PENDENTE"
    PUBLICADO = "PUBLICADO"
    SUSPENSO = "SUSPENSO"
    REMOVIDO = "REMOVIDO"
    RETIRADO = "RETIRADO"
    SUBSTITUIDO = "SUBSTITUIDO"
    REJEITADO = "REJEITADO"


class AcaoModeracao(str, Enum):
    APROVAR = "APROVAR"
    REJEITAR = "REJEITAR"
    MANTER = "MANTER"
    RESTAURAR = "RESTAURAR"
    REMOVER = "REMOVER"
