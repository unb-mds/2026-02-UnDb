"""Somente Moderation API gratuita: sem geração, prompts, ferramentas ou fallback pago."""

import json
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from pydantic import ValidationError

from app.schemas.triagem import ClassificacaoIA, RespostaModeracaoOpenAI

VERSAO_INTEGRACAO = "239-moderations-v1"


class TriagemIndisponivel(Exception):
    pass


class SemRedirecionamento(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def classificar(texto: str, *, chave: str, modelo: str, timeout: float) -> ClassificacaoIA:
    # Restringir a família de modelos evita configurar geração paga por engano.
    if not modelo.startswith("omni-moderation-") or len(texto) > 500:
        raise TriagemIndisponivel("configuracao de moderacao invalida")
    request = Request(
        "https://api.openai.com/v1/moderations",
        method="POST",
        data=json.dumps({"model": modelo, "input": texto}).encode(),
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"},
    )
    try:
        with build_opener(SemRedirecionamento()).open(request, timeout=timeout) as resposta:
            raw = resposta.read(32769)
        if len(raw) > 32768:
            raise ValueError("resposta excedeu limite")
        dados = RespostaModeracaoOpenAI.model_validate_json(raw)
        resultado = dados.results[0]
        return ClassificacaoIA(
            categorias=[
                categoria for categoria, marcada in resultado.categories.items() if marcada
            ],
            sinalizado=resultado.flagged,
            modelo=dados.model,
        )
    except (HTTPError, URLError, HTTPException, TimeoutError, OSError, ValueError, ValidationError):
        # Não propagar corpo ou mensagens do provedor: podem conter dados privados.
        raise TriagemIndisponivel("apoio indisponivel; manter revisao humana") from None
