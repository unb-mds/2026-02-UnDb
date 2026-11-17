"""RF26: migração e HTTP/PostgreSQL sintético em banco local exclusivo.

UNDB_269_POSTGRES_TEST=1 DATABASE_URL=postgresql+psycopg2://fixture@127.0.0.1:55469/undb_269_test \
SECRET_KEY=teste-local python -m tests.integration_termos
O banco deve estar vazio e criado previamente. Nunca aceita destino remoto.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def main():
    url = make_url(os.environ["DATABASE_URL"])
    if (
        os.environ.get("UNDB_269_POSTGRES_TEST") != "1"
        or url.host != "127.0.0.1"
        or url.port != 55469
        or url.database != "undb_269_test"
        or os.environ.get("MIGRATION_DATABASE_URL", str(url)) != str(url)
    ):
        raise SystemExit("Exige autorização de teste e banco local exclusivo undb_269_test:55469.")
    ambiente = {**os.environ, "MIGRATION_DATABASE_URL": os.environ["DATABASE_URL"]}
    backend = Path(__file__).resolve().parents[1]
    engine = create_engine(url)
    if inspect(engine).get_table_names():
        raise SystemExit("Banco precisa estar vazio; não apaga dados existentes.")

    def alembic(*args):
        resultado = subprocess.run(
            [sys.executable, "-m", "alembic", *args],
            cwd=backend,
            env=ambiente,
            capture_output=True,
            text=True,
        )
        if resultado.returncode:
            raise RuntimeError(
                f"Alembic {args[0]} falhou no ambiente sintético: {resultado.stderr}"
            )

    alembic("upgrade", "20261115_02")
    from app.core.database import get_db
    from app.core.security import gerar_hash_senha
    from app.domain.termos import TERMOS_VERSAO
    from app.main import app
    from app.models.usuario import Usuario
    from app.services.email_service import get_email_sender
    from tests.test_termos import EmailSintetico

    senha = "Senha-sintetica-269!"
    with engine.begin() as con:
        con.execute(
            text(
                "INSERT INTO usuarios(id,nome,email,password_hash,email_confirmado) "
                "VALUES (:id,'Conta antiga','antiga@aluno.unb.br',:hash,true)"
            ),
            {"id": uuid4(), "hash": gerar_hash_senha(senha)},
        )
    alembic("upgrade", "head")
    alembic("check")
    email = EmailSintetico()
    with Session(engine) as db:
        antiga = db.scalar(select(Usuario))
        assert antiga.termos_versao is None and antiga.termos_ciencia_em is None
        app.dependency_overrides[get_db] = lambda: db
        app.dependency_overrides[get_email_sender] = lambda: email
        try:
            with TestClient(app, base_url="https://testserver") as client:
                dados = dict(
                    nome="Nova conta",
                    email="nova@aluno.unb.br",
                    senha=senha,
                    ciencia_termos=True,
                    termos_versao=TERMOS_VERSAO,
                )
                for mudanca in ({"ciencia_termos": False}, {"termos_versao": "invalida"}):
                    assert (
                        client.post("/api/auth/cadastro", json={**dados, **mudanca}).status_code
                        == 422
                    )
                sem_ciencia = {k: v for k, v in dados.items() if k != "ciencia_termos"}
                assert client.post("/api/auth/cadastro", json=sem_ciencia).status_code == 422
                assert email.envios == []
                antes = datetime.now(timezone.utc)
                assert client.post("/api/auth/cadastro", json=dados).status_code == 202
                nova = db.scalar(select(Usuario).where(Usuario.email == dados["email"]))
                assert nova.termos_versao == TERMOS_VERSAO
                assert nova.termos_ciencia_em.tzinfo is not None
                assert (
                    antes
                    <= nova.termos_ciencia_em.astimezone(timezone.utc)
                    <= datetime.now(timezone.utc)
                )
                assert len(email.envios) == 1
                assert (
                    client.post(
                        "/api/auth/cadastro", json={**dados, "email": antiga.email}
                    ).status_code
                    == 202
                )
                db.refresh(antiga)
                assert antiga.termos_versao is None and antiga.termos_ciencia_em is None
                assert (
                    client.post(
                        "/api/auth/login",
                        json={"email": antiga.email, "senha": senha},
                        headers={"Origin": "http://localhost:3000"},
                    ).status_code
                    == 200
                )
                assert client.get("/api/auth/sessao").json()["autenticado"]
                try:
                    db.execute(
                        text("UPDATE usuarios SET termos_ciencia_em=NULL WHERE email=:email"),
                        {"email": nova.email},
                    )
                    db.commit()
                except IntegrityError:
                    db.rollback()
                else:
                    raise AssertionError("CHECK aceitou ciência incompleta")
        finally:
            app.dependency_overrides.clear()
    alembic("downgrade", "20261115_02")
    assert "termos_versao" not in {c["name"] for c in inspect(engine).get_columns("usuarios")}
    with engine.connect() as con:
        assert con.scalar(text("SELECT count(*) FROM usuarios")) == 2
    alembic("upgrade", "head")
    alembic("check")
    engine.dispose()
    print(
        json.dumps(
            {
                "postgresql": "16.15",
                "dados": "sintéticos",
                "producao_acessada": False,
                "upgrade_com_conta_antiga": "aprovado",
                "alembic_check": "aprovado",
                "http_cadastro_validacao_persistencia": "aprovado",
                "login_legado": "aprovado",
                "check_constraint": "aprovado",
                "downgrade_reaplicacao": "aprovado",
                "email": "adaptador sintético, nenhum envio externo",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
