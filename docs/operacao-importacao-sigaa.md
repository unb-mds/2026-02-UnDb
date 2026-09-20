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

## Verificação da execução

Após executar a rotina, o resultado pode ser consultado com:

```bash
docker compose exec db psql -U g7 -d g7 -c "
SELECT
    id,
    status,
    iniciada_em,
    finalizada_em,
    ofertas_extraidas,
    ofertas_processadas,
    erro
FROM importacao_execucoes
ORDER BY iniciada_em DESC
LIMIT 1;
"
```

A execução realizada em `2026-09-20` foi registrada na tabela
`importacao_execucoes` com status `falha`.

A falha foi causada por ofertas do SIGAA com mais de um docente. Essas ofertas
não são persistidas porque o modelo atual exige exatamente um docente por turma.
As ocorrências foram registradas no campo `erro`, enquanto as demais ofertas
continuaram sendo processadas.

## Limitação conhecida

Ofertas com dois ou mais docentes são registradas como erro individual.
Essa limitação pertence à modelagem da importação e não interrompe o
processamento das outras ofertas.