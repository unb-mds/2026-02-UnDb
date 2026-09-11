from app.models.departamento import Departamento
from app.models.professor import Professor
from app.models.disciplina import Disciplina, estuda
from app.models.turma import Turma
from app.models.usuario import Usuario
from app.models.avaliacao import Avaliacao

__all__ = [
    "Departamento",
    "Professor",
    "Disciplina",
    "Turma",
    "Usuario",
    "Avaliacao",
    "estuda",
]