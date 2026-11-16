"""Respostas de erro sem valores recebidos, mensagens de provedores ou parâmetros SQL."""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def validacao_segura(request: Request, erro: RequestValidationError):
    # Até loc/msg/ctx podem conter chaves ou valores fornecidos pelo cliente.
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "loc": ["request"],
                    "msg": "Dados inválidos. Confira os campos informados.",
                    "type": "validation_error",
                }
            ]
        },
        headers={"Cache-Control": "no-store"},
    )


async def erro_interno_seguro(request: Request, erro: Exception):
    # Não passar a exceção para logging: até o texto da exceção pode conter segredos.
    logger.error("http.falha_interna", extra={"tipo_erro": type(erro).__name__})
    return JSONResponse(
        status_code=500,
        content={"detail": "Não foi possível concluir a solicitação."},
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
    )
