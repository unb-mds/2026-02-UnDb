import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import CORS_ORIGINS
from app.core.http_errors import erro_interno_seguro, validacao_segura
from app.core.http_errors import abuso_excedido_seguro, limitador_indisponivel_seguro
from app.core.http_errors import email_indisponivel_seguro
from app.services.email_service import EmailDeliveryError
from app.core.dependencia_limite_abuso import AbusoExcedido, LimitadorIndisponivel
from app.core.safe_logging import configurar_logs_seguros
from app.core.origins import ProtecaoOrigem
from app.routers import solicitacoes_titulares
from app.routers import (
    identidade_docente,
    auth,
    avaliacoes,
    comentarios,
    disciplinas,
    professores,
    moderacao,
    denuncias,
)

configurar_logs_seguros()
http_logger = logging.getLogger("app.http")
http_logger.setLevel(logging.INFO)
app = FastAPI(title="G7 - Avaliação de Disciplinas")
app.add_exception_handler(RequestValidationError, validacao_segura)
app.add_exception_handler(Exception, erro_interno_seguro)
app.add_exception_handler(AbusoExcedido, abuso_excedido_seguro)
app.add_exception_handler(LimitadorIndisponivel, limitador_indisponivel_seguro)
app.add_exception_handler(EmailDeliveryError, email_indisponivel_seguro)
app.include_router(solicitacoes_titulares.router)


@app.middleware("http")
async def proteger_cache_privado(request, call_next):
    response = await call_next(request)
    rota = request.scope.get("route")
    http_logger.info(
        "http.resposta",
        extra={
            "metodo": request.method,
            "rota": getattr(rota, "path", "nao_encontrada"),
            "status_http": response.status_code,
        },
    )
    rotas_privadas = (
        "/api/auth",
        "/api/avaliacoes",
        "/api/comentarios",
        "/api/agradecimentos",
        "/api/moderacao",
        "/api/solicitacoes",
        "/api/atendimento",
    )
    if any(
        request.url.path == rota or request.url.path.startswith(f"{rota}/")
        for rota in rotas_privadas
    ):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
    return response


app.add_middleware(ProtecaoOrigem)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(identidade_docente.router)
app.include_router(avaliacoes.router)
app.include_router(auth.router)
app.include_router(professores.router)
app.include_router(disciplinas.router)
app.include_router(comentarios.router)
app.include_router(moderacao.router)
app.include_router(denuncias.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
