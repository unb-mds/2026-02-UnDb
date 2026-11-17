"""Purga em lotes: executar uma vez ou periodicamente com --continuo."""

import argparse
import json
import logging
import time

from app.core import config
from app.core.safe_logging import configurar_logs_seguros
from app.services.limite_abuso_service import LimitadorAbuso


def executar() -> int:
    return LimitadorAbuso().limpar_expirados()


def main():
    configurar_logs_seguros()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuo", action="store_true")
    args = parser.parse_args()
    intervalo = config.ABUSO_LIMPEZA_INTERVALO_SEGUNDOS
    if intervalo <= 0:
        parser.error("Intervalo de limpeza deve ser positivo.")
    while True:
        try:
            print(json.dumps({"removidos": executar()}), flush=True)
        except Exception:
            logging.getLogger(__name__).error("abuso.limpeza_falhou")
            if not args.continuo:
                raise SystemExit(1) from None
        if not args.continuo:
            return
        time.sleep(intervalo)


if __name__ == "__main__":
    main()
