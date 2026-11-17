"""Decisão B do PO: exclusão imediata e descarte após janela configurada."""

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from app.core import config
from app.repositories import retencao_repository as repo


def agora_utc():
    return datetime.now(timezone.utc)


def prazo():
    if config.RETENCAO_CONTEUDO_DIAS <= 0:
        raise ValueError("Janela de retenção inválida.")
    return timedelta(days=config.RETENCAO_CONTEUDO_DIAS)


def excluir_conta(db, usuario):
    try:
        conta = repo.bloquear_conta(db, usuario.id)
        if conta is None:
            raise HTTPException(404, "Conta não encontrada.")
        agora = agora_utc()
        if conta.excluido_em is None:
            conta.excluido_em = agora
        conta.nome, conta.password_hash = "", None
        conta.termos_versao, conta.termos_ciencia_em = None, None
        conta.email_confirmado = conta.moderador = conta.reconciliador = False
        for avaliacao in repo.avaliacoes_da_conta(db, conta.id):
            repo.ocultar(db, avaliacao, agora, prazo())
        repo.remover_credenciais(db, conta.id)
        db.commit()
    except Exception:
        db.rollback()
        raise


def excluir_avaliacao(db, usuario, id, moderacao=False):
    try:
        conta = repo.bloquear_conta(db, usuario.id)
        if conta is None or conta.excluido_em is not None:
            raise HTTPException(401, "Sessão inválida.")
        if moderacao and (not conta.moderador or not conta.email_confirmado):
            raise HTTPException(403, "Permissão de moderador necessária.")
        item = repo.bloquear_avaliacao(db, id)
        if item is None or (not moderacao and item.usuario_id != conta.id):
            raise HTTPException(404, "Avaliação não encontrada.")
        repo.ocultar(db, item, agora_utc(), prazo())
        db.commit()
    except Exception:
        db.rollback()
        raise


def purgar(db):
    if config.PURGA_LOTE <= 0:
        raise ValueError("Lote inválido.")
    try:
        total = repo.purgar_expirados(db, agora_utc(), config.PURGA_LOTE)
        db.commit()
        return total
    except Exception:
        db.rollback()
        raise
