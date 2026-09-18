from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.routers import avaliacoes, disciplinas, professores

app = FastAPI(title="G7 - Avaliação de Disciplinas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(avaliacoes.router)
app.include_router(disciplinas.router)
app.include_router(professores.router)
app.include_router(disciplinas.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
