"""Reconciliação explícita de uma ocorrência provisória. Padrão: somente simulação."""

import argparse
import json
from uuid import UUID

from app.core.database import SessionLocal
from app.repositories.reconciliacao_professor_repository import (
    ReconciliacaoRecusada,
    aplicar,
    aplicar_grupo,
    planejar,
    planejar_grupo,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origem", required=True, type=UUID, action="append")
    parser.add_argument("--destino", required=True, type=UUID)
    parser.add_argument("--aplicar", action="store_true")
    parser.add_argument("--confirmo-mesma-pessoa", action="store_true")
    parser.add_argument("--evidencia", default="")
    args = parser.parse_args()
    if args.aplicar and (not args.confirmo_mesma_pessoa or not args.evidencia.strip()):
        parser.error("Aplicar exige --confirmo-mesma-pessoa e --evidencia.")
    with SessionLocal() as db:
        if args.aplicar and db.bind.dialect.name != "postgresql":
            parser.error("A aplicação operacional exige PostgreSQL e janela de manutenção.")
        try:
            operacao = aplicar if args.aplicar else planejar
            origens = args.origem[0]
            if len(args.origem) > 1:
                operacao = aplicar_grupo if args.aplicar else planejar_grupo
                origens = args.origem
            plano = (
                operacao(db, origens, args.destino, args.evidencia)
                if args.aplicar
                else operacao(db, origens, args.destino)
            )
            if args.aplicar:
                db.commit()
            else:
                db.rollback()
        except Exception as erro:
            db.rollback()
            if isinstance(erro, ReconciliacaoRecusada):
                parser.exit(2, f"Recusado: {erro}\n")
            raise
    print(json.dumps(plano, ensure_ascii=False, indent=2))
    if plano["estado"] == "bloqueada":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
