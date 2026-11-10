"""Audita uma execução específica sem acessar o SIGAA ou alterar o banco."""

import argparse
import json
from pathlib import Path
from uuid import UUID

from app.core.database import SessionLocal
from app.repositories.importacao_execucao_repository import obter_por_id
from app.services.auditoria_importacao_service import auditar_registro


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execucao", required=True, type=UUID)
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    with SessionLocal() as db:
        registro = obter_por_id(db, args.execucao)
        if registro is None:
            parser.error("execucao nao encontrada")
        relatorio = auditar_registro(registro)
    conteudo = json.dumps(relatorio, ensure_ascii=False, indent=2)
    if args.saida:
        args.saida.write_text(conteudo, encoding="utf-8")
    print(conteudo)
    raise SystemExit(0 if relatorio["completa"] else 1)


if __name__ == "__main__":
    main()
