import argparse
import json

from app.core.database import SessionLocal
from app.services.sigaa_import_service import (
    DepartamentoImportacao,
    executar_importacao,
)


def _departamento(argumento: str) -> DepartamentoImportacao:
    departamento, separador, unidade_sigaa = argumento.partition("=")
    if not separador or not departamento.strip() or not unidade_sigaa.strip():
        raise argparse.ArgumentTypeError(
            "use CODIGO=ROTULO_SIGAA, por exemplo "
            "CIC=DEPTO CIENCIAS DA COMPUTACAO"
        )
    return DepartamentoImportacao(departamento.strip(), unidade_sigaa.strip())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Coleta ofertas publicas do SIGAA e persiste no backend."
    )
    parser.add_argument(
        "--departamento",
        action="append",
        type=_departamento,
        required=True,
        help="repetivel; formato CODIGO=ROTULO_SIGAA",
    )
    parser.add_argument("--ano", required=True)
    parser.add_argument("--periodo", required=True)
    args = parser.parse_args()

    with SessionLocal() as db:
        resultado = executar_importacao(
            db,
            args.departamento,
            ano=args.ano,
            periodo=args.periodo,
        )

    print(json.dumps(resultado.to_dict(), ensure_ascii=False, indent=2))
    raise SystemExit(0 if resultado.sucesso else 1)


if __name__ == "__main__":
    main()
