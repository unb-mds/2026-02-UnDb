# Denúncia e agradecimentos — Issue #193

**Estado:** implementação corrigida após revisão; aceite e merge pendentes.
**Data:** 03/11/2026. **Base revisada:** `bbffbe4`, PR #196.
**Fontes:** RF21/AC21-01/02/04/05 em [requisitos](../requisitos.md) e
[contrato das APIs #160/#161](alinhamento-denuncias-issues-160-161.md).

## Comportamento e correções

- A leitura pública usa `id`, `texto` e `created_at` da versão publicada, sem autoria.
  O diálogo envia somente um dos sete motivos fechados para
  `POST /api/comentarios/{versao_id}/denuncias`. Confirmação depende da resposta;
  404, 409 e 422 têm mensagens próprias. Não há protocolo, justificativa livre,
  contagem de denúncias ou indicação de suspensão na interface.
- Falha na leitura de comentários agora produz aviso de indisponibilidade e orientação
  para recarregar; não é convertida em ausência de comentários. Uma lista vazia válida
  continua apresentando o estado vazio.
- Login/logout bem-sucedidos notificam o layout já montado. A consulta de agradecimentos
  anterior é cancelada, mensagens antigas são removidas e respostas obsoletas são
  ignoradas. A troca de conta não reaproveita mensagens nem confirmações anteriores.
- `GET /api/agradecimentos` usa cookie e `no-store` e não consome mensagens. Cada banner
  confirma `POST /api/agradecimentos/{id}/exibido` somente após montar e entrar na área
  visível, com a aba visível. Falha no POST conserva a mensagem no servidor; foco ou
  mudança de visibilidade permitem tentar novamente. Nada é gravado em Web Storage.
- O teste de navegador separa responsividade e consumo único. O modo real usa login,
  denúncia, decisão de moderador e consultas reais; não depende de arrays da fixture HTTP.
  As consultas de inicialização têm timeout e o navegador temporário é fechado por CDP.

A base de leitura pública auxilia a #159; envio/edição/retirada e estados do autor continuam
sob responsabilidade daquela issue. Não há alteração de backend de produto, critérios
estruturados, limiar de suspensão, regras ou permissões de moderação.

## Verificações executadas nesta correção

Ambiente: Windows, Node 24.22.1, Edge/Chromium headless; API em Python 3.12 e PostgreSQL 16
em containers descartáveis exclusivos desta verificação, com migrations até `20261101_03`.

| Verificação | Evidência e alcance |
|---|---|
| `node tests/run-tests.mjs` | 46 testes aprovados: suíte de serviços existente e regressões de notificação de sessão; motivos fechados, parâmetros, cookies, 404/409/422, agradecimentos e 204 |
| `node node_modules/eslint/bin/eslint.js .` | Lint do frontend |
| `node node_modules/typescript/bin/tsc --noEmit` | Tipos, após geração de tipos das rotas pelo Next |
| `node node_modules/next/dist/bin/next build --webpack` | Build de produção aprovado; o Turbopack falhou ao iniciar processo auxiliar neste Windows. A primeira tentativa no sandbox também não conseguiu obter fontes Geist. Não se alterou o script de build nem a fonte do produto |
| `node tests/denuncia-browser.mjs` | HTTP controlado: leitura/denúncia em 320 e 1280 px, claro/escuro; login/logout sem recarregar; conta diferente; duplicidade, 404, falha de consulta 503; mensagem não consumida com aba oculta e consumida após visibilidade |
| Mesmo runner com `DENUNCIA_FIXTURE_FILE` | API/PostgreSQL reais: quatro combinações de viewport/tema, denúncia SPAM por visitante, conta sem e-mail confirmado, duplicidade 409, remoção humana seguida de 404, geração de agradecimento, GET sem consumo, login/logout e primeira exibição com descarte confirmado por novo GET |
| `mkdocs build --strict --site-dir /tmp/undb-site`, Python 3.12 em container temporário | Documentação construída sem falhas |

A verificação real usa somente dados sintéticos gerados por UUID. Não representa teste em
smartphone físico, leitor de tela, todos os sete motivos pelo navegador, concorrência ou
homologação global de RF20–RF22. A enumeração dos sete motivos e 422 estão na suíte de
serviços; os cenários de concorrência e limiar permanecem nas evidências do backend.
Não há alegação de conclusão da #159 ou da validação integrada #163.

## Reprodução do teste real

A partir da raiz de uma cópia de teste, com Docker, Node, dependências do frontend
instaladas, Edge/Chromium e portas 8000, 3100 e 9227 livres, execute em PowerShell.
Use nomes novos se estes já existirem. As credenciais abaixo pertencem exclusivamente
à infraestrutura descartável. O banco é criado vazio e não recebe dados externos.

```powershell
docker network create undb-denuncia-test
docker run -d --name undb-denuncia-db --network undb-denuncia-test -e POSTGRES_DB=review -e POSTGRES_USER=review -e POSTGRES_PASSWORD=fixture-local postgres:16
docker build -t undb-denuncia-backend backend
$backendTeste = (Resolve-Path backend).Path
docker run -d --name undb-denuncia-api --network undb-denuncia-test -p 8000:8000 -e DATABASE_URL=postgresql+psycopg2://review:fixture-local@undb-denuncia-db:5432/review -e SECRET_KEY=fixture-local -e DEBUG=True -e CORS_ORIGINS=http://localhost:3100 -e UNDB_INTEGRATION_TEST=1 --mount "type=bind,source=$backendTeste,target=/app" undb-denuncia-backend sh -c 'alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000'
# Aguarde /health responder antes de gerar a fixture.
$fixtureTeste = Join-Path $env:TEMP 'undb-denuncia-fixture.json'
docker exec undb-denuncia-api python -m tests.denuncia_browser_fixture | Set-Content -Encoding utf8 $fixtureTeste
$env:DENUNCIA_FIXTURE_FILE = $fixtureTeste
Push-Location frontend
node node_modules/next/dist/bin/next build --webpack
node tests/denuncia-browser.mjs
Pop-Location
Remove-Item Env:DENUNCIA_FIXTURE_FILE
docker rm -f -v undb-denuncia-api undb-denuncia-db
docker network rm undb-denuncia-test
Remove-Item -LiteralPath $fixtureTeste
```

A fixture contém credenciais exclusivamente sintéticas. Gere uma nova fixture para cada
execução real: o teste remove a versão e consome o agradecimento. Para HTTP controlado,
remova `DENUNCIA_FIXTURE_FILE`, libere a porta 8000 e execute o runner sem containers.
`BROWSER_PATH` pode indicar outro Edge/Chromium instalado. O banco e os containers do
exemplo devem ser removidos ao terminar; nunca aponte este teste para um banco de uso real.
