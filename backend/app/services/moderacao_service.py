"""Human review of comment versions; decisions never copy discarded content."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import AcaoModeracao, EstadoComentario
from app.models.usuario import Usuario
from app.repositories import comentario_repository, moderacao_repository
from app.schemas.moderacao import ComentarioModeracaoResponse, IdentidadeInterna

RETENCAO = timedelta(days=7)


class ModeracaoError(Exception):
    def __init__(self, status_code: int, mensagem: str):
        self.status_code = status_code
        super().__init__(mensagem)


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def autorizar(usuario: Usuario) -> None:
    if not usuario.email_confirmado or not usuario.moderador:
        raise ModeracaoError(403, "permissao de moderador confirmado necessaria")


def representar(versao) -> ComentarioModeracaoResponse:
    return ComentarioModeracaoResponse(
        id=versao.id, texto=versao.texto, estado=versao.estado,
        autor=IdentidadeInterna.model_validate(versao.avaliacao.usuario),
        substitui_id=versao.substitui_id, created_at=versao.created_at,
    )


def listar(db: Session, usuario: Usuario, estado: EstadoComentario | None = None):
    autorizar(usuario)
    moderacao_repository.descartar_vencidos(db, agora_utc())
    resultado = [representar(v) for v in moderacao_repository.listar_fila(db, estado)]
    db.commit()
    return resultado


def consultar(db: Session, usuario: Usuario, versao_id: UUID):
    autorizar(usuario)
    moderacao_repository.descartar_vencidos(db, agora_utc())
    versao = comentario_repository.obter_por_id(db, versao_id)
    if versao is None:
        raise ModeracaoError(404, "comentario nao encontrado")
    resultado = representar(versao)
    db.commit()
    return resultado


def decisoes(db: Session, usuario: Usuario, versao_id: UUID):
    autorizar(usuario)
    moderacao_repository.descartar_vencidos(db, agora_utc())
    resultado = moderacao_repository.listar_decisoes(db, versao_id)
    db.commit()
    return resultado


def decidir(db: Session, usuario: Usuario, versao_id: UUID, dados):
    autorizar(usuario)
    try:
        versao = comentario_repository.obter_bloqueado(db, versao_id)
        if versao is None:
            raise ModeracaoError(404, "comentario nao encontrado")
        if versao.avaliacao.usuario_id == usuario.id:
            raise ModeracaoError(403, "moderador impedido por autoria do comentario")
        anterior = versao.estado
        if anterior != EstadoComentario.PENDENTE or dados.acao not in (AcaoModeracao.APROVAR, AcaoModeracao.REJEITAR):
            raise ModeracaoError(409, "acao incompativel com estado atual")
        if dados.acao == AcaoModeracao.APROVAR:
            atual = comentario_repository.obter_atual_por_avaliacao(db, versao.avaliacao_id)
            if atual is not None:
                atual.estado = EstadoComentario.SUBSTITUIDO
                atual.texto = None
                atual.descartar_em = None
            versao.estado = EstadoComentario.PUBLICADO
        else:
            versao.estado = EstadoComentario.REJEITADO
            versao.texto = None
        agora = agora_utc()
        versao.updated_at = agora
        decisao = moderacao_repository.registrar_decisao(
            db, comentario_versao_id=versao.id, moderador_id=usuario.id,
            acao=dados.acao.value, motivo=dados.motivo,
            estado_anterior=anterior.value, estado_posterior=versao.estado.value,
            created_at=agora, descartar_em=agora + RETENCAO,
        )
        db.commit()
        return decisao
    except Exception:
        db.rollback()
        raise
