import argparse
import json
import sys

from app.commands.importar_sigaa import _departamento
from app.core.database import SessionLocal
from app.services.importacao_agendada_service import (
    executar_importacao_agendada,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Executa a importação agendada do SIGAA e registra o histórico."
    )

    parser.add_argument(
        "--departamento",
        action="append",
        type=_departamento,
        required=True,
        help="Formato CODIGO=ROTULO_SIGAA. Pode ser repetido.",
    )

    parser.add_argument("--ano", required=True)
    parser.add_argument("--periodo", required=True)

    args = parser.parse_args()

    try:
        with SessionLocal() as db:
            registro = executar_importacao_agendada(
                db,
                args.departamento,
                ano=args.ano,
                periodo=args.periodo,
            )

        resultado = {
            "id": str(registro.id),
            "status": registro.status,
            "iniciada_em": registro.iniciada_em.isoformat(),
            "finalizada_em": (
                registro.finalizada_em.isoformat()
                if registro.finalizada_em
                else None
            ),
            "ofertas_extraidas": registro.ofertas_extraidas,
            "ofertas_processadas": registro.ofertas_processadas,
            "erro": registro.erro,
            "resultado": registro.resultado_json,
        }

        print(json.dumps(resultado, ensure_ascii=False, indent=2))

        if registro.status != "sucesso":
            raise SystemExit(1)

    except Exception as erro:
        print(
            json.dumps(
                {
                    "status": "falha",
                    "erro": f"{type(erro).__name__}: {erro}",
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()