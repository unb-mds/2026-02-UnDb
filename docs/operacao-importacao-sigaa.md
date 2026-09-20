# Operação recorrente da importação do SIGAA

## Decisão de operação

A importação será executada por cron, fora da API, como rotina recorrente.

- Frequência: diariamente às 03:00
- Mecanismo: cron local
- Registro de execução: tabela `importacao_execucoes` no PostgreSQL
- Comando: `python -m app.commands.importar_sigaa_agendado`

## Como executar

```bash
cd backend
DATABASE_URL='postgresql+psycopg2://g7:senha123@127.0.0.1:51024/g7' \
SECRET_KEY='chave-local-de-teste' \
PYTHONPATH=. \
python -m app.commands.importar_sigaa_agendado \
  --departamento "CIC=DEPTO CIÊNCIAS DA COMPUTAÇÃO" \
  --ano 2026 \
  --periodo 2
