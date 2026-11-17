"""Registro dedicado: nunca copiar corpo, query string ou exceção para console."""

import calendar
import logging
import re
from datetime import datetime, timezone
from uuid import uuid4
from starlette.concurrency import run_in_threadpool
from app.core import config
from app.core.database import SessionLocal
from app.repositories import registro_acesso_repository as repo


def expira_em(data, meses):
    if meses <= 0:
        raise ValueError("Retenção deve ser positiva.")
    ano, mes = divmod(data.year * 12 + data.month - 1 + meses, 12)
    return data.replace(
        year=ano, month=mes + 1, day=min(data.day, calendar.monthrange(ano, mes + 1)[1])
    )


def operacao(method, path):
    if method in {"POST", "PATCH", "DELETE"}:
        for prefixo in (
            "auth",
            "avaliacoes",
            "comentarios",
            "moderacao",
            "solicitacoes",
            "atendimento",
        ):
            if re.fullmatch(rf"/api/{prefixo}(?:/[A-Za-z0-9_-]+)*", path):
                # Só nomes de operações; nunca IDs ou caminhos recebidos no registro.
                if prefixo == "auth":
                    ultimo = path.rsplit("/", 1)[-1]
                    if ultimo not in {
                        "cadastro",
                        "login",
                        "confirmar",
                        "reenviar-confirmacao",
                        "recuperar-senha",
                        "redefinir-senha",
                        "logout",
                        "conta",
                    }:
                        return None
                    return f"auth.{ultimo}"
                sufixo = {"POST": "escrever", "PATCH": "editar", "DELETE": "excluir"}[method]
                if prefixo == "comentarios" and path.endswith("/denuncias"):
                    return "denuncia.criar"
                return f"{prefixo}.{sufixo}"
    return None


def gravar(dados):
    try:
        with SessionLocal() as db:
            repo.gravar(db, dados)
    except Exception:
        logging.getLogger(__name__).error("acesso.gravacao_falhou")


class RegistrosAcesso:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        op = operacao(scope["method"], scope["path"])
        if op is None:
            return await self.app(scope, receive, send)
        status = 500
        requisicao = uuid4()

        async def enviar(mensagem):
            nonlocal status
            if mensagem["type"] == "http.response.start":
                status = mensagem["status"]
            await send(mensagem)

        try:
            await self.app(scope, receive, enviar)
        finally:
            agora = datetime.now(timezone.utc)
            headers = [(k.lower(), v) for k, v in scope.get("headers", [])]
            encaminhados = [
                v.decode("latin-1") for k, v in headers if k in {b"forwarded", b"x-forwarded-for"}
            ]
            try:
                dados = dict(
                    ocorrido_em=agora,
                    expira_em=expira_em(agora, config.ACESSO_RETENCAO_MESES),
                    operacao=op,
                    usuario_id=scope.get("acesso_usuario_id"),
                    ip_conexao=scope.get("client", (None,))[0] if scope.get("client") else None,
                    encaminhado_nao_confiavel="\n".join(encaminhados) if encaminhados else None,
                    resultado="sucesso" if status < 400 else "falha",
                    requisicao_id=requisicao,
                )
                await run_in_threadpool(gravar, dados)
            except Exception:
                logging.getLogger(__name__).error("acesso.gravacao_falhou")
