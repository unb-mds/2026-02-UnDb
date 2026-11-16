from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
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

app = FastAPI(title="G7 - Avaliação de Disciplinas")
app.include_router(solicitacoes_titulares.router)


@app.middleware("http")
async def proteger_cache_privado(request, call_next):
    response = await call_next(request)
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
