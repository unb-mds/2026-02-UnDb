"""Lista os identificadores das unidades disponíveis no formulário público do SIGAA."""

import sys

from app.scrapers.sigaa_poc import listar_unidades, listar_unidades_reais


def main() -> None:
    try:
        for identificador, nome in listar_unidades_reais():
            print(f"{identificador} -> {nome}")
    except (OSError, ValueError) as erro:
        print(f"Não foi possível listar as unidades do SIGAA: {erro}", file=sys.stderr)
        raise SystemExit(1) from erro


if __name__ == "__main__":
    main()
