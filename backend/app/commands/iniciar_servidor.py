"""Inicializa a API hospedada somente depois de aplicar as migrações."""

import os
import subprocess
import sys


def main() -> None:
    from app.core.config import PORT

    if not 1 <= PORT <= 65535:
        raise ValueError("PORT deve estar entre 1 e 65535")

    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
    # Substitui o processo para que o servidor receba SIGTERM diretamente.
    os.execv(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(PORT),
        ],
    )


if __name__ == "__main__":
    main()
