"""Explicit migration data check, following tests.migration_legacy_check.

Run seed at 20261024_01, then upgrade head and run verify. Uses the evaluation
fixture from migration_legacy_check; only for a disposable migration database.
"""

import argparse
from uuid import UUID

from sqlalchemy import text

from app.core.database import engine
from tests.migration_legacy_check import AVALIACAO_ID

RETIRADO_ID = UUID("00000000-0000-0000-0000-000000000061")
PENDENTE_ID = UUID("00000000-0000-0000-0000-000000000062")


def seed():
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO comentario_versoes
            (id, avaliacao_id, texto, estado, created_at, updated_at)
            VALUES (:retirado, :avaliacao, 'Texto retirado legado', 'RETIRADO',
                    CURRENT_TIMESTAMP - INTERVAL '8 days', CURRENT_TIMESTAMP - INTERVAL '8 days'),
                   (:pendente, :avaliacao, 'Texto pendente legado', 'PENDENTE',
                    CURRENT_TIMESTAMP - INTERVAL '100 days', CURRENT_TIMESTAMP - INTERVAL '100 days')"""),
            {"retirado": RETIRADO_ID, "pendente": PENDENTE_ID, "avaliacao": AVALIACAO_ID},
        )


def verify():
    with engine.connect() as conn:
        assert (
            conn.scalar(
                text("SELECT texto FROM comentario_versoes WHERE id = :id"), {"id": RETIRADO_ID}
            )
            is None
        )
        assert (
            conn.scalar(
                text("SELECT texto FROM comentario_versoes WHERE id = :id"), {"id": PENDENTE_ID}
            )
            == "Texto pendente legado"
        )
        assert (
            conn.scalar(
                text("SELECT didatica FROM avaliacoes WHERE id = :id"), {"id": AVALIACAO_ID}
            )
            == 5
        )
        assert conn.scalar(text("SELECT COUNT(*) FROM usuarios WHERE moderador")) == 0
    print(
        "Migration: descarte legado, preservacao de pendente/criterios e ausencia de privilegio automatico aprovados"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao", choices=("seed", "verify"))
    args = parser.parse_args()
    (seed if args.acao == "seed" else verify)()
