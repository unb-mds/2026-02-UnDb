#!/bin/bash

set -eu

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
PYTHON="$PROJECT_DIR/.venv/bin/python"

cd "$BACKEND_DIR"

export PYTHONPATH="$BACKEND_DIR"

# arquivo de ambiente local que fica fora do Git
ENV_FILE="$HOME/.config/undb/importacao-sigaa.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Arquivo de ambiente não encontrado: $ENV_FILE" >&2
  exit 1
fi

set -a
. "$ENV_FILE"
set +a

exec "$PYTHON" \
  -m app.commands.importar_sigaa_agendado \
  --departamento "CIC=DEPTO CIÊNCIAS DA COMPUTAÇÃO" \
  --ano 2026 \
  --periodo 2