"""Servidor exclusivo da jornada sintética: transporte privado de e-mail fora dos logs."""

import os
from pathlib import Path

import uvicorn

from app.main import app
from app.services.email_service import get_email_sender


def main():
    if os.environ.get("UNDB_INTEGRATION_TEST") != "1":
        raise RuntimeError("Exige ensaio descartável explícito.")
    destino = Path(os.environ["E2E_EMAIL_FIXTURE_FILE"]).resolve()
    if destino.exists() or not destino.parent.is_dir():
        raise RuntimeError("Exige arquivo novo no diretório temporário privado do ensaio.")
    # O navegador só começa após /health; a caixa já existe, mesmo antes do primeiro envio.
    fd = os.open(destino, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)

    class TransporteSintetico:
        def enviar_confirmacao(self, destinatario, link):
            # Apenas dados do ensaio, fora de logging/stdout/artefatos versionados.
            fd = os.open(destino, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
                arquivo.write(f"confirmacao para {destinatario}: {link}\n")

    app.dependency_overrides[get_email_sender] = TransporteSintetico
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
