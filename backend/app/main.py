from fastapi import FastAPI

from app.routers import avaliacoes, professores

app = FastAPI(title="G7 - Avaliação de Disciplinas")

app.include_router(avaliacoes.router)
app.include_router(professores.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
