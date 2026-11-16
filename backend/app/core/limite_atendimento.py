"""Orçamento temporário por cliente/processo; não confia em X-Forwarded-For."""

import hashlib
import hmac
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request

from app.core import config

_janelas: dict[str, tuple[float, int]] = {}
_lock = Lock()


def limitar(request: Request):
    cliente = request.client.host if request.client else "desconhecido"
    chave = hmac.new(config.SECRET_KEY.encode(), cliente.encode(), hashlib.sha256).hexdigest()
    agora = monotonic()
    with _lock:
        for k, (inicio, _) in list(_janelas.items()):
            if agora - inicio >= 60:
                del _janelas[k]
        inicio, quantidade = _janelas.get(chave, (agora, 0))
        if quantidade >= max(1, config.CANAL_TITULARES_LIMITE_MINUTO) or (
            chave not in _janelas and len(_janelas) >= 4096
        ):
            raise HTTPException(
                429, "Muitas tentativas. Aguarde um minuto.", headers={"Retry-After": "60"}
            )
        _janelas[chave] = (inicio, quantidade + 1)
