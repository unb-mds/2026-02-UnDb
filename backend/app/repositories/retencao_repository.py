"""Exclusão e purga transacionais; nenhum conteúdo é copiado para logs."""

from sqlalchemy import select, update, delete
from app.models import (
    Usuario,
    Avaliacao,
    ComentarioVersao,
    DecisaoModeracao,
    Denuncia,
    Agradecimento,
    SessaoUsuario,
    TokenConfirmacaoEmail,
    TokenRecuperacaoSenha,
)
from app.models.contador_abuso import ContadorAbuso
from app.models.enums import EstadoComentario


def bloquear_conta(db, id):
    return db.scalar(
        select(Usuario)
        .where(Usuario.id == id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )


def bloquear_avaliacao(db, id):
    return db.scalar(
        select(Avaliacao)
        .where(Avaliacao.id == id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )


def avaliacoes_da_conta(db, id):
    return list(
        db.scalars(
            select(Avaliacao)
            .where(Avaliacao.usuario_id == id)
            .order_by(Avaliacao.id)
            .with_for_update()
        )
    )


def ocultar(db, avaliacao, agora, prazo):
    if avaliacao.excluido_em is None:
        avaliacao.excluido_em, avaliacao.purgar_em = agora, agora + prazo
    # Todas as versões, inclusive substituídas, desaparecem junto da avaliação.
    db.execute(
        update(ComentarioVersao)
        .where(ComentarioVersao.avaliacao_id == avaliacao.id)
        .values(estado=EstadoComentario.RETIRADO, descartar_em=avaliacao.purgar_em)
    )
    db.execute(
        update(Denuncia)
        .where(
            Denuncia.comentario_versao_id.in_(
                select(ComentarioVersao.id).where(ComentarioVersao.avaliacao_id == avaliacao.id)
            ),
            Denuncia.encerrada_em.is_(None),
        )
        .values(encerrada_em=agora)
    )


def remover_credenciais(db, id):
    for modelo in (SessaoUsuario, TokenConfirmacaoEmail, TokenRecuperacaoSenha, Agradecimento):
        db.execute(delete(modelo).where(modelo.usuario_id == id))


def apagar_comentarios(db, ids):
    if not ids:
        return
    # FKs preservam integridade; cascata explícita no mesmo commit funciona também
    # em bancos existentes sem ON DELETE CASCADE. Ninguém pode apagar só o pai.
    for modelo in (Denuncia, Agradecimento, DecisaoModeracao):
        db.execute(delete(modelo).where(modelo.comentario_versao_id.in_(ids)))
    db.execute(
        update(ComentarioVersao)
        .where(ComentarioVersao.substitui_id.in_(ids))
        .values(substitui_id=None)
    )
    db.execute(delete(ComentarioVersao).where(ComentarioVersao.id.in_(ids)))


def purgar_conteudo(db, agora, lote):
    avaliacoes = list(
        db.scalars(
            select(Avaliacao.id)
            .where(Avaliacao.purgar_em <= agora)
            .order_by(Avaliacao.id)
            .limit(lote)
            .with_for_update(skip_locked=True)
        )
    )
    for id in avaliacoes:
        ids = list(
            db.scalars(select(ComentarioVersao.id).where(ComentarioVersao.avaliacao_id == id))
        )
        apagar_comentarios(db, ids)
        db.execute(delete(Avaliacao).where(Avaliacao.id == id))
    comentarios = list(
        db.scalars(
            select(ComentarioVersao.id)
            .where(
                ComentarioVersao.descartar_em <= agora,
                ComentarioVersao.estado.in_(
                    (
                        EstadoComentario.RETIRADO,
                        EstadoComentario.REMOVIDO,
                        EstadoComentario.SUBSTITUIDO,
                    )
                ),
            )
            .order_by(ComentarioVersao.id)
            .limit(lote)
            .with_for_update(skip_locked=True)
        )
    )
    apagar_comentarios(db, comentarios)
    return len(avaliacoes) + len(comentarios)


def purgar_expirados(db, agora, lote):
    from app.repositories.registro_acesso_repository import purgar

    total = purgar_conteudo(db, agora, lote) + purgar(db, agora, lote)
    for modelo in (SessaoUsuario, TokenConfirmacaoEmail, TokenRecuperacaoSenha):
        ids = select(modelo.id).where(modelo.expires_at <= agora).limit(lote)
        total += db.execute(delete(modelo).where(modelo.id.in_(ids))).rowcount
    chaves = list(
        db.execute(
            select(ContadorAbuso.operacao, ContadorAbuso.chave)
            .where(ContadorAbuso.expira_em <= agora)
            .limit(lote)
            .with_for_update(skip_locked=True)
        )
    )
    for operacao, chave in chaves:
        total += db.execute(
            delete(ContadorAbuso).where(
                ContadorAbuso.operacao == operacao, ContadorAbuso.chave == chave
            )
        ).rowcount
    return total
