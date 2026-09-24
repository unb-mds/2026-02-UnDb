# Verificação da execução do frontend — Issue #36

**Data:** 18/09/2026 (America/Sao_Paulo).
**Escopo:** build e execução local/Compose, comunicação navegador/API e Next.js/API,
empacotamento standalone e preservação das rotas existentes.

## Ambiente e isolamento

- Base: `develop`, commit `915a9d5`, igual a `origin/develop` após `git fetch origin`.
- Windows: Node.js 24.21.0, npm 11.19.0, Next.js 16.3.5.
- Ubuntu 26.04 no WSL: Docker Engine 29.1.3 e Compose 2.40.3, instalados com autorização.
- Projeto Compose exclusivo `undb-issue36`, volume `undb-issue36_postgres_data` criado vazio.
- Somente valores fictícios de `backend/.env.example`; nenhum segredo real ou dado do SIGAA.
- Imagens `node:24-bookworm-slim`, `python:3.12-slim` e `postgres:16`.

Os comandos Docker abaixo foram executados na raiz pelo WSL como root para acesso ao
daemon. Isso não muda o usuário da aplicação: o frontend executa com UID 1000 (`node`).
No PowerShell, o prefixo utilizado foi `wsl -d Ubuntu -u root --`.

## Comandos e resultados

| Comando | Resultado observado |
|---|---|
| `cd frontend && npm run lint` | ESLint sem erros ou avisos |
| `cd frontend && npm run build` | Build e TypeScript aprovados; três rotas com parâmetros renderizadas por requisição |
| `npm run start -- --hostname 127.0.0.1 --port 3100` (em `frontend/`) | Servidor pronto; início, buscas e detalhe com HTTP 200 |
| `npm run dev -- --hostname 127.0.0.1 --port 3101` (em `frontend/`) | Servidor pronto; início e detalhe com HTTP 200 |
| `docker compose -p undb-issue36 --env-file backend/.env.example config --quiet` | Configuração válida |
| `docker compose -p undb-issue36 --env-file backend/.env.example up --build -d --wait --wait-timeout 120` | Imagens construídas, migrações aplicadas e três serviços iniciados; banco/frontend saudáveis |
| `docker compose -p undb-issue36 --env-file backend/.env.example up --no-build` | Execução em primeiro plano durante os testes |
| `docker compose -p undb-issue36 --env-file backend/.env.example ps` | Backend em execução; PostgreSQL e frontend com health check saudável |
| `docker compose -p undb-issue36 --env-file backend/.env.example exec -T backend alembic current` | `20260917_02 (head)` |
| `docker compose -p undb-issue36 --env-file backend/.env.example exec -T backend alembic check` | `No new upgrade operations detected` |
| `docker compose -p undb-issue36 --env-file backend/.env.example run --rm --no-deps -v "$PWD/backend/tests:/app/tests:ro" backend python -m unittest discover -s tests -v` (Bash) | 51 testes aprovados |
| `docker image history --no-trunc --format json undb-issue36-frontend` | 17 camadas inspecionadas; servidor/assets copiados do builder; nenhum segredo do projeto identificado |
| `docker compose -p undb-issue36 --env-file backend/.env.example restart frontend` | Frontend reiniciado; smoke HTTP repetido com sucesso |
| `git diff --check` | Sem erros de whitespace |

O build Docker executou `npm ci` do lockfile e `npm run build` sem reutilizar
`node_modules` ou `.next` do Windows. O npm reportou zero vulnerabilidades nessa execução
e um aviso sobre o script de instalação de `unrs-resolver`; o build concluiu normalmente.
Isso não representa uma auditoria geral de segurança.

O WSL encerrou a distribuição após uma chamada destacada ficar ociosa, parando os
containers. Os logs mostraram desligamento normal; manter `compose up` em primeiro plano,
como no README, permitiu executar todas as verificações. Nenhum ajuste de aplicação foi
necessário para esse comportamento do ambiente.

## Integração HTTP e navegador

Foi inserida uma fixture sintética no PostgreSQL isolado usando os modelos SQLAlchemy:
um professor (`36000000-0000-0000-0000-000000000001`, `Docente Teste Docker`), uma disciplina
(`36000000-0000-0000-0000-000000000002`, `TESTE0036`, `Disciplina Teste Docker`), uma unidade
e uma turma ativa ligando os dois. Nenhuma avaliação foi cadastrada.

Scripts temporários de verificação, fora do versionamento em `frontend/.next/issue36/`,
executados com `node frontend/.next/issue36/http-smoke.mjs` e
`node frontend/.next/issue36/browser-smoke.mjs`, verificaram:

- HTTP 200 e conteúdo esperado em `/`, `/professores`, `/disciplinas`, detalhe de
  professor, comparação da disciplina e avaliação agregada do par cadastrado.
- Os três caminhos dinâmicos renderizaram dados reais da API/PostgreSQL em containers;
  o par sem avaliações mostrou o estado de dados insuficientes.
- Professor e disciplina inexistentes retornaram HTTP 404 para requisições com
  `User-Agent: Googlebot`, que evita streaming antecipado na verificação do status.
- CSS retornou HTTP 200 e continha `.flex` e `.text-accent`; fontes Geist `.woff2` e
  `public/file.svg` também retornaram HTTP 200.
- `GET /api/professores?nome=docker` e `GET /api/disciplinas?codigo=TESTE0036` retornaram
  um registro e `Access-Control-Allow-Origin: http://localhost:3000`.
- `GET /health` da API retornou HTTP 200.
- Edge headless: digitação nos campos de busca, resultado visível e clique até o detalhe
  de professor e a comparação de disciplina. As chamadas do navegador foram para
  `http://localhost:8000`, sem acesso a `http://backend:8000` e sem falhas de CORS.
