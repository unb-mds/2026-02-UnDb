# Operação recorrente da importação do SIGAA

## Decisão operacional vigente

A importação é executada fora da API pelo comando
`python -m app.commands.importar_sigaa_agendado`. O script
`scripts/cron/sigaa-import.sh` permite integrá-lo ao cron.

A política aprovada combina dois perfis, sempre no fuso `America/Sao_Paulo`:

- **durante o período de matrícula:** execução diária às 03:00;
- **no restante do semestre:** execução semanal, aos domingos às 03:00.

A troca de perfil deve acompanhar as datas do calendário acadêmico oficial da UnB. Essas
datas não ficam embutidas no código porque mudam a cada semestre; o responsável pela operação
ativa o perfil diário no início da matrícula e retorna ao perfil semanal quando ela terminar.

Cada execução cria uma linha em `importacao_execucoes` com status `em_andamento` e a atualiza
para `sucesso` ou `falha`, incluindo timestamps, contadores, erros e o resultado detalhado.

## Execução manual

Execute a partir de `backend/`, repetindo `--departamento` para todas as unidades que devem
ser atualizadas:

```bash
DATABASE_URL='postgresql+psycopg2://usuario:senha@host:5432/banco' \
SECRET_KEY='chave-configurada-no-ambiente' \
PYTHONPATH=. \
python -m app.commands.importar_sigaa_agendado \
  --departamento "CIC=DEPTO CIÊNCIAS DA COMPUTAÇÃO" \
  --departamento "MAT=DEPTO MATEMÁTICA" \
  --ano 2026 \
  --periodo 2
```

O comando retorna código `0` somente quando todas as unidades terminam com sucesso. Falhas
parciais ou totais retornam código `1`, sem impedir que o resultado seja registrado no banco.

## Configuração do script para cron

O script exige configuração explícita. Isso evita presumir o período acadêmico pelo mês civil
ou executar silenciosamente apenas para o CIC.

Variáveis obrigatórias:

- `DATABASE_URL` e `SECRET_KEY`: configuração do backend;
- `SIGAA_ANO`: ano com quatro dígitos;
- `SIGAA_PERIODO`: `1` ou `2`;
- `SIGAA_DEPARTAMENTOS`: unidades no formato `CODIGO=ROTULO_SIGAA`, separadas por `;`.

Exemplo de arquivo `/etc/undb/sigaa-import.env`:

```bash
DATABASE_URL='postgresql+psycopg2://usuario:senha@host:5432/banco'
SECRET_KEY='chave-configurada-no-ambiente'
SIGAA_ANO='2026'
SIGAA_PERIODO='2'
SIGAA_DEPARTAMENTOS='CIC=DEPTO CIÊNCIAS DA COMPUTAÇÃO;MAT=DEPTO MATEMÁTICA'
```

Proteja o arquivo porque ele contém credenciais:

```bash
chmod 600 /etc/undb/sigaa-import.env
```

Edite o agendamento com `crontab -e` e mantenha ativo **somente um** dos perfis abaixo. O
servidor deve usar o fuso `America/Sao_Paulo`; quando a implementação de cron aceitar
`CRON_TZ`, registre-o no próprio crontab.

Durante o período de matrícula, execute diariamente às 03:00:

```cron
CRON_TZ=America/Sao_Paulo
0 3 * * * /bin/bash -lc 'set -a; source /etc/undb/sigaa-import.env; set +a; /caminho/para/2026-02-UnDb/scripts/cron/sigaa-import.sh' >> /var/log/undb-sigaa-import.log 2>&1
```

No restante do semestre, execute aos domingos às 03:00:

```cron
CRON_TZ=America/Sao_Paulo
0 3 * * 0 /bin/bash -lc 'set -a; source /etc/undb/sigaa-import.env; set +a; /caminho/para/2026-02-UnDb/scripts/cron/sigaa-import.sh' >> /var/log/undb-sigaa-import.log 2>&1
```

Ao trocar de perfil:

1. consulte no calendário acadêmico oficial as datas de início e fim da matrícula;
2. substitua a expressão de agendamento, sem manter as duas entradas ativas;
3. execute o comando manualmente uma vez e confirme o novo registro no banco;
4. verifique no dia seguinte, ou no domingo seguinte, se o cron criou outra execução.

Atualize `SIGAA_ANO`, `SIGAA_PERIODO` e a lista completa de departamentos quando o período
acadêmico mudar. A enumeração e validação de cobertura das unidades continua rastreada na
Issue #27.

## Verificação da execução

Consulte o registro mais recente:

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

Para investigar uma falha, consulte também `departamentos` e `resultado_json`. Ofertas com
zero, um ou vários docentes são suportadas pela modelagem atual; erros registrados representam
falhas reais de coleta, validação ou persistência, e não uma limitação a um único docente.
