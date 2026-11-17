"""Ensaio destrutivo EXCLUSIVO em cluster local descartável, sem dados reais.

Execute com Python 3.12 da venv e --confirm-disposable-local. O script exige que
os bancos/roles reservados ainda não existam e remove apenas o que criou.
Não configure URLs de ambiente compartilhado: todas são substituídas aqui.
"""

import argparse
import json
import os
import secrets
import subprocess
import sys
from contextlib import closing
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
BACKEND = ROOT / "backend"
DATABASES = ("issue266_migracoes", "undb_207_test")
ROLES = ("issue266_owner", "issue266_api")


def fluxo_http():
    """Usa DB real; substitui somente o transporte de e-mail externo."""
    sys.path.insert(0, str(BACKEND))
    from app.core.database import engine
    from app.main import app
    from app.services.email_service import get_email_sender
    from fastapi.testclient import TestClient

    class Sender:
        token = None

        def enviar_confirmacao(self, destinatario, link):
            self.token = parse_qs(urlsplit(link).query)["token"][0]

        enviar_recuperacao_senha = enviar_confirmacao

    sender = Sender()
    app.dependency_overrides[get_email_sender] = lambda: sender
    try:
        with TestClient(app, base_url="https://api.example") as client:

            def post(path, body=None, expected=200):
                response = client.post(path, json=body)
                assert response.status_code == expected, (path, response.status_code)
                assert response.headers["cache-control"] == "no-store"
                assert response.headers["referrer-policy"] == "no-referrer"
                return response

            client.headers["Origin"] = "https://frontend.example"
            email = "postgres266@aluno.unb.br"
            senha = secrets.token_urlsafe(24)
            nova = secrets.token_urlsafe(24)
            post(
                "/api/auth/cadastro",
                {"nome": "Pessoa sintética", "email": email, "senha": senha},
                202,
            )
            confirmacao = sender.token
            post("/api/auth/confirmar", {"token": confirmacao})
            post("/api/auth/confirmar", {"token": confirmacao}, 400)
            r = post("/api/auth/login", {"email": email, "senha": senha})
            assert all(
                flag in r.headers["set-cookie"]
                for flag in ("HttpOnly", "Secure", "SameSite=lax")
            )
            cookie_antigo = client.cookies.get("undb_session")
            assert client.get("/api/auth/sessao").json()["autenticado"] is True
            client.headers["Origin"] = "https://externa.example"
            post("/api/auth/logout", expected=403)
            assert client.get("/api/auth/sessao").json()["autenticado"] is True
            client.headers["Origin"] = "https://frontend.example"
            post("/api/auth/recuperar-senha", {"email": email}, 202)
            primeiro = sender.token
            post("/api/auth/recuperar-senha", {"email": email}, 202)
            token = sender.token
            # RF24 invalida os demais links após a troca, não ao solicitar outro.
            post("/api/auth/redefinir-senha", {"token": primeiro, "senha": nova})
            post("/api/auth/redefinir-senha", {"token": token, "senha": nova}, 400)
            post("/api/auth/redefinir-senha", {"token": primeiro, "senha": nova}, 400)
            client.cookies.set(
                "undb_session", cookie_antigo, domain="api.example", path="/"
            )
            assert client.get("/api/auth/sessao").json()["autenticado"] is False
            post("/api/auth/login", {"email": email, "senha": senha}, 401)
            post("/api/auth/login", {"email": email, "senha": nova})
            post("/api/auth/logout")
            assert client.get("/api/auth/sessao").json()["autenticado"] is False
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
    print(
        "Fluxo PostgreSQL de confirmação/login/CSRF/recuperação/revogação/logout aprovado."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-disposable-local", action="store_true")
    parser.add_argument("--port", type=int, default=55466)
    parser.add_argument("--admin-user", default="auditor266")
    parser.add_argument("--password-file", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".audit-tools")
    parser.add_argument("--http-child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.http_child:
        fluxo_http()
        return
    if not args.confirm_disposable_local or not args.password_file:
        parser.error(
            "Exige confirmação de cluster descartável local e arquivo de senha sintética."
        )

    import psycopg2
    from psycopg2 import sql

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    admin = psycopg2.connect(
        host="127.0.0.1",
        port=args.port,
        user=args.admin_user,
        password=args.password_file.read_text(encoding="ascii"),
        dbname="postgres",
    )
    admin.autocommit = True
    passwords = {role: secrets.token_urlsafe(32) for role in ROLES}
    created_dbs, created_roles, results = [], [], []

    def url(role, database):
        return f"postgresql+psycopg2://{role}:{quote(passwords[role])}@127.0.0.1:{args.port}/{database}"

    env = {
        **os.environ,
        "DATABASE_URL": url(ROLES[1], DATABASES[0]),
        "MIGRATION_DATABASE_URL": url(ROLES[0], DATABASES[0]),
        "SECRET_KEY": secrets.token_urlsafe(32),
        "DEBUG": "False",
        "CORS_ORIGINS": "http://localhost:3000",
        "FRONTEND_URL": "https://frontend.example",
        "EMAIL_BACKEND": "console",
        "CANAL_TITULARES_ATIVO": "False",
        "CANAL_TITULARES_RETENCAO_APROVADA": "False",
        "RECONCILIACAO_POSTGRES_TEST_URL": url(ROLES[0], DATABASES[1]),
    }

    def run(label, *command, environment=None):
        with (output / f"{label}.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(
                [sys.executable, *command],
                cwd=BACKEND,
                env=environment or env,
                stdout=log,
                stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                check=False,
            )
        results.append({"etapa": label, "exit_code": result.returncode})
        print(label, result.returncode, flush=True)
        if result.returncode:
            raise RuntimeError(
                f"Etapa {label} falhou; consultar log local sanitizado antes de publicar."
            )

    try:
        with admin.cursor() as cursor:
            cursor.execute(
                "SELECT datname FROM pg_database WHERE datname = ANY(%s)",
                (list(DATABASES),),
            )
            if cursor.fetchall():
                raise RuntimeError(
                    "Banco reservado já existe; não reutilizar nem apagar."
                )
            cursor.execute(
                "SELECT rolname FROM pg_roles WHERE rolname = ANY(%s)", (list(ROLES),)
            )
            if cursor.fetchall():
                raise RuntimeError(
                    "Role reservada já existe; não reutilizar nem apagar."
                )
            cursor.execute("SHOW server_version")
            results.append(
                {"postgresql": cursor.fetchone()[0], "python": sys.version.split()[0]}
            )
            for role in ROLES:
                cursor.execute(
                    sql.SQL(
                        "CREATE ROLE {} LOGIN PASSWORD %s NOSUPERUSER NOCREATEDB NOCREATEROLE"
                    ).format(sql.Identifier(role)),
                    (passwords[role],),
                )
                created_roles.append(role)
            for database in DATABASES:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(database), sql.Identifier(ROLES[0])
                    )
                )
                created_dbs.append(database)
        for label, command in (
            ("migration-up", ("alembic", "upgrade", "head")),
            ("migration-check", ("alembic", "check")),
            ("migration-down", ("alembic", "downgrade", "base")),
            ("migration-up-repeat", ("alembic", "upgrade", "head")),
            ("legacy-down", ("alembic", "downgrade", "base")),
            ("legacy-base", ("alembic", "upgrade", "20260911_01")),
            ("legacy-seed", ("tests.migration_legacy_check", "seed")),
            ("legacy-up", ("alembic", "upgrade", "head")),
            ("legacy-verify", ("tests.migration_legacy_check", "verify-upgrade")),
            ("legacy-check", ("alembic", "check")),
            ("legacy-downgrade", ("alembic", "downgrade", "20260911_01")),
            (
                "legacy-verify-down",
                ("tests.migration_legacy_check", "verify-downgrade"),
            ),
            ("legacy-up-final", ("alembic", "upgrade", "head")),
        ):
            # Fixtures legadas exigem DML de owner antes dos grants da aplicação.
            owner_env = {**env, "DATABASE_URL": env["MIGRATION_DATABASE_URL"]}
            run(label, "-m", *command, environment=owner_env)
        with (
            closing(
                psycopg2.connect(
                    host="127.0.0.1",
                    port=args.port,
                    user=args.admin_user,
                    password=args.password_file.read_text(encoding="ascii"),
                    dbname=DATABASES[0],
                )
            ) as conn,
            conn,
            conn.cursor() as cursor,
        ):
            cursor.execute(
                sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(
                    sql.Identifier(ROLES[1])
                )
            )
            cursor.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename <> 'alembic_version'"
            )
            for (table,) in cursor.fetchall():
                cursor.execute(
                    sql.SQL(
                        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE {} TO {}"
                    ).format(sql.Identifier(table), sql.Identifier(ROLES[1]))
                )
            cursor.execute(
                "SELECT has_schema_privilege(%s, 'public', 'CREATE'), rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname=%s",
                (ROLES[1], ROLES[1]),
            )
            assert cursor.fetchone() == (False, False, False, False)
        run(
            "http-seguranca",
            str(Path(__file__).resolve()),
            "--http-child",
            environment={**env, "CORS_ORIGINS": "https://frontend.example"},
        )
        run(
            "suite312-postgres",
            "-m",
            "coverage",
            "run",
            "--branch",
            "--source=app",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-q",
        )
        run(
            "integracao-avaliacao",
            "-m",
            "tests.integration_avaliacao",
            "--api-only",
            environment={**env, "UNDB_INTEGRATION_TEST": "1"},
        )
        run("integracao-moderacao", "-m", "tests.integration_moderacao")
    finally:
        with admin.cursor() as cursor:
            for database in reversed(created_dbs):
                cursor.execute(
                    sql.SQL("DROP DATABASE {} WITH (FORCE)").format(
                        sql.Identifier(database)
                    )
                )
            for role in reversed(created_roles):
                cursor.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))
        admin.close()
        (output / "postgres-resultados.json").write_text(
            json.dumps(results, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
