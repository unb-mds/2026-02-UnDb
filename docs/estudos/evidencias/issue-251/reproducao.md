# Reprodução e validação — Issue #251

[Avaliação técnica](../../avaliacao-busca-autocomplete-issue-251.md) · [Tabelas de resultados](resultados.md)

## Limites e arquivos

O ensaio é documental e independente da aplicação. `preparar.py` usa somente SQLite em memória,
importa os models/repositories da revisão analisada e produz `dataset.json`. `medir.mjs`
cria PostgreSQL WASM em memória, executa SQL parametrizado e produz `resultados.json`.
`resumir.py` gera `resultados.md` desses arquivos. Não existem migrations de produto neste diretório.

Não configurar `DATABASE_URL` de produção para reproduzir. A preparação força SQLite e chave
sintética antes de importar os módulos. O runner Node não lê `.env` nem conexões do UnDb.
As ferramentas do ensaio devem ficar em venv/diretório temporário, sem alterar dependências,
scripts, lockfiles ou serviços do projeto.

## Execução medida em 15/11/2026

- Fonte: `develop` remoto `cd7a27c9b7835d1d42967bdc6d51e9596b8a952f`, consultado por fetch HTTPS.
- Windows, Node v24.21.0, Python 3.14.7, SQLAlchemy 2.1.8, PGlite 0.5.16.
- PostgreSQL 18.6 WASM, `pg_trgm` 1.6, collation `C`, ctype `C.UTF-8`.
- Um aquecimento e 30 repetições por consulta e variante; execuções sequenciais, sem carga HTTP.
- CPU, ponte WASM, cache e ordem das medições influenciam o resultado. Não foi medido throughput,
  partida a frio, consumo de compute Neon ou latência de usuário.
- Execução anterior identificou que `SHOW lc_ctype` não é parâmetro reconhecido nessa versão;
  metadado foi obtido em `pg_database`. Essa tentativa incompleta não foi usada nas tabelas.
- O primeiro runner com Meilisearch não concluiu por bloqueio do executável; o resultado final
  arquivado foi gerado novamente com o ramo Meilisearch desabilitado. A variante literal foi
  acrescentada ao ensaio e a rodada final gerou as três colunas medidas.

## Comandos de reprodução local

Em PowerShell, na raiz da revisão analisada, usar um venv próprio. O exemplo instala somente
as bibliotecas necessárias à preparação; o ambiente desta execução também continha as demais
dependências existentes de `backend/requirements.txt`, para executar os testes relacionados.

```powershell
python -m venv venv/issue-251
& venv/issue-251/Scripts/python.exe -m pip install SQLAlchemy==2.1.8 python-decouple==3.8

$ensaio251 = Join-Path $env:TEMP 'undb-issue-251'
New-Item -ItemType Directory -Path $ensaio251 -Force | Out-Null
$env:NPM_CONFIG_CACHE = Join-Path $ensaio251 'npm-cache'
npm install --prefix $ensaio251 --ignore-scripts --no-audit --no-fund @electric-sql/pglite@0.5.16
$env:PGLITE_PACKAGE = Join-Path $ensaio251 'node_modules/@electric-sql/pglite'
Remove-Item Env:MEILI_BINARY -ErrorAction SilentlyContinue

& venv/issue-251/Scripts/python.exe docs/estudos/evidencias/issue-251/preparar.py
node docs/estudos/evidencias/issue-251/medir.mjs
& venv/issue-251/Scripts/python.exe docs/estudos/evidencias/issue-251/resumir.py
```

`preparar.py` sobrescreve somente seu dataset; os outros dois scripts sobrescrevem seus
resultados/tabelas. Tempos e timestamp devem mudar entre máquinas; os UUIDs e julgamentos são
determinísticos. A asserção de paridade compara os conjuntos SQLite/PostgreSQL dos 26 casos,
não sua ordem: a apresentação baseline usa o mesmo `Intl.Collator` do frontend.

