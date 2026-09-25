#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"

cd "${BACKEND_DIR}"

export PYTHONPATH="${BACKEND_DIR}"

for variavel in DATABASE_URL SECRET_KEY SIGAA_ANO SIGAA_PERIODO; do
  if [[ -z "${!variavel:-}" ]]; then
    echo "${variavel} não foi definida." >&2
    exit 1
  fi
done

if [[ ! "${SIGAA_ANO}" =~ ^[0-9]{4}$ ]]; then
  echo "SIGAA_ANO deve conter quatro dígitos." >&2
  exit 1
fi

if [[ ! "${SIGAA_PERIODO}" =~ ^(1|2)$ ]]; then
  echo "SIGAA_PERIODO deve ser 1 ou 2." >&2
  exit 1
fi

if [[ "${SIGAA_TODAS_UNIDADES:-}" == "1" ]]; then
  if [[ -n "${SIGAA_DEPARTAMENTOS:-}" ]]; then
    echo "Use SIGAA_TODAS_UNIDADES ou SIGAA_DEPARTAMENTOS, não ambos." >&2
    exit 1
  fi
  argumentos_origem=(--todas-unidades)
else
  if [[ -z "${SIGAA_DEPARTAMENTOS:-}" ]]; then
    echo "Defina SIGAA_TODAS_UNIDADES=1 ou SIGAA_DEPARTAMENTOS." >&2
    exit 1
  fi
  IFS=';' read -r -a departamentos <<< "${SIGAA_DEPARTAMENTOS}"
  argumentos_origem=()
  for departamento in "${departamentos[@]}"; do
    departamento="${departamento#"${departamento%%[![:space:]]*}"}"
    departamento="${departamento%"${departamento##*[![:space:]]}"}"
    if [[ -n "${departamento}" ]]; then
      argumentos_origem+=(--departamento "${departamento}")
    fi
  done

  if (( ${#argumentos_origem[@]} == 0 )); then
    echo "SIGAA_DEPARTAMENTOS não contém departamentos válidos." >&2
    exit 1
  fi
fi

python -m app.commands.importar_sigaa_agendado \
  "${argumentos_origem[@]}" \
  --ano "${SIGAA_ANO}" \
  --periodo "${SIGAA_PERIODO}"
