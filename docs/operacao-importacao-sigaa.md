# Operação da importação do SIGAA

## Decisão operacional vigente

**Atualização de 10/11/2026:** a carga manual de graduação 2026.2 no Neon terminou
com sucesso, com 6.571 ofertas extraídas/processadas e sem erro, conforme o
resumo fornecido pelo operador. [Resultado, contagens e limites](estudos/importacao-neon-2026-11-10.md).
Não houve comprovação de cron remoto ou workflow SIGAA ativo. A #164 acrescenta
um workflow versionado e auditoria de cobertura; publicação/configuração e uma
execução automática real ainda precisam de evidência. Os perfis
abaixo não representam comprovação de agendamento ativo. O
[guia de hospedagem](hospedagem.md) descreve a configuração pública e os segredos.

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

## Workflow GitHub Actions preparado na #164

O arquivo `.github/workflows/sigaa-importacao.yml` executa o importador fora da
API, sem depender de um processo contínuo no Render. Não executa migrations.
Agendamento e disparo manual estão restritos a `main`; integrar em `develop`
não ativa a rotina. O job fica desabilitado para agendamento enquanto
`SIGAA_PERFIL` não for configurado. O disparo manual é uma ação explícita do
operador e não depende do perfil. A execução sempre usa `--todas-unidades`.

Configurar em **Settings → Secrets and variables → Actions**:

| Tipo | Nome | Configuração privada ou operacional |
|---|---|---|
| Secret | `SIGAA_DATABASE_URL` | Conexão direta/TLS do importador no banco correto; nunca usar `undb_api` |
| Secret | `SIGAA_SECRET_KEY` | Configuração privada exigida pelo backend |
| Variable | `SIGAA_ANO` | Ano acadêmico com quatro dígitos, confirmado pelo operador |
| Variable | `SIGAA_PERIODO` | `1` ou `2`, confirmado pelo operador |
| Variable | `SIGAA_PERFIL` | `diario` na matrícula ou `semanal` fora dela; ausente/outro valor não executa por agenda |

Os dois eventos de agenda usam `America/Sao_Paulo`, às 03:00, um diário e outro
aos domingos. A condição do job seleciona somente o evento correspondente ao
perfil, inclusive no domingo: não há duas importações no mesmo dia por causa
dos dois eventos. Manter desativado qualquer cron externo para o mesmo banco.
A concorrência do workflow serializa suas execuções, sem cancelar a que já está
em andamento; não protege contra uma importação iniciada fora do GitHub.

Os [eventos agendados do GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule)
usam a branch padrão e podem sofrer atrasos. O job tem limite de 350 minutos;
a carga manual registrada levou cerca de 221 minutos. Timeout, cancelamento ou
indisponibilidade do banco podem deixar o histórico `em_andamento`; verificar a
execução antes de repetir. O processo persiste por unidade, portanto uma
interrupção não desfaz automaticamente unidades já comitadas.

### Papel do importador

Usar um papel separado da API e das migrações. Criar uma vez como administrador:

```sql
CREATE ROLE undb_importador WITH LOGIN
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
```

Definir senha por mecanismo privado e aplicar os GRANTs versionados em
`scripts/sql/164-acesso-importador.sql`. Eles permitem escrever no catálogo e no
histórico, e substituir vínculos docentes de turmas; não permitem acessar
contas, avaliações, comentários ou alterar schema. Conferir também privilégios
herdados e `PUBLIC`. Guardar a conexão resultante apenas em `SIGAA_DATABASE_URL`.
O papel `undb_api` da #170 permanece sem essas permissões administrativas de dados.

### Auditoria e histórico

A lista esperada é enumerada antes da coleta e comitada em
`importacao_execucoes.departamentos`. O JSON registra `origem_unidades` como
`formulario_sigaa` ou `lista_explicita`. Não há constante de 211 unidades: o
denominador é o formulário efetivamente enumerado naquela execução.

O workflow pede `--auditoria <arquivo>` ao comando existente. Ao finalizar,
compara os códigos esperados com o resultado completo e falha se houver unidade
ausente, inesperada, repetida, com falha, contagem inválida/divergente ou período
incompatível. Unidades consultadas com sucesso e zero ofertas são válidas.
O relatório inclui a lista esperada, lacunas, ID e timestamps da execução; não
inclui mensagens de exceção privadas, credenciais, contas ou avaliações.

O artefato `sigaa-cobertura-<run_id>-<tentativa>` guarda o relatório por 30 dias,
inclusive nas falhas que chegaram a produzir auditoria. O arquivo bruto de logs
não é publicado; detalhes de falha ficam no histórico privado do banco. Falhas
antes da conexão/registro ou encerramento forçado podem não gerar artefato.
Baixar a evidência necessária e preservar seu vínculo ao run antes de expirar.

Também é possível auditar **um ID explícito** de uma execução anterior, sem
reimportar, acessar o SIGAA ou alterar o banco, a partir de `backend/`:

```bash
python -m app.commands.auditar_importacao_sigaa \
  --execucao <UUID_DO_HISTORICO> --saida cobertura.json
```

Código 0 significa correspondência completa entre a lista registrada e o
resultado; código 1 sinaliza divergências ou execução não bem-sucedida. Em
históricos antigos sem `origem_unidades`, a auditoria informa `nao_registrada` e
`cobertura_formulario_verificada=false`, mesmo que a lista registrada confira.
Isso não deve ser interpretado como prova independente de que o formulário
inteiro foi enumerado. A comparação da carga manual anterior ainda precisa da
lista e do resultado completos do operador. Não versionar dumps nem logs brutos.

Para concluir a #164: publicar em `main`, configurar segredos/perfil/período,
validar um disparo manual e depois uma execução **agendada**, conferir histórico
e auditoria e registrar as evidências. Os testes locais usam dados simulados e
não concluem a cobertura da carga real de novembro.

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