A consulta pg_trgm da POC desempata por nome/UUID no PostgreSQL; a política futura de
desempate por unidade/código descrita na avaliação ainda é proposta. Limite e ranking são
experimentais e não equivalem ao comportamento aprovado das listagens existentes.

## Meilisearch: tentativa não executada

O executável Community oficial v1.56.2 foi obtido em
[GitHub Releases](https://github.com/meilisearch/meilisearch/releases/tag/v1.56.2).
SHA-256 conferido contra o digest da release:

```text
9434f678eeebc2d65418d4aa7b09dc99a5ccd0851927fbc0627cb23d011c1da9
```

A própria invocação `--help` foi bloqueada por “Uma política de Controle de Aplicativo bloqueou
este arquivo”; o runner recebeu `spawn UNKNOWN`, errno -4094. Docker também não estava
disponível: pipe `docker_engine` inexistente, sem daemon ativo. Nenhuma política foi alterada,
nenhum serviço remoto foi usado e não há resultado Meilisearch medido.

O ramo opcional de `medir.mjs` é material para uma futura tentativa em ambiente permitido,
**não validado**. Se `MEILI_BINARY` apontar a executável oficial permitido, ele tentará iniciar
processo oculto temporário em `127.0.0.1:17700`, sem analytics, com dados/chave sintéticos,
índices separados por tipo e diretório novo em TEMP. A porta deve estar livre. Ao finalizar,
encerra apenas o processo filho criado. Não instala serviço Windows. Revisar o runner antes
de executar; uma falha não deve ser interpretada como teste concluído.

Configurações planejadas: `searchableAttributes=[codigo,nome]`, exibição de
`id,nome,codigo,departamento,departamento_nome`, typo 5/9, sem typo no atributo `codigo`,
limite oito e comparação entre `matchingStrategy=last` e `all`. O runner aguarda tarefas
de indexação concluírem. Esses valores **não foram enviados a um serviço em execução**.

## Checks relacionados executados

Com as dependências **já declaradas** do backend em venv isolado e variáveis de teste,
a partir de `backend/`:

```powershell
$env:DATABASE_URL = 'sqlite+pysqlite:///:memory:'
$env:SECRET_KEY = 'ensaio-sintetico-251'
python -m unittest tests.test_api_institucional tests.test_reconciliacao_professores -v
```

Resultado: **20 testes, 19 aprovados, um ignorado** por exigir PostgreSQL nativo descartável
`undb_207_test`. Duração observada 0,849 s. Nenhum banco compartilhado foi acessado.
Não foram executados testes de novo frontend, integração PostgreSQL nativa ou carga real.

## Validação documental

A documentação usa a navegação existente de estudos do MkDocs. O novo estudo foi adicionado
a essa seção; os anexos são alcançados pelos links do estudo. Comando de validação, na raiz:

```powershell
mkdocs build --strict --site-dir site
git diff --check
```

Validação em 15/11/2026, com MkDocs 1.6.1 e Material 9.8.1 do ambiente documental existente:
**build estrito aprovado (exit 0)** e `git diff --check` aprovado. O comando é o mesmo
do workflow de documentação. Não houve erro ou warning de link/âncora. As páginas do estudo
e dos dois anexos foram incluídas na navegação; as outras páginas históricas ausentes de
`nav` continuam aparecendo como INFO. O tema instalado emite seu aviso próprio sobre o
futuro fim de suporte/alternativa Zensical; esse banner não foi suprimido nem houve mudança
de tema, dependência ou configuração para escondê-lo.

Uma conferência adicional do HTML gerado validou as três páginas novas, 367 links/âncoras
internos (incluindo a navegação) e 24 caminhos de código referenciados no SHA analisado,
sem problemas. Arquivos textuais da entrega também foram conferidos quanto a espaços finais.

A entrega foi copiada da worktree atualizada para `docs/estudos/` no checkout original,
junto da inclusão em `mkdocs.yml`, sem trocar/avançar sua branch. A base do diagnóstico
continua sendo o SHA remoto acima, e o build estrito foi repetido no local de entrega.
