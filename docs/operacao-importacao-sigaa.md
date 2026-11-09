# Operação da importação do SIGAA

## Decisão operacional vigente

A importação é executada fora da API pelo comando
`python -m app.commands.importar_sigaa_agendado`. O script
`scripts/cron/sigaa-import.sh` permite integrá-lo ao cron.

Na Release 1, a importação é iniciada manualmente no ambiente local. A instalação
de uma rotina periódica (RF18) ficou para a Release 2.

A política de agendamento prevista para a Release 2 combina dois perfis, sempre no
fuso `America/Sao_Paulo`:

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

### Códigos de saída e tratamento de falhas

O comando CLI implementa uma política de término determinística para integração com ferramentas de automação e monitoramento:
- **Código `0` (Sucesso integral):** retornado apenas quando todas as unidades configuradas foram coletadas, validadas e persistidas sem nenhum erro.
- **Código `1` (Falha parcial ou total):** retornado se qualquer unidade falhar, se houver divergência entre as ofertas extraídas e o total reportado pelo SIGAA, se ocorrer timeout persistente nas requisições, ou caso ocorra exceção inesperada durante o processamento.

#### Tratamento de erros e tentativas (retries)
- **Tentativas automáticas:** cada unidade tenta novamente até 2 vezes (totalizando 3 tentativas com backoff linear de 1s e 2s) em caso de falha de conexão (`URLError`), timeout (`TimeoutError`) ou redirecionamento inesperado (`SigaaRedirecionadoError`).
- **Isolamento entre unidades:** a falha de uma unidade não aborta o processamento das demais. Cada unidade possui sua própria transação no banco.
- **Savepoints por oferta:** dentro de uma unidade, o salvamento de cada oferta é protegido por savepoint (`db.begin_nested()`). Caso uma oferta específica falhe (por exemplo, por dados corrompidos ou conflito de identidade), o erro é registrado e o processamento das outras ofertas da mesma unidade continua.

#### Efeitos sobre os dados existentes
- **Falha total na unidade (ex.: queda de conexão ou erro no commit):** a transação da unidade é desfeita via rollback. Os dados previamente persistidos dessa unidade no PostgreSQL permanecem inalterados.
- **Falha parcial na unidade:** as ofertas válidas são persistidas/atualizadas, mas a sincronização de inativação **não é disparada**. Portanto, nenhuma turma ausente é marcada como inativa se a coleta não tiver sido 100% íntegra.
- **Sucesso completo na unidade:** todas as ofertas são persistidas/atualizadas e as turmas do período que não apareceram no retrato atual do SIGAA são marcadas com `ativa = false`.
- **Registro persistente de histórico:** mesmo que a execução termine com falha parcial ou exceção fatal, o registro da tentativa é comitado em `importacao_execucoes` com `status = 'falha'`, preenchendo o campo `erro` com a mensagem/traceback para fins de auditoria.

## Configuração do script para cron (Release 2)

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

## Verificação da execução e histórico de auditoria

Cada execução do comando agendado registra uma linha na tabela `importacao_execucoes`.

### Estrutura do registro em `importacao_execucoes`

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | UUID (PK) | Identificador único da execução. |
| `status` | VARCHAR(20) | Estado do ciclo de vida: `em_andamento`, `sucesso` ou `falha`. |
| `iniciada_em` | TIMESTAMPTZ | Timestamp de início da execução. |
| `finalizada_em` | TIMESTAMPTZ | Timestamp de conclusão (ou término com erro). |
| `ano` | VARCHAR(4) | Ano letivo processado (ex.: `2026`). |
| `periodo` | VARCHAR(2) | Período acadêmico (ex.: `2`). |
| `departamentos` | JSON | Lista dos departamentos solicitados (`[{"departamento": "CIC", "unidade_sigaa": "..."}]`). |
| `ofertas_extraidas` | INTEGER | Soma das ofertas identificadas no HTML em todas as unidades. |
| `ofertas_processadas` | INTEGER | Soma das ofertas persistidas/atualizadas com sucesso. |
| `erro` | TEXT | Mensagens de erro consolidadas em caso de falha (ou `NULL` em sucesso). |
| `resultado_json` | JSON | Estrutura completa contendo o detalhe por unidade, tempos e listas de erros. |

### Consultas de auditoria

1. **Consultar o resumo da execução mais recente:**
   ```bash
   docker compose exec db psql -U g7 -d g7 -c "
   SELECT
       id,
       status,
       ano || '.' || periodo AS periodo,
       iniciada_em,
       finalizada_em,
       ofertas_extraidas,
       ofertas_processadas,
       COALESCE(erro, 'Nenhum erro') AS erro
   FROM importacao_execucoes
   ORDER BY iniciada_em DESC
   LIMIT 1;
   "
   ```

2. **Inspecionar o detalhamento por unidade (`resultado_json`):**
   ```bash
   docker compose exec db psql -U g7 -d g7 -c "
   SELECT
       id,
       jsonb_pretty(resultado_json::jsonb) AS resultado_detalhado
   FROM importacao_execucoes
   ORDER BY iniciada_em DESC
   LIMIT 1;
   "
   ```

3. **Verificar turmas ativas sincronizadas no período:**
   ```bash
   docker compose exec db psql -U g7 -d g7 -c "
   SELECT
       t.id AS turma_id,
       t.unidade_id,
       d.codigo AS disciplina,
       t.codigo AS turma,
       t.semestre,
       t.ativa,
       COUNT(p.id) AS qtd_professores
   FROM turmas t
   JOIN disciplinas d ON d.id = t.disciplina_id
   LEFT JOIN turmas_professores tp ON tp.turma_id = t.id
   LEFT JOIN professores p ON p.id = tp.professor_id
   WHERE t.semestre = '2026.2' AND t.ativa = true
   GROUP BY t.id, t.unidade_id, d.codigo, t.codigo, t.semestre, t.ativa
   LIMIT 10;
   "
   ```

Ofertas com zero, um ou vários docentes são suportadas pela modelagem relacional (`turmas_professores`); erros registrados representam
falhas reais de coleta, validação ou integridade de dados, e não uma restrição a um único docente.
