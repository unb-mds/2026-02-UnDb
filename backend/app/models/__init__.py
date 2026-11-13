from app.models.avaliacao import Avaliacao
from app.models.comentario_versao import ComentarioVersao
from app.models.disciplina import Disciplina
from app.models.importacao_execucao import ImportacaoExecucao
from app.models.professor_correspondencia import ProfessorCorrespondencia
from app.models.professor import Professor
from app.models.sessao_usuario import SessaoUsuario
from app.models.turma import Turma
from app.models.token_confirmacao_email import TokenConfirmacaoEmail
from app.models.unidade import Unidade
from app.models.usuario import Usuario
from app.models.decisao_moderacao import DecisaoModeracao
from app.models.denuncia import Denuncia, Agradecimento

__all__ = [
    "IdentidadeDocente",
    "IdentidadeLocal",
    "PendenciaIdentidade",
    "DecisaoIdentidade",
    "Avaliacao",
    "ComentarioVersao",
    "Disciplina",
    "ImportacaoExecucao",
    "Professor",
    "ProfessorCorrespondencia",
    "SessaoUsuario",
    "Turma",
    "TokenConfirmacaoEmail",
    "Unidade",
    "Usuario",
    "DecisaoModeracao",
    "Denuncia",
    "Agradecimento",
]

from app.models.identidade_docente import IdentidadeDocente, PendenciaIdentidade, DecisaoIdentidade
from app.models.identidade_docente import IdentidadeLocal
