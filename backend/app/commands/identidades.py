"""Concessão de papel separado e aplicação administrativa da fila da #207."""

import argparse
import json
import sys
from time import monotonic
from app.core.database import SessionLocal
from app.repositories import identidade_docente_repository as repo
from app.services.identidade_docente_service import aplicar_confirmadas, consolidar_locais


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="acao", required=True)
    papel = sub.add_parser("papel")
    papel.add_argument("email")
    papel.add_argument("permissao", choices=["conceder", "revogar"])
    aplicar = sub.add_parser("aplicar")
    aplicar.add_argument("--confirmo-janela-sem-escritores-e-backup", action="store_true")
    locais = sub.add_parser("locais", help="Prévia do fallback por nome + unidade")
    locais.add_argument("--aplicar", action="store_true")
    locais.add_argument("--confirmo-janela-sem-escritores-e-backup", action="store_true")
    args = parser.parse_args()
    inicio = monotonic()

    def progresso(numero, total, resultado):
        print(
            f"[{numero}/{total}] {resultado['estado']} — "
            f"{monotonic() - inicio:.1f}s (resultado salvo no banco)"
            if args.acao == "aplicar" or getattr(args, "aplicar", False)
            else f"[{numero}/{total}] {resultado['estado']} — prévia sem escrita",
            file=sys.stderr,
            flush=True,
        )

    with SessionLocal() as db:
        if args.acao == "papel":
            repo.conceder(db, args.email, args.permissao == "conceder")
            db.commit()
        else:
            if (args.acao == "aplicar" or args.aplicar) and (
                not args.confirmo_janela_sem_escritores_e_backup
                or db.bind.dialect.name != "postgresql"
            ):
                parser.error(
                    "Aplicação exige PostgreSQL, backup conferido e janela sem API/importadores/escritores."
                )
            resultados = (
                aplicar_confirmadas(db, progresso)
                if args.acao == "aplicar"
                else consolidar_locais(db, args.aplicar, progresso)
            )
            print(json.dumps(resultados, ensure_ascii=False))
            if any(r["estado"] == "BLOQUEADA" for r in resultados):
                raise SystemExit(2)


if __name__ == "__main__":
    main()
