"""#267: backup/restore exclusivamente sintéticos em Docker descartável.

python scripts/recovery_drill.py --confirm-disposable --image <imagem-backend>
Exige imagem com requirements.txt e httpx (TestClient) instalados. Monta o backend
atual somente para leitura. Não recebe URL, dump, volume ou conexão externos.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "undb267_disposable_source"
TARGET = "undb267_disposable_restore"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument(
        "--image",
        required=True,
        help="Imagem local de dependências do backend; não é removida",
    )
    parser.add_argument("--output", type=Path, default=ROOT / "recovery267-results.json")
    args = parser.parse_args()
    if not args.confirm_disposable:
        parser.error("Confirme o ensaio local descartável com --confirm-disposable")
    if not args.output.parent.is_dir() or args.output.exists():
        parser.error("Destino do relatório deve ser novo e ter diretório existente")

    prefix = "undb267-disposable-" + secrets.token_hex(6)
    network, pg, app = prefix + "-net", prefix + "-db", prefix + "-app"
    password = secrets.token_urlsafe(32)
    env = {
        **os.environ,
        "POSTGRES_PASSWORD": password,
        "PGPASSWORD": password,
        "SECRET_KEY": secrets.token_urlsafe(32),
        "ABUSO_HMAC_SECRET": secrets.token_urlsafe(32),
    }
    result = {
        "data_inicio_utc": datetime.now(timezone.utc).isoformat(),
        "etapas": [],
        "ambiente": "Docker, rede interna exclusiva sem portas, dados/tmp em tmpfs; somente sintético",
        "imagem_dependencias": args.image,
        "producao_acessada": False,
    }
    owned = []
    phase = "preflight"

    def run(*command, environment=env, timeout=180):
        completed = subprocess.run(
            command,
            check=False,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if completed.returncode:
            # Não divulgar saída de ferramentas/SQL/HTTP, que pode conter segredos.
            # Mensagens controladas de AssertionError ajudam a distinguir defeito do ensaio.
            safe = [
                line for line in completed.stdout.splitlines() if line.startswith("AssertionError:")
            ]
            raise RuntimeError(
                f"comando retornou {completed.returncode}" + (f"; {safe[-1]}" if safe else "")
            )
        return completed.stdout.strip()

    def pg_command(*command):
        return run("docker", "exec", "--env", "PGPASSWORD", pg, *command)

    def stage(name, database):
        nonlocal phase
        phase = name
        uri = f"postgresql+psycopg2://drill:{password}@issue267-db:5432/{database}"
        private_env = {**env, "DATABASE_URL": uri, "MIGRATION_DATABASE_URL": uri}
        output = run(
            "docker",
            "exec",
            "--env",
            "DATABASE_URL",
            "--env",
            "MIGRATION_DATABASE_URL",
            app,
            "python",
            "-m",
            "tests.recovery_scenario",
            name,
            environment=private_env,
        )
        payload = next(
            line.removeprefix("ISSUE267_RESULT=")
            for line in output.splitlines()
            if line.startswith("ISSUE267_RESULT=")
        )
        result["etapas"].append({"etapa": name, "resultado": json.loads(payload)})
        print(name + ": aprovado", flush=True)

    try:
        result["sha_base"] = run("git", "-C", str(ROOT), "rev-parse", "HEAD")
        result["fontes_sha256"] = {
            str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (
                Path(__file__).resolve(),
                ROOT / "backend/tests/recovery_scenario.py",
            )
        }
        context = run("docker", "context", "show")
        endpoint = run(
            "docker",
            "context",
            "inspect",
            context,
            "--format",
            '{{(index .Endpoints "docker").Host}}',
        )
        effective_endpoint = os.environ.get("DOCKER_HOST") or endpoint
        if not effective_endpoint.startswith(("npipe://", "unix://")):
            raise RuntimeError("Exige Docker local via named pipe/socket, sem endpoint remoto")
        result["docker_contexto_local"] = True
        result["docker"] = run("docker", "version", "--format", "{{.Server.Version}}")
        result["imagem_id"] = run("docker", "image", "inspect", args.image, "--format", "{{.Id}}")
        run(
            "docker",
            "network",
            "create",
            "--internal",
            "--label",
            "undb.issue=267",
            network,
        )
        owned.append(("network", network))
        phase = "postgres"
        run(
            "docker",
            "create",
            "--name",
            pg,
            "--label",
            "undb.issue=267",
            "--network",
            network,
            "--network-alias",
            "issue267-db",
            "--env",
            "POSTGRES_PASSWORD",
            "--env",
            "POSTGRES_USER=drill",
            "--tmpfs",
            "/var/lib/postgresql/data:rw,noexec,nosuid",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid",
            "postgres:16",
        )
        owned.append(("container", pg))
        run("docker", "start", pg)
        for _ in range(60):
            try:
                pg_command("pg_isready", "-U", "drill")
                break
            except RuntimeError:
                time.sleep(1)
        else:
            raise RuntimeError("PostgreSQL descartável não iniciou")
        result["postgres"] = pg_command("postgres", "--version")
        for database in (SOURCE, TARGET):
            pg_command("createdb", "-U", "drill", "--template=template0", database)
        phase = "application"
        # Container exclusivo sem porta, filesystem read-only e diretório privado efêmero.
        run(
            "docker",
            "create",
            "--name",
            app,
            "--label",
            "undb.issue=267",
            "--network",
            network,
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,mode=1777",
            "--mount",
            f"type=bind,source={ROOT / 'backend'},target=/app,readonly",
            "--workdir",
            "/app",
            "--env",
            "ISSUE267_DISPOSABLE=1",
            "--env",
            "SECRET_KEY",
            "--env",
            "ABUSO_HMAC_SECRET",
            "--env",
            "DEBUG=False",
            "--env",
            "CORS_ORIGINS=https://frontend.example",
            "--env",
            "FRONTEND_URL=https://frontend.example",
            "--env",
            "EMAIL_BACKEND=console",
            "--env",
            "CANAL_TITULARES_ATIVO=False",
            "--env",
            "CANAL_TITULARES_RETENCAO_APROVADA=False",
            "--env",
            "CANAL_TITULARES_LEITORES=",
            "--env",
            "CANAL_TITULARES_ATENDENTES=",
            "--env",
            "MODERACAO_FILTRO_ATIVO=False",
            "--env",
            "MODERACAO_IA_ATIVA=False",
            "--env",
            "MODERACAO_AUTOMATICA_ATIVA=False",
            args.image,
            "python",
            "-c",
            "import time; time.sleep(3600)",
        )
        owned.append(("container", app))
        run("docker", "start", app)
        result["python"] = run("docker", "exec", app, "python", "--version")
        result["dependencias"] = run(
            "docker", "exec", app, "python", "-m", "pip", "freeze"
        ).splitlines()
        source_uri = f"postgresql+psycopg2://drill:{password}@issue267-db:5432/{SOURCE}"
        target_uri = f"postgresql+psycopg2://drill:{password}@issue267-db:5432/{TARGET}"

        def alembic(database_uri, *command):
            return run(
                "docker",
                "exec",
                "--env",
                "DATABASE_URL",
                "--env",
                "MIGRATION_DATABASE_URL",
                app,
                "alembic",
                *command,
                environment={
                    **env,
                    "DATABASE_URL": database_uri,
                    "MIGRATION_DATABASE_URL": database_uri,
                },
            )

        phase = "migrations"
        alembic(source_uri, "upgrade", "head")
        alembic(source_uri, "check")
        result["alembic"] = {"upgrade_origem_head": 0, "check_origem": 0}
        stage("seed", SOURCE)
        phase = "dump"
        pg_command(
            "sh",
            "-c",
            "umask 077; mkdir -m 700 /tmp/issue267; "
            f"pg_dump -U drill -Fc --no-owner --no-acl --file=/tmp/issue267/backup.dump {SOURCE}",
        )
        check_mode = pg_command("stat", "-c", "%a", "/tmp/issue267/backup.dump")
        if check_mode != "600":
            raise RuntimeError("dump sem proteção 0600")
        pg_command("pg_restore", "--list", "/tmp/issue267/backup.dump")
        result["dump"] = {
            "formato": "custom",
            "modo": check_mode,
            "listagem_valida": True,
            "destino_distinto": True,
            "local": "tmpfs privado no container, sem exportação",
        }
        stage("late", SOURCE)
        phase = "restore"
        pg_command(
            "pg_restore",
            "-U",
            "drill",
            "--no-owner",
            "--no-acl",
            "--exit-on-error",
            "--dbname=" + TARGET,
            "/tmp/issue267/backup.dump",
        )
        stage("verify", TARGET)
        alembic(target_uri, "check")
        result["alembic"]["check_restaurado"] = 0
        stage("replay", TARGET)
        stage("journey", TARGET)
        stage("retention", TARGET)
        result["resultado"] = "aprovado"
    except Exception as error:
        result["resultado"] = "falha"
        # Nunca serializar ConnectionError/SQL/ambiente com URI.
        result["falha"] = {
            "etapa": phase,
            "tipo": type(error).__name__,
            "detalhe": str(error)
            if isinstance(error, RuntimeError)
            else "verificar preparação do ensaio",
        }
        print(f"Falha na etapa {phase}: {result['falha']['detalhe']}", flush=True)
    finally:
        cleanup = []
        for kind, name in reversed(owned):
            try:
                run(
                    "docker",
                    kind,
                    "rm",
                    *(["--force"] if kind == "container" else []),
                    name,
                )
                cleanup.append({"tipo": kind, "removido": True})
            except Exception:
                cleanup.append({"tipo": kind, "removido": False, "recurso": name})
        result["descarte"] = cleanup
        result["dump_diario_conexoes_removidos"] = len(cleanup) == 3 and all(
            c["removido"] for c in cleanup
        )
        if not result["dump_diario_conexoes_removidos"]:
            result["resultado"] = "falha"
        result["data_fim_utc"] = datetime.now(timezone.utc).isoformat()
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return 0 if result["resultado"] == "aprovado" else 1


if __name__ == "__main__":
    sys.exit(main())
