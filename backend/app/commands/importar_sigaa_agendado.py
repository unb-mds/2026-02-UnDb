import argparse
import json
import sys

from sqlalchemy.orm import Session

from app.commands.importar_sigaa import _departamento
from app.core.database import SessionLocal
from app.repositories import unidade_repository
from app.scrapers.sigaa_poc import listar_unidades_reais
from app.services.importacao_agendada_service import (
    executar_importacao_agendada,
)
from app.services.sigaa_import_service import DepartamentoImportacao, FONTE_SIGAA


def _todas_unidades(db: Session) -> list[DepartamentoImportacao]:
    solicitacoes = []
    for identificador, nome in listar_unidades_reais():
        unidade = unidade_repository.get_by_fonte_identificador_externo(
            db, FONTE_SIGAA, identificador
        )
        codigo = unidade.codigo if unidade is not None else identificador
        solicitacoes.append(DepartamentoImportacao(codigo, nome))
    return solicitacoes


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Executa a importação agendada do SIGAA e registra o histórico."
    )

    origem = parser.add_mutually_exclusive_group(required=True)
    origem.add_argument(
        "--departamento",
        action="append",
        type=_departamento,
        help="Formato CODIGO=ROTULO_SIGAA. Pode ser repetido.",
    )
    origem.add_argument(
        "--todas-unidades",
        action="store_true",
        help="Consulta todas as unidades do formulário público do SIGAA.",
    )

    parser.add_argument("--ano", required=True)
    parser.add_argument("--periodo", required=True)

    args = parser.parse_args()

    try:
        with SessionLocal() as db:
            if args.todas_unidades:
                departamentos = lambda: _todas_unidades(db)
            else:
                departamentos = args.departamento
            registro = executar_importacao_agendada(
                db,
                departamentos,
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
