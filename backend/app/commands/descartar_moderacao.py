"""Discard expired moderation data. Keep --continuo running in the application environment."""

import argparse
import logging
import time

from app.core.database import SessionLocal
from app.core import config
from app.services.retencao_service import purgar
from app.core.safe_logging import configurar_logs_seguros
from app.repositories.moderacao_repository import descartar_vencidos
from app.services.moderacao_service import agora_utc


def executar():
    with SessionLocal() as db:
        purgar(db)
        descartar_vencidos(db, agora_utc())
        db.commit()


def main():
    configurar_logs_seguros()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuo", action="store_true")
    args = parser.parse_args()
    if config.PURGA_INTERVALO_SEGUNDOS <= 0:
        parser.error("Intervalo de purga deve ser positivo.")
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
        time.sleep(config.PURGA_INTERVALO_SEGUNDOS)


if __name__ == "__main__":
    main()
