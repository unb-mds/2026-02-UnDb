"""Rollback/reaplicação com dados mínimos, só em PostgreSQL descartável local."""

import os
from datetime import datetime, timezone
from uuid import uuid4
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def main():
    url = make_url(os.environ["MIGRATION_DATABASE_URL"])
    if url.host not in {"localhost", "127.0.0.1", "::1"} or url.database not in {
        "undb_266_test",
        "ci",
    }:
        raise ValueError("Somente banco local descartável.")
    engine = create_engine(url, hide_parameters=True)
    id = uuid4()
    agora = datetime.now(timezone.utc)
    cfg = Config("alembic.ini")
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO usuarios (id,nome,email,password_hash,email_confirmado,moderador,reconciliador,excluido_em) VALUES (:id,'',:email,NULL,false,false,false,:agora)"
                ),
                {"id": id, "email": f"{id.hex}@aluno.unb.br", "agora": agora},
            )
        command.downgrade(cfg, "20261117_01")
        with engine.connect() as conn:
            assert (
                conn.scalar(text("SELECT password_hash FROM usuarios WHERE id=:id"), {"id": id})
                == ""
            )
            assert (
                conn.scalar(
                    text("SELECT excluido_em FROM retencao_rollback_contas WHERE id=:id"),
                    {"id": id},
                )
                == agora
            )
        command.upgrade(cfg, "head")
        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT password_hash,excluido_em FROM usuarios WHERE id=:id"), {"id": id}
            ).one()
            assert row == (None, agora)
            conn.execute(text("DELETE FROM usuarios WHERE id=:id"), {"id": id})
        print("Rollback/reaplicação preservam exclusão e não recuperam credenciais.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
