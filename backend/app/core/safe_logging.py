"""Saída mínima nos handlers da aplicação; nunca formatar payloads ou exceções brutas."""

import copy
import logging
import re
import time

EVENTOS = frozenset(
    {
        "http.falha_interna",
        "acesso.gravacao_falhou",
        "http.resposta",
        "auth.recuperacao.envio_falhou",
        "auth.confirmacao.envio_falhou",
        "auth.confirmacao.simulado",
        "auth.recuperacao.simulado",
        "auth.transporte.indisponivel",
        "moderacao.descarte_falhou",
        "abuso.negado",
        "abuso.fluxo_seguiu",
        "abuso.acao_isenta",
        "abuso.observado",
        "abuso.atraso_observado",
        "abuso.indisponivel",
        "abuso.limpeza_falhou",
    }
)
_NOME = re.compile(r"[a-zA-Z0-9_.]{1,100}\Z")


class FormatoSeguro(logging.Formatter):
    converter = time.gmtime

    def format(self, record: logging.LogRecord) -> str:
        # Não modificar o registro compartilhado com outros handlers.
        seguro = copy.copy(record)
        seguro.exc_info = None
        seguro.exc_text = None
        seguro.stack_info = None
        seguro.args = ()
        seguro.name = record.name if _NOME.fullmatch(record.name) else "biblioteca"
        if record.name == "uvicorn.access":
            # O access log padrão inclui IP, caminho, identificadores e query string.
            status = (
                record.args[4] if isinstance(record.args, tuple) and len(record.args) == 5 else None
            )
            seguro.msg = (
                f"http.resposta status={status}" if type(status) is int else "http.resposta"
            )
        elif isinstance(record.msg, str) and record.msg in EVENTOS:
            seguro.msg = record.msg
            if record.msg.startswith("abuso."):
                motivo = getattr(record, "motivo", None)
                if motivo in {"limite_identidade", "limite_global", "atraso"}:
                    seguro.msg += f" motivo={motivo}"
            if record.msg == "http.resposta":
                # Rota é o template do router, nunca request.url/path recebido.
                metodo = getattr(record, "metodo", "")
                rota = getattr(record, "rota", "nao_encontrada")
                status = getattr(record, "status_http", None)
                if metodo in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}:
                    seguro.msg += f" metodo={metodo}"
                if isinstance(rota, str) and re.fullmatch(r"[/a-zA-Z0-9_{}-]{1,200}", rota):
                    seguro.msg += f" rota={rota}"
                if type(status) is int:
                    seguro.msg += f" status={status}"
        else:
            # Não é possível sanitizar com regex texto livre de bibliotecas/provedores.
            seguro.msg = "registro_tecnico detalhes_omitidos"
            if record.name.startswith("alembic") and isinstance(record.msg, str):
                if record.msg.startswith("Running upgrade"):
                    seguro.msg = "migracao.upgrade"
                elif record.msg.startswith("Running downgrade"):
                    seguro.msg = "migracao.downgrade"
        tipo = getattr(record, "tipo_erro", None)
        if record.exc_info:
            tipo = record.exc_info[0].__name__
        if isinstance(tipo, str) and _NOME.fullmatch(tipo):
            seguro.msg += f" tipo={tipo}"
        return super().format(seguro)


def configurar_logs_seguros() -> None:
    """Aplicar após a configuração do Uvicorn/Alembic, inclusive a handlers próprios."""
    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(logging.StreamHandler())
    formato = FormatoSeguro(
        "%(asctime)sZ %(levelname)s [%(name)s] %(message)s", "%Y-%m-%dT%H:%M:%S"
    )
    loggers = [root, *list(logging.Logger.manager.loggerDict.values())]
    for logger in loggers:
        if isinstance(logger, logging.Logger):
            for handler in logger.handlers:
                handler.setFormatter(formato)
