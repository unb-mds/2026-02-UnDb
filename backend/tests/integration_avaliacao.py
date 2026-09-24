"""Verificação explícita da #116: HTTP real, PostgreSQL migrado e navegador.

Execute em banco local de testes: python -m tests.integration_avaliacao [--api-only].
Não cria schema nem substitui dependências da aplicação. Remove só suas fixtures.
"""
import json
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.database import engine
from app.core.security import gerar_hash_senha, gerar_hash_token
from app.models.avaliacao import Avaliacao
from app.models.disciplina import Disciplina
from app.models.professor import Professor
from app.models.sessao_usuario import SessaoUsuario
from app.models.token_confirmacao_email import TokenConfirmacaoEmail
from app.models.turma import Turma, turmas_professores
from app.models.unidade import Unidade
from app.models.usuario import Usuario


def registros(fixture):
    with Session(engine) as db:
        return [dict(id=str(a.id), usuario_id=str(a.usuario_id), didatica=a.didatica,
                     dificuldade=a.dificuldade.value, chamada=a.chamada,
                     disponibiliza_material=a.disponibiliza_material,
                     qualidade_material=a.qualidade_material.value if a.qualidade_material else None,
                     recomenda=a.recomenda, created_at=a.created_at.isoformat(),
                     updated_at=a.updated_at.isoformat())
                for a in db.scalars(select(Avaliacao).where(
                    Avaliacao.professor_id == UUID(fixture["professorId"])))]


def requisicao(path, payload=None, cookie=None):
    headers = {"Content-Type": "application/json"}
    if cookie:
        headers["Cookie"] = cookie
    request = Request("http://127.0.0.1:8000" + path,
                      data=json.dumps(payload).encode() if payload is not None else None,
                      headers=headers)
    try:
        response = urlopen(request, timeout=20)
    except HTTPError as error:
        response = error
    with response:
        return response.status, json.load(response), response.headers


def verificar_api(fixture):
    payload = dict(professor_id=fixture["professorId"], disciplina_id=fixture["disciplinaId"],
                   didatica=4, dificuldade="MEDIO", chamada=True,
                   disponibiliza_material=True, qualidade_material="BOM", recomenda=True)
    for cookie in (None, "undb_session=invalida", "undb_session=" + fixture["expiredToken"]):
        assert requisicao("/api/avaliacoes", payload, cookie)[0] == 401
    status, _, headers = requisicao("/api/auth/login", dict(email=fixture["email"], senha=fixture["senha"]))
    assert status == 200
    cookie = headers["Set-Cookie"].split(";")[0]
    assert requisicao("/api/avaliacoes", payload, cookie)[0] == 403
    with Session(engine) as db:
        db.get(Usuario, UUID(fixture["usuarioId"])).email_confirmado = True
        db.commit()
    for changes in ({"usuario_id": fixture["usuarioId"]}, {"comentario": "texto"},
                    {"didatica": 6}, {"didatica": "3"}, {"chamada": "false"},
                    {"dificuldade": "INVALIDA"}, {"qualidade_material": None}):
        assert requisicao("/api/avaliacoes", {**payload, **changes}, cookie)[0] == 422
    for field in ("didatica", "dificuldade", "chamada", "disponibiliza_material", "recomenda"):
        incomplete = {key: value for key, value in payload.items() if key != field}
        assert requisicao("/api/avaliacoes", incomplete, cookie)[0] == 422
    assert registros(fixture) == []

    # Sessões distintas do mesmo usuário evitam que a renovação de uma única
    # sessão serialize artificialmente as requisições antes do upsert.
    cookies = [requisicao("/api/auth/login", dict(email=fixture["email"], senha=fixture["senha"]))[2]
               ["Set-Cookie"].split(";")[0] for _ in range(8)]
    barrier = Barrier(len(cookies))

    def enviar_concorrente(index):
        barrier.wait(timeout=20)
        return requisicao("/api/avaliacoes", {**payload, "didatica": index % 5 + 1}, cookies[index])

    with ThreadPoolExecutor(max_workers=len(cookies)) as pool:
        respostas = list(pool.map(enviar_concorrente, range(len(cookies))))
    assert all(response[0] == 200 for response in respostas), respostas
    assert len({response[1]["id"] for response in respostas}) == 1
    primeira = registros(fixture)
    assert len(primeira) == 1
    replacement = {**payload, "didatica": 1, "dificuldade": "DIFICIL", "chamada": False,
                   "disponibiliza_material": False, "qualidade_material": None, "recomenda": False}
    assert requisicao("/api/avaliacoes", replacement, cookie)[0] == 200
    segunda = registros(fixture)
    assert len(segunda) == 1 and segunda[0]["id"] == primeira[0]["id"]
    assert segunda[0]["created_at"] == primeira[0]["created_at"]
    assert segunda[0]["updated_at"] >= primeira[0]["updated_at"]
    for field in ("didatica", "dificuldade", "chamada", "disponibiliza_material", "qualidade_material", "recomenda"):
        assert segunda[0][field] == replacement[field]
    print("API/PostgreSQL: rejeições 401/403/422 sem escrita; 8 inserções concorrentes = 1 ID/linha; substituição integral preserva ID e criação.", flush=True)
    # Prepara a mesma fixture vazia/não confirmada para o fluxo do navegador.
    with Session(engine) as db:
        db.execute(delete(Avaliacao).where(Avaliacao.professor_id == UUID(fixture["professorId"])))
        db.get(Usuario, UUID(fixture["usuarioId"])).email_confirmado = False
        db.commit()


