"""Adaptadores HTTP do bloco 3; autorização permanece nas dependências existentes."""

import logging
from math import ceil
from threading import Lock
from time import monotonic

from fastapi import Depends

from app.core import config
from app.core.auth import obter_sessao_opcional, obter_usuario_confirmado, obter_moderador
from app.core.dependencia_limite_abuso import (
    AbusoExcedido,
    LimitadorIndisponivel,
    obter_limitador,
)
from app.core.limite_abuso import IdentidadeAbuso, TipoIdentidade
from app.domain.limite_abuso import FalhaLimite, PoliticaAbuso

logger = logging.getLogger(__name__)
_lock = Lock()
_inicio = 0.0
_quantidade = 0


def politica_fluxo(operacao, papel=None):
    perfil = config.FLUXOS_ABUSO_POLITICAS[operacao]
    nome = f"{operacao}.{papel}" if papel else operacao
    dados = dict(perfil)
    if papel:
        dados["quantidade"] = config.FLUXOS_ABUSO_POR_PAPEL[papel]
    dados.update(config.ABUSO_POLITICAS.get(nome, {}))
    dados["falha"] = perfil["falha"]
    return PoliticaAbuso(operacao=nome, **dados)


def fallback_denuncia():
    """Um teto global por processo, somente durante falha; não é distribuído."""
    global _inicio, _quantidade
    with _lock:
        agora = monotonic()
        janela = config.DENUNCIA_FALLBACK_JANELA_SEGUNDOS
        limite = config.DENUNCIA_FALLBACK_QUANTIDADE
        if janela <= 0 or limite <= 0:
            raise LimitadorIndisponivel(config.ABUSO_RETRY_FALHA_SEGUNDOS)
        if agora - _inicio >= janela:
            _inicio, _quantidade = agora, 0
        if _quantidade >= limite:
            raise AbusoExcedido(max(1, ceil(janela - (agora - _inicio))))
        _quantidade += 1


def verificar(operacao, usuario, limitador, papel=None):
    falha = config.FLUXOS_ABUSO_POLITICAS[operacao]["falha"]
    try:
        politica = politica_fluxo(operacao, papel)
    except (ValueError, TypeError, KeyError):
        resultado = limitador.falha(falha)
    else:
        identidade = IdentidadeAbuso(TipoIdentidade.CONTA, str(usuario.id)) if usuario else None
        resultado = limitador.consumir(politica, identidade)
    if resultado.indisponivel:
        if falha == FalhaLimite.SEGUIR:
            logger.warning("abuso.fluxo_seguiu")
            return
        if falha == FalhaLimite.LOCAL:
            fallback_denuncia()
            return
        raise LimitadorIndisponivel(resultado.retry_after)
    if not resultado.permitido:
        raise AbusoExcedido(resultado.retry_after)


def avaliar(usuario=Depends(obter_usuario_confirmado), limitador=Depends(obter_limitador)):
    verificar("avaliacao.escrever", usuario, limitador)


def denunciar(sessao=Depends(obter_sessao_opcional), limitador=Depends(obter_limitador)):
    verificar("denuncia.criar", sessao.usuario if sessao else None, limitador)


def titular(operacao):
    def dependencia(sessao=Depends(obter_sessao_opcional), limitador=Depends(obter_limitador)):
        verificar(operacao, sessao.usuario if sessao else None, limitador)

    return dependencia


def moderar(operacao, autorizacao=obter_moderador):
    def dependencia(usuario=Depends(autorizacao), limitador=Depends(obter_limitador)):
        papel = "moderador" if usuario.moderador else "reconciliador"
        verificar(operacao, usuario, limitador, papel)

    return dependencia


def registrar_bypass():
    # HTTP registra rota/status; este evento não inclui identidade nem payload.
    logger.info("abuso.acao_isenta")
