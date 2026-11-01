from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import EstadoComentario
from app.repositories import comentario_repository, denuncia_repository
from app.schemas.denuncia import ConfirmacaoDenuncia, DenunciaInterna, DenunciasDaVersao
from app.schemas.moderacao import IdentidadeInterna
from app.services import moderacao_service
from app.services.moderacao_service import ModeracaoError, agora_utc

LIMIAR_SUSPENSAO = 50


def registrar(db: Session, versao_id: UUID, usuario, dados) -> ConfirmacaoDenuncia:
    try:
        versao = comentario_repository.obter_bloqueado(db, versao_id)
        if versao is None or versao.estado != EstadoComentario.PUBLICADO:
            raise ModeracaoError(404, "versao indisponivel para denuncia")
        usuario_id = usuario.id if usuario is not None else None
        if usuario_id is not None and denuncia_repository.existe_da_conta(db, versao_id, usuario_id):
            raise ModeracaoError(409, "ja existe denuncia aberta desta conta para a versao")
        agora = agora_utc()
        denuncia_repository.criar(db, versao_id, usuario_id, dados.motivo, agora)
        if denuncia_repository.contar_contas(db, versao_id) >= LIMIAR_SUSPENSAO:
            versao.estado = EstadoComentario.SUSPENSO
            versao.updated_at = agora
            denuncia_repository.agradecer(db, versao_id, "SUSPENSAO", agora)
        db.commit()
        return ConfirmacaoDenuncia()
    except Exception:
        db.rollback()
        raise


def consultar(db: Session, usuario, versao_id: UUID) -> DenunciasDaVersao:
    moderacao_service.autorizar(usuario)
    if comentario_repository.obter_por_id(db, versao_id) is None:
        raise ModeracaoError(404, "comentario nao encontrado")
    autenticadas, visitantes = [], []
    for denuncia in denuncia_repository.listar(db, versao_id):
        item = DenunciaInterna(
            id=denuncia.id, comentario_versao_id=denuncia.comentario_versao_id,
            motivo=denuncia.motivo, created_at=denuncia.created_at,
            denunciante=IdentidadeInterna.model_validate(denuncia.denunciante) if denuncia.denunciante else None,
        )
        (autenticadas if denuncia.denunciante_id is not None else visitantes).append(item)
    return DenunciasDaVersao(autenticadas=autenticadas, visitantes=visitantes,
                             contas_distintas=denuncia_repository.contar_contas(db, versao_id),
                             total_visitantes=len(visitantes))


def listar_agradecimentos(db: Session, usuario):
    return denuncia_repository.listar_agradecimentos(db, usuario.id)


def confirmar_exibicao(db: Session, usuario, mensagem_id: UUID) -> None:
    if not denuncia_repository.apagar_agradecimento(db, usuario.id, mensagem_id):
        raise ModeracaoError(404, "mensagem nao encontrada")
    db.commit()
