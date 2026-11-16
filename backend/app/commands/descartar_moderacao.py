"""Discard expired moderation data. Keep --continuo running in the application environment."""

import argparse
import logging
import time

from app.core.database import SessionLocal
from app.core.safe_logging import configurar_logs_seguros
from app.repositories.moderacao_repository import descartar_vencidos
from app.services.moderacao_service import agora_utc


def executar():
    with SessionLocal() as db:
        descartar_vencidos(db, agora_utc())
        db.commit()


def main():
    configurar_logs_seguros()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuo", action="store_true")
    args = parser.parse_args()
    while True:
        try:
            executar()
        except Exception as erro:
            logging.getLogger(__name__).error(
                "moderacao.descarte_falhou", extra={"tipo_erro": type(erro).__name__}
            )
            if not args.continuo:
                raise SystemExit(1) from None
        if not args.continuo:
            return
        time.sleep(60)


if __name__ == "__main__":
    main()