- As páginas locais em portas 3100/3101 também consultaram a API usando o fallback da
  URL pública, sem `API_INTERNAL_URL` configurada.

O primeiro script de navegador tentou digitar antes da hidratação do React; foi ajustado
para aguardar os handlers. Também passou a distinguir cancelamentos normais de prefetch
RSC durante navegação de falhas de rede. A execução final passou sem mudança no produto.

Para repetir a verificação HTTP com dados existentes no seu ambiente, inicie a composição,
obtenha IDs válidos nas buscas e consulte os caminhos abaixo, substituindo os IDs:

```bash
curl -f http://localhost:3000/
curl -f http://localhost:8000/health
curl -f -H 'Origin: http://localhost:3000' -i 'http://localhost:8000/api/professores?nome=docker'
curl -f http://localhost:3000/professores/ID_PROFESSOR
curl -f http://localhost:3000/disciplinas/ID_DISCIPLINA
curl -f http://localhost:3000/professores/ID_PROFESSOR/disciplinas/ID_DISCIPLINA
```

No navegador, repita as duas buscas e navegue pelos links dos resultados; confira no painel
Network que a API pública responde e que nenhum pedido tenta resolver o hostname `backend`.

## Conteúdo da imagem e revisão

Uma inspeção por Node dentro do container confirmou UID diferente de zero, presença de
`/app/server.js`, ausência de arquivos `.env*` em `/app` e ausência de TypeScript, Tailwind
e ESLint no `node_modules` final. Os bundles públicos não contêm `http://backend:8000`.
A primeira tentativa de inspeção via shell teve interpretação incorreta de aspas entre
Windows e WSL; seu resultado não foi usado como evidência e a verificação foi refeita
com o script Node por stdin (`inspect-image.mjs`).

O diff foi revisado quanto a escopo, endereços entre containers, variáveis de build/runtime,
assets do standalone e preservação do fluxo local. A atualização da skill Docker é uma
correção de referências (`EXTEND`, versão `0.1.1`), conferida pelo checklist de
`skill-authoring`; mantém `proposed`, portabilidade e fronteiras de aprovação.

## Limites

- A checagem pontual não introduz suíte permanente de interface.
- Dados sintéticos validam execução e integração; não substituem importação real do SIGAA
  nem revalidam todos os critérios de agregação visual.
- As evidências são de um ambiente; a validação por dois membros continua na #37.
- A proposta de execução permanece documentada para aceite humano no ADR 08; não houve
  promoção da skill Docker nem alteração remota de issues, branches ou PRs.
- Hosting, TLS e operação pública em produção não foram definidos ou testados.

## Retomada e revalidação — 19/09/2026

A retomada encontrou os onze arquivos desta entrega ainda sem commit na branch
`feature/36-execucao-containerizacao-frontend`, criada a partir de `915a9d5`.
Consultas somente de leitura à API do GitHub confirmaram `develop` nesse mesmo commit,
ausência de branch publicada ou PR da #36, referências à #36 nos épicos #11 e #13 e
#32 encerrada. A implementação existente foi preservada, sem necessidade de correção.

Foram executados novamente:

- `npm run lint` e `npm run build` em `frontend/`: aprovados, incluindo TypeScript
  e as três rotas dinâmicas renderizadas por requisição.
- `npm run start -- --hostname 127.0.0.1 --port 3100` e
  `npm run dev -- --hostname 127.0.0.1 --port 3101`: inicialização e consultas HTTP
  aprovadas, incluindo detalhe com dados da API pelo fallback público.
- `docker compose -p undb-issue36 --env-file backend/.env.example config --quiet`
  e `up --build`: configuração e reconstrução aprovadas; três serviços iniciados,
  frontend e PostgreSQL saudáveis. O volume sintético anterior foi reutilizado.
- `docker compose -p undb-issue36 --env-file backend/.env.example run --rm --no-deps
  -v /mnt/c/Users/vinic/Prog/MDS/2026-02-UnDb/backend/tests:/app/tests:ro backend
  python -m unittest discover -s tests -v` pelo WSL: 51 testes aprovados.
- `docker compose -p undb-issue36 --env-file backend/.env.example exec -T backend
  alembic check`: nenhuma operação de atualização detectada.
- Verificações Node por stdin: seis rotas HTTP 200 com conteúdo esperado e dois
  casos 404, tanto no container quanto no servidor local de produção; CSS Tailwind,
  fonte Geist e asset público servidos; buscas da API, CORS e `/health` aprovados.
- Edge headless via protocolo DevTools: buscas de professor e disciplina, clique
  até os detalhes, URL pública e ausência de falhas de rede/CORS confirmados.
- Inspeção Node por stdin dentro do frontend: usuário sem privilégios, servidor
  standalone presente, ausência de `.env*` e dependências de desenvolvimento na
  imagem final, sem URL interna nos bundles públicos.
- `git diff --check` e revisão do diff: sem problemas identificados no escopo.

O build local removeu os scripts temporários que estavam em `.next/issue36/`;
as verificações foram reexecutadas por stdin, sem depender desses arquivos gerados.
A primeira conexão DevTools ocorreu antes de o Edge ficar pronto; a repetição passou.
Essas falhas de preparação não exigiram alterações no produto. O npm em Docker
reportou zero vulnerabilidades e avisos sobre ESLint 9 e o script de `unrs-resolver`;
lint e build concluíram normalmente, sem atualização de dependências nesta issue.

Os critérios técnicos estão cobertos pela implementação e pelas evidências acima.
O aceite da estratégia pelos responsáveis de frontend/infraestrutura permanece na
revisão humana do ADR 08; não se presume aprovação coletiva nem conclusão oficial
da issue. Nenhum push, publicação de branch, criação de PR ou merge foi realizado.
