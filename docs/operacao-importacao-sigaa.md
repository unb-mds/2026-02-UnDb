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

Execute a partir de `backend/`. `--todas-unidades` consulta as opções atuais do formulário
público e importa as turmas de graduação de cada uma:

```bash
DATABASE_URL='postgresql+psycopg2://usuario:senha@host:5432/banco' \
SECRET_KEY='chave-configurada-no-ambiente' \
PYTHONPATH=. \
python -m app.commands.importar_sigaa_agendado \
  --todas-unidades \
  --ano 2026 \
  --periodo 2
```

O ID público de cada unidade é usado como código interno quando ela ainda não existe no
banco. Se uma importação anterior já associou esse ID a um código como `CIC`, o código
existente é preservado.

Para uma verificação limitada, substitua `--todas-unidades` por uma ou mais opções
`--departamento "CODIGO=ROTULO_SIGAA"`. Os dois modos são mutuamente exclusivos.

O comando retorna código `0` somente quando todas as unidades terminam com sucesso. Falhas
parciais ou totais retornam código `1`, sem impedir que o resultado seja registrado no banco.
Cada unidade tenta novamente até duas vezes após timeout ou redirecionamento inesperado
da consulta de turmas; a falha final permanece no histórico se as tentativas se esgotarem.

## Configuração do script para cron

O script exige configuração explícita. Isso evita presumir o período acadêmico pelo mês civil
ou executar silenciosamente apenas para o CIC.

Variáveis obrigatórias:

- `DATABASE_URL` e `SECRET_KEY`: configuração do backend;
- `SIGAA_ANO`: ano com quatro dígitos;
- `SIGAA_PERIODO`: `1` ou `2`;
- `SIGAA_TODAS_UNIDADES=1`: enumera todas as opções atuais do formulário; use este modo
  para a cobertura da Release 1;
- alternativamente, `SIGAA_DEPARTAMENTOS`: unidades no formato
  `CODIGO=ROTULO_SIGAA`, separadas por `;`, somente para execução limitada.

Exemplo de arquivo `/etc/undb/sigaa-import.env`:

```bash
DATABASE_URL='postgresql+psycopg2://usuario:senha@host:5432/banco'
SECRET_KEY='chave-configurada-no-ambiente'
SIGAA_ANO='2026'
SIGAA_PERIODO='2'
SIGAA_TODAS_UNIDADES='1'
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

Atualize `SIGAA_ANO` e `SIGAA_PERIODO` quando o período acadêmico mudar. No modo
`SIGAA_TODAS_UNIDADES=1`, a lista de unidades é lida novamente do SIGAA em cada execução;
uma falha nessa leitura é registrada em `importacao_execucoes`. A verificação de cobertura
da Release 1 está rastreada na Issue #131.

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
