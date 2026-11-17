from app.models.voto_comentario import VotoComentario
from app.models.avaliacao import Avaliacao
from app.models.contador_abuso import ContadorAbuso
from app.models.solicitacao_titular import SolicitacaoTitular, EventoSolicitacao
from app.models.comentario_versao import ComentarioVersao
from app.models.disciplina import Disciplina
from app.models.importacao_execucao import ImportacaoExecucao
from app.models.professor_correspondencia import ProfessorCorrespondencia
from app.models.professor import Professor
from app.models.sessao_usuario import SessaoUsuario
from app.models.turma import Turma
from app.models.token_confirmacao_email import TokenConfirmacaoEmail
from app.models.unidade import Unidade
from app.models.token_recuperacao_senha import TokenRecuperacaoSenha
from app.models.usuario import Usuario
from app.models.decisao_moderacao import DecisaoModeracao
from app.models.denuncia import Denuncia, Agradecimento

__all__ = [
    "ContadorAbuso",
    "VotoComentario",
    "SolicitacaoTitular",
    "EventoSolicitacao",
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
    "RegistroAcesso",
    "Turma",
    "TokenConfirmacaoEmail",
    "Unidade",
    "TokenRecuperacaoSenha",
    "Usuario",
    "DecisaoModeracao",
    "Denuncia",
    "Agradecimento",
]

from app.models.identidade_docente import IdentidadeDocente, PendenciaIdentidade, DecisaoIdentidade
from app.models.identidade_docente import IdentidadeLocal

from app.models.registro_acesso import RegistroAcesso
