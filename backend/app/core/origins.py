"""Restrição de origens aprovada na #266; independente da autorização de cada rota."""

from urllib.parse import urlsplit

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core import config


def _origem(valor: str, *, referer: bool = False) -> str | None:
    if not valor or any(c.isspace() or c == "\\" for c in valor):
        return None
    try:
        url = urlsplit(valor)
        if (
            url.scheme not in ("http", "https")
            or not url.hostname
            or "%" in url.netloc
            or url.username is not None
            or url.password is not None
            or not url.port
            and url.netloc.endswith(":")
        ):
            return None
        origem = f"{url.scheme}://{url.netloc}"
        if not referer and origem != valor:
            return None
        return origem
    except ValueError:
        return None


class ProtecaoOrigem:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if (
            scope["type"] != "http"
            or scope["method"] not in {"POST", "PUT", "PATCH", "DELETE"}
            or not (scope["path"] == "/api" or scope["path"].startswith("/api/"))
        ):
            return await self.app(scope, receive, send)

        request = Request(scope)
        origens = request.headers.getlist("origin")
        referencias = request.headers.getlist("referer")
        permitido = False
        if len(origens) == 1:
            origem = _origem(origens[0])
            permitido = origem is not None and origem in config.CORS_ORIGINS
        elif not origens and len(referencias) == 1:
            origem = _origem(referencias[0], referer=True)
            permitido = origem is not None and origem in config.CORS_ORIGINS
        elif not origens and not referencias:
            permitido = (
                "undb_session" not in request.cookies
                and scope["path"].rstrip("/") != "/api/auth/login"
            )
        if len(referencias) > 1:
            permitido = False
        if not permitido:
            resposta = JSONResponse(
                {"detail": "Origem da solicitação não autorizada."},
                status_code=403,
                headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
            )
            return await resposta(scope, receive, send)
        return await self.app(scope, receive, send)
