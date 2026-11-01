"""Discard expired moderation data. Keep --continuo running in the application environment."""
import argparse
import logging
import time

from app.core.database import SessionLocal
from app.repositories.moderacao_repository import descartar_vencidos
from app.services.moderacao_service import agora_utc


def executar():
    with SessionLocal() as db:
        descartar_vencidos(db, agora_utc())
        db.commit()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuo", action="store_true")
    args = parser.parse_args()
    while True:
        try:
            executar()
        except Exception:
            if not args.continuo:
                raise
            logging.exception("Falha no descarte de moderacao; nova tentativa em 60s")
        if not args.continuo:
            return
        time.sleep(60)


if __name__ == "__main__":
    main()