def main():
    assert engine.dialect.name == "postgresql", "A integração exige PostgreSQL real."
    if "--inspect" in sys.argv:
        print(json.dumps(registros(json.loads(os.environ["E2E_FIXTURE"])))); return
    assert os.environ.get("UNDB_INTEGRATION_TEST") == "1", "Defina UNDB_INTEGRATION_TEST=1 em banco de testes."
    with socket.socket() as reserva:
        reserva.bind(("127.0.0.1", 8000))
    suffix = uuid4().hex[:12]
    fixture = dict(professorId=str(uuid4()), disciplinaId=str(uuid4()), usuarioId=str(uuid4()),
                   unidadeId=str(uuid4()), turmaId=str(uuid4()), expiredToken=uuid4().hex,
                   confirmationToken=uuid4().hex,
                   email=f"integracao.{suffix}@aluno.unb.br", senha="senha-local-integracao")
    api = None
    try:
        with Session(engine) as db:
            professor = Professor(id=UUID(fixture["professorId"]), nome="Professor de teste", departamento="CIC")
            disciplina = Disciplina(id=UUID(fixture["disciplinaId"]), codigo=f"T{suffix}", nome="Disciplina de teste", departamento="CIC")
            unidade = Unidade(id=UUID(fixture["unidadeId"]), codigo=suffix, nome="Unidade de teste")
            usuario = Usuario(id=UUID(fixture["usuarioId"]), nome="Estudante de teste", email=fixture["email"],
                              password_hash=gerar_hash_senha(fixture["senha"]), email_confirmado=False)
            db.add_all([professor, disciplina, unidade, usuario])
            db.flush()
            db.add(Turma(id=UUID(fixture["turmaId"]), disciplina=disciplina, unidade=unidade,
                         codigo="1", semestre="2026.2", professores=[professor]))
            db.add(SessaoUsuario(usuario_id=usuario.id, token_hash=gerar_hash_token(fixture["expiredToken"]),
                                expires_at=datetime.now(timezone.utc) - timedelta(days=1)))
            db.add(TokenConfirmacaoEmail(usuario_id=usuario.id, token_hash=gerar_hash_token(fixture["confirmationToken"]),
                                        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)))
            db.commit()
        env = {**os.environ, "DEBUG": "True", "CORS_ORIGINS": "http://localhost:3100",
               "E2E_FIXTURE": json.dumps(fixture), "E2E_PYTHON": sys.executable}
        api = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"], env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            if api.poll() is not None:
                raise RuntimeError("A API não iniciou.")
            try:
                if requisicao("/health")[0] == 200:
                    break
            except (URLError, OSError):
                time.sleep(0.1)
        else:
            raise TimeoutError("API indisponível")
        verificar_api(fixture)
        if "--api-only" not in sys.argv:
            subprocess.run(["node", "tests/avaliacao-browser.mjs"], env=env,
                           cwd=Path(__file__).resolve().parents[2] / "frontend", check=True)
    finally:
        if api:
            api.terminate()
            api.wait(timeout=15)
        with Session(engine) as db:
            db.execute(delete(Avaliacao).where(Avaliacao.professor_id == UUID(fixture["professorId"])))
            db.execute(delete(SessaoUsuario).where(SessaoUsuario.usuario_id == UUID(fixture["usuarioId"])))
            db.execute(delete(TokenConfirmacaoEmail).where(TokenConfirmacaoEmail.usuario_id == UUID(fixture["usuarioId"])))
            db.execute(delete(turmas_professores).where(turmas_professores.c.turma_id == UUID(fixture["turmaId"])))
            for model, key in ((Turma, "turmaId"), (Usuario, "usuarioId"), (Professor, "professorId"),
                               (Disciplina, "disciplinaId"), (Unidade, "unidadeId")):
                db.execute(delete(model).where(model.id == UUID(fixture[key])))
            db.commit()


if __name__ == "__main__":
    main()
