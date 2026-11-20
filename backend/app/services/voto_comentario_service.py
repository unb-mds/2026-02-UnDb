from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import EstadoComentario
from app.models.usuario import Usuario
from app.repositories import comentario_repository, voto_comentario_repository, retencao_repository


class VotoComentarioError(Exception):
    def __init__(self, status_code: int, mensagem: str):
        self.status_code = status_code
        super().__init__(mensagem)


def _publicado(db: Session, versao_id: UUID):
    # Mesmo lock e ordem usados por retirada, moderação e substituição.
    versao = comentario_repository.obter_bloqueado(db, versao_id)
    if versao is None or versao.estado != EstadoComentario.PUBLICADO or versao.texto is None:
        raise VotoComentarioError(404, "comentario indisponivel")
    return versao


def consultar(db: Session, versao_id: UUID, usuario: Usuario | None):
    try:
        _publicado(db, versao_id)
        resultado = voto_comentario_repository.resumir(
            db, versao_id, usuario.id if usuario else None
        )
        db.commit()
        return resultado
    except Exception:
        db.rollback()
        raise


def definir(db: Session, versao_id: UUID, usuario: Usuario, voto: str | None):
    try:
        conta = retencao_repository.bloquear_conta(db, usuario.id)
        if conta is None or conta.excluido_em is not None:
            raise VotoComentarioError(401, "Sessão inválida.")
        if not conta.email_confirmado:
            raise VotoComentarioError(403, "Confirme seu e-mail para votar.")
        versao = _publicado(db, versao_id)
        if versao.avaliacao.usuario_id == usuario.id:
            raise VotoComentarioError(403, "nao e permitido votar no proprio comentario")
        voto_comentario_repository.definir(db, versao_id, usuario.id, voto)
        resultado = voto_comentario_repository.resumir(db, versao_id, usuario.id)
        db.commit()
        return resultado
    except Exception:
        db.rollback()
        raise
