"""Human review of comment versions; decisions never copy discarded content."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import AcaoModeracao, EstadoComentario
from app.models.usuario import Usuario
from app.repositories import comentario_repository, moderacao_repository, denuncia_repository
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
        if denuncia_repository.existe_da_conta(db, versao.id, usuario.id):
            raise ModeracaoError(403, "moderador impedido por denuncia propria")
        anterior = versao.estado
        abertas = denuncia_repository.listar(db, versao.id)
        permitidas = {
            EstadoComentario.PENDENTE: (AcaoModeracao.APROVAR, AcaoModeracao.REJEITAR),
            EstadoComentario.PUBLICADO: (AcaoModeracao.MANTER, AcaoModeracao.REMOVER) if abertas else (),
            EstadoComentario.SUSPENSO: (AcaoModeracao.RESTAURAR, AcaoModeracao.REMOVER),
        }
        if dados.acao not in permitidas.get(anterior, ()):
            raise ModeracaoError(409, "acao incompativel com estado atual")
        agora = agora_utc()
        if dados.acao == AcaoModeracao.APROVAR:
            atual = comentario_repository.obter_atual_por_avaliacao(db, versao.avaliacao_id)
            if atual is not None:
                if denuncia_repository.existe_da_conta(db, atual.id, usuario.id):
                    raise ModeracaoError(403, "moderador impedido por denuncia propria da versao substituida")
                denuncia_repository.encerrar(db, atual.id, "VERSAO_SUBSTITUIDA")
                atual.estado = EstadoComentario.SUBSTITUIDO
                atual.texto = None
                atual.descartar_em = None
                atual.updated_at = agora
            versao.estado = EstadoComentario.PUBLICADO
        elif dados.acao == AcaoModeracao.REJEITAR:
            versao.estado = EstadoComentario.REJEITADO
            versao.texto = None
        else:
            if dados.acao == AcaoModeracao.REMOVER:
                if abertas:
                    denuncia_repository.agradecer(db, versao.id, "REMOCAO", agora)
                versao.estado = EstadoComentario.REMOVIDO
                versao.descartar_em = agora + RETENCAO
            else:
                versao.estado = EstadoComentario.PUBLICADO
            denuncia_repository.encerrar(db, versao.id, {
                AcaoModeracao.REMOVER: "REMOVIDO", AcaoModeracao.MANTER: "MANTIDO",
                AcaoModeracao.RESTAURAR: "RESTAURADO",
            }[dados.acao])
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
