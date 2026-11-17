"""Avaliação de políticas, sempre em transação própria e antes de efeitos do chamador."""

import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from math import ceil

from sqlalchemy.orm import Session

from app.core import config
from app.core.limite_abuso import IdentidadeAbuso, derivar_chave, sessao_limitador
from app.domain.limite_abuso import (
    FalhaLimite,
    ModoLimite,
    MotivoLimite,
    PoliticaAbuso,
    ResultadoLimite,
    atraso_progressivo,
)
from app.repositories import limite_abuso_repository as repo

logger = logging.getLogger(__name__)


def carregar_politica(operacao: str) -> PoliticaAbuso:
    # Só políticas explícitas da configuração, nunca parâmetros do cliente HTTP.
    campos = {
        "quantidade": config.ABUSO_QUANTIDADE_PADRAO,
        "janela_segundos": config.ABUSO_JANELA_SEGUNDOS_PADRAO,
        "quantidade_global": config.ABUSO_QUANTIDADE_GLOBAL_PADRAO,
        "janela_global_segundos": config.ABUSO_JANELA_GLOBAL_SEGUNDOS_PADRAO,
        **config.ABUSO_POLITICAS[operacao],
    }
    return PoliticaAbuso(operacao=operacao, **campos)


class LimitadorAbuso:
    def __init__(
        self,
        fabrica_sessao: Callable[[], Session] = sessao_limitador,
        relogio: Callable[[Session], datetime] = repo.agora_banco,
    ):
        self.fabrica_sessao = fabrica_sessao
        self.relogio = relogio

    def consumir(
        self, politica: PoliticaAbuso, identidade: IdentidadeAbuso | None = None
    ) -> ResultadoLimite:
        try:
            chave_global = derivar_chave(config.ABUSO_HMAC_SECRET, politica.operacao, None)
            chave = (
                derivar_chave(config.ABUSO_HMAC_SECRET, politica.operacao, identidade)
                if identidade is not None
                else None
            )
            with self.fabrica_sessao() as db, db.begin():
                agora = self.relogio(db)
                # Ordem uniforme global -> identidade evita ciclos entre consumidores.
                global_ = repo.incrementar(
                    db, politica.operacao, chave_global, politica.janela_global_segundos, agora
                )
                motivo, espera = MotivoLimite.PERMITIDO, 0
                if global_.quantidade > politica.quantidade_global:
                    motivo = MotivoLimite.GLOBAL
                    espera = ceil((global_.expira_em - agora).total_seconds())
                elif chave is not None:
                    estado = repo.incrementar(
                        db,
                        politica.operacao,
                        chave,
                        politica.janela_segundos,
                        agora,
                        politica.modo == ModoLimite.ENFORCE,
                    )
                    if estado.quantidade > politica.quantidade:
                        motivo = MotivoLimite.IDENTIDADE
                        espera = ceil((estado.expira_em - agora).total_seconds())
                    elif estado.proxima_tentativa_em and estado.proxima_tentativa_em > agora:
                        motivo = MotivoLimite.ATRASO
                        espera = ceil((estado.proxima_tentativa_em - agora).total_seconds())
                    elif politica.modo == ModoLimite.ENFORCE:
                        atraso = atraso_progressivo(estado.quantidade, politica)
                        if atraso:
                            # A espera não pode sobreviver ao orçamento da janela.
                            repo.definir_proxima_tentativa(
                                db,
                                politica.operacao,
                                chave,
                                min(agora + timedelta(seconds=atraso), estado.expira_em),
                            )
                    elif atraso_progressivo(estado.quantidade, politica):
                        # Observe mede o que imporia atraso, sem restringir a próxima chamada.
                        self._evento("abuso.atraso_observado", politica, MotivoLimite.ATRASO)
                # Orçamentos são confirmados também na negação; não dependem do rollback do fluxo.
            excedido = motivo != MotivoLimite.PERMITIDO
            if excedido:
                self._evento(
                    "abuso.observado" if politica.modo == ModoLimite.OBSERVE else "abuso.negado",
                    politica,
                    motivo,
                )
            return ResultadoLimite(
                permitido=not excedido or politica.modo == ModoLimite.OBSERVE,
                retry_after=max(0, espera),
                motivo=motivo,
                excedido=excedido,
            )
        except Exception:
            # Não registrar exceção, SQL, chave, identificador ou segredo.
            return self.falha(politica.falha)

    def reiniciar_identidade(self, politica: PoliticaAbuso, identidade: IdentidadeAbuso) -> bool:
        """Gancho para sucesso autenticado: preserva o orçamento global da operação."""
        try:
            chave = derivar_chave(config.ABUSO_HMAC_SECRET, politica.operacao, identidade)
            with self.fabrica_sessao() as db, db.begin():
                repo.reiniciar_identidade(db, politica.operacao, chave)
            return True
        except Exception:
            self.falha(politica.falha)
            return False

    def limpar_expirados(self) -> int:
        lote = config.ABUSO_LIMPEZA_LOTE
        if type(lote) is not int or lote <= 0:
            raise ValueError("Lote de limpeza inválido.")
        with self.fabrica_sessao() as db, db.begin():
            return repo.limpar_expirados(db, self.relogio(db), lote)

    @staticmethod
    def falha(acao: FalhaLimite = FalhaLimite.FECHAR) -> ResultadoLimite:
        logger.error("abuso.indisponivel")
        return ResultadoLimite(
            permitido=acao == FalhaLimite.SEGUIR,
            retry_after=max(1, config.ABUSO_RETRY_FALHA_SEGUNDOS),
            motivo=MotivoLimite.INDISPONIVEL,
            indisponivel=True,
            acao_falha=acao,
        )

    @staticmethod
    def _evento(evento: str, politica: PoliticaAbuso, motivo: MotivoLimite):
        logger.warning(evento, extra={"operacao": politica.operacao, "motivo": motivo.value})
