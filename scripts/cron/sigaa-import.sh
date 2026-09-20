#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"

cd "${BACKEND_DIR}"

export PYTHONPATH="${BACKEND_DIR}"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL não foi definida." >&2
  exit 1
fi

if [[ -z "${SECRET_KEY:-}" ]]; then
  echo "SECRET_KEY não foi definida." >&2
  exit 1
fi

ANO="$(date +%Y)"
MES="$(date +%-m)"

if (( MES <= 6 )); then
  PERIODO="1"
else
  PERIODO="2"
fi

python -m app.commands.importar_sigaa_agendado \
  --departamento "${SIGAA_DEPARTAMENTO:-CIC=DEPTO CIÊNCIAS DA COMPUTAÇÃO}" \
  --ano "${ANO}" \
  --periodo "${PERIODO}"