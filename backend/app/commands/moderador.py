"""Operational role assignment, executed by the operator on the PO's instruction."""

import argparse

from app.core.database import SessionLocal
from app.repositories.moderacao_repository import definir_papel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email")
    parser.add_argument("acao", choices=("conceder", "revogar"))
    args = parser.parse_args()
    with SessionLocal() as db:
        definir_papel(db, args.email, args.acao == "conceder")
        db.commit()


if __name__ == "__main__":
    main()
