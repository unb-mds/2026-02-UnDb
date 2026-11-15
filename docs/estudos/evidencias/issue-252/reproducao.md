# Reprodução e validação — Issue #252

[Relatório](../../avaliacao-ofensas-disfarcadas-issue-252.md) · [Resultados](resultados.md)

## Ambiente e limites

Base `4d5dabf5343e324c369cf70316e778eb50801a6e`, Windows, Python 3.14.7,
SQLAlchemy 2.1.8, Ruff 0.17.3. O CI usa Python 3.12; não foi executado aqui.
As dependências de runtime já existiam no venv `venv/issue-251`; Ruff foi instalado
da declaração fixa `backend/requirements-dev.txt`. Nenhum manifest foi alterado.
O build documental usa o venv existente `venv/docs-audit-247`, MkDocs Material 9.8.1.

`avaliar.py` força conexão SQLite em memória e chave sintética antes de importar módulos;
não cria schema, não abre conexão, não recebe texto externo nem dispõe de opção para API.
Executa o filtro real e candidatos experimentais e usa `processar` real com repositórios,
auditoria, cota e IA substituídos. Não chama rotas públicas nem salva avaliações.
Os estados PUBLICADO são de objetos em memória. Não configurar banco/chave de produção.

## Reproduzir o corpus

Na raiz de uma worktree atualizada, com Python/venv e dependências já declaradas:

```powershell
python -m venv venv/issue-252
& venv/issue-252/Scripts/python.exe -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
$env:PYTHONUTF8 = '1'
& venv/issue-252/Scripts/python.exe docs/estudos/evidencias/issue-252/avaliar.py
& venv/issue-252/Scripts/python.exe -m unittest discover -s docs/estudos/evidencias/issue-252 -p test_avaliacao.py -v
& venv/issue-252/Scripts/python.exe -m ruff check --config backend/pyproject.toml docs/estudos/evidencias/issue-252
& venv/issue-252/Scripts/python.exe -m ruff format --check --config backend/pyproject.toml docs/estudos/evidencias/issue-252
```

O runner sobrescreve somente `resultados.json` e `resultados.md` ao lado do corpus.
Data UTC e HEAD mudam entre execuções; os hashes permitem conferir fontes e código.
Para reproduzir o baseline, conferir os hashes de arquivos do backend, não apenas o HEAD
documental. Os rótulos continuam propostos; o runner recusa uma lista de revisores não vazia
até que o protocolo/metadados sejam revistos para uma rodada homologada.

Saída medida: atual 8/24/0/24; NFKD 10/22/0/24; invisíveis 13/19/0/24;
homoglifos 15/17/0/24; separadores/repetições 22/10/0/24; leet 28/4/1/23;
exceção `4` 29/3/2/22. Ordem: TP/FN/FP/TN. Quatro testes da bancada aprovados.

## Verificar o backend sem dados compartilhados

Na mesma sessão PowerShell, antes de entrar em `backend`:

```powershell
$env:DATABASE_URL = 'sqlite+pysqlite:///:memory:'
$env:MIGRATION_DATABASE_URL = 'sqlite+pysqlite:///:memory:'
$env:SECRET_KEY = 'ensaio-sintetico-252'
$env:OPENAI_API_KEY = ''
$env:MODERACAO_AUTOMATICA_ATIVA = 'False'
$env:MODERACAO_FILTRO_ATIVO = 'False'
$env:MODERACAO_IA_ATIVA = 'False'
$env:MODERACAO_IA_DADOS_APROVADOS = 'False'
cd backend
python -m unittest tests.test_triagem tests.test_moderacao_automatica tests.test_moderacao tests.test_comentario tests.test_denuncia -v
python -m unittest discover -s tests -v
python -m unittest tests.test_migration_connection -v
python -m ruff check .
python -m ruff format --check .
python -m compileall -q app alembic
```

Usar o executável do venv preparado, ou ativá-lo antes dos comandos `python`.
Os testes de integração HTTP usam ASGI e SQLite em memória, com fixtures sintéticas existentes.
Testes que precisam de PostgreSQL nativo continuam opcionais; não substituir sua URL por banco real.

| Verificação executada em 15/11/2026 | Resultado |
|---|---|
| 64 testes específicos de moderação/fluxos | Todos aprovados |
| Descoberta completa backend | 275 testes: 271 aprovados, dois erros de cleanup, dois ignorados |
| Isolamento `tests.test_migration_connection` | Três testes: um aprovado e mesmos dois erros de cleanup |
| Ruff backend | Lint aprovado; 142 arquivos formatados |
| Ruff estudo | Lint e formatação dos dois scripts aprovados |
| Compilação app/Alembic | Aprovada |
| API real / combinada real | Não executadas, zero chamadas |
| PostgreSQL/migrações/e2e navegador | Não executados; Docker sem daemon, nenhum banco descartável provisionado |
| Frontend/TypeScript | Não executados; nenhum frontend/contrato alterado |

Erros da descoberta e do isolamento, em `TemporaryDirectory.cleanup`, após as asserções:

```text
test_explicit_migration_connection_does_not_migrate_runtime_database ... ERROR
PermissionError: [WinError 32] ... migration%170.db
test_without_override_preserves_existing_database_url_behavior ... ERROR
PermissionError: [WinError 32] ... runtime.db
Ran 275 tests in 10.972s
FAILED (errors=2, skipped=2)
```

É uma limitação reproduzida dos testes existentes neste ambiente Windows/Python 3.14,
com handle SQLite aberto na limpeza. Não se declarou a suíte aprovada nem alterou o
backend para corrigir esse ponto fora do escopo da avaliação.

## Documentação e Git

Na raiz, com as dependências `requirements-docs.txt`:

```powershell
python -m mkdocs build --strict --site-dir site
git diff --check
```

MkDocs estrito aprovado em 15/11/2026, build em 1,91 s. As páginas novas constam do menu;
os avisos informativos de páginas antigas fora do menu não interromperam o build.
`git diff --check` aprovado, inclusive após adicionar os arquivos ao índice.
Nenhum comando deste roteiro autoriza push, PR, merge, deploy ou alteração de produção.
Para ensaio real da API, solicitar ao PO a decisão específica descrita no relatório;
não habilitar `--openai` do comando anterior da #239 como se fosse avaliação destes 62 casos.
