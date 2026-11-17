"""Ensaio destrutivo APENAS em banco descartável reservado para testes."""

import os
import runpy
from pathlib import Path
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url


def main():
    url = make_url(os.environ["MIGRATION_DATABASE_URL"])
    if url.host not in {"127.0.0.1", "localhost", "::1"} or url.database != "undb_266_test":
        raise ValueError("Exige banco local reservado undb_266_test, nunca produção.")
    cfg = Config("alembic.ini")
    engine = create_engine(url, hide_parameters=True)
    for origem in ("develop_02", "retencao_02", "acessos_03"):
        command.downgrade(cfg, "base")
        command.upgrade(cfg, "20261115_02")
        if origem == "develop_02":
            command.upgrade(cfg, "20261117_02")
        else:
            command.upgrade(cfg, "20261117_01")
            with engine.begin() as conn, Operations.context(MigrationContext.configure(conn)):
                runpy.run_path(str(Path("alembic/versions/20261117_02_retencao.py")))["upgrade"]()
                if origem == "acessos_03":
                    runpy.run_path(str(Path("alembic/versions/20261117_03_registros_acesso.py")))[
                        "upgrade"
                    ]()
            command.stamp(
                cfg, "20261117_02" if origem == "retencao_02" else "20261117_03", purge=True
            )
        command.upgrade(cfg, "head")
        command.check(cfg)
        with engine.connect() as conn:
            assert conn.scalar(text("SELECT version_num FROM alembic_version")) == "20261117_04"
            cols = {c["name"] for c in inspect(conn).get_columns("usuarios")}
            assert {"termos_versao", "termos_ciencia_em", "excluido_em"} <= cols
        print(origem + ": migracao/check aprovados")
    engine.dispose()


if __name__ == "__main__":
    main()
