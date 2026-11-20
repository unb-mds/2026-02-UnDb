# Revisão final local — 18/11/2026

## Escopo e base

Solicitação do responsável nesta conversa: revisão geral, reenvio de confirmação,
revisão da home e do catálogo e consulta das próprias avaliações na conta.

Base atualizada: `origin/develop`, commit `1817919`. Implementação isolada em
`codex/revisao-geral-final`, no worktree `.worktrees/revisao-geral-final`. O checkout
principal e suas alterações preexistentes foram preservados. Sem commit, push,
PR, merge, mudanças no Render ou alteração de produção nesta atividade.

A inspeção de código se concentrou em autenticação/sessão, consulta e envio de
avaliações, destaques, catálogo e suas camadas de serviço/repositório. As suítes
existentes ampliam a regressão para agregação, busca, importação, moderação,
retenção, limites e concorrência; sucesso dos testes não equivale a auditoria
exaustiva de todos os caminhos nem à validação da futura integração da Yasmin.

Fontes: pedido explícito do solicitante; `docs/requisitos.md`, inclusive RF27;
`specs.md`; implementação/contratos vigentes; skills de governança,
implementation, testing, code-review, FastAPI, Docker e páginas Next/Tailwind.

## Mudanças e findings tratados

| Constatação | Alteração | Evidência |
|---|---|---|
| O POST de reenvio existia, mas não estava acessível na interface | Nova página `/reenviar-confirmacao` e atalhos no login, cadastro e falha de confirmação | HTTP de reenvio já coberto no backend; novos cenários de UI verificam retorno interno, erro/retry e respostas temporárias |
| Minha conta só mostrava a sessão e saída | GET privado `/api/avaliacoes/minhas`, lista dos cinco critérios, data e professor/disciplina; paginação de dez itens | Quatro testes HTTP novos verificam autoria, paginação, exclusão lógica, sessão expirada, ausência de cache e omissão de dados do autor |
| Destaques disparavam até seis comparações adicionais e ocultavam falhas | Uma consulta aos destaques, cartões com nome/código/unidade e quantidade; estados carregando, vazio, erro e retry | Testes verificam uma chamada, links, textos longos e apresentação responsiva |
| Catálogo era lista de links azuis sem hierarquia e ficava fora do landmark principal | Cartões com contexto institucional; busca e catálogo dentro de um único `main` | Links e paginação HTML mantidos; inspeção visual em 320/768/1280 |
| Conta ficava estreita ao receber uma lista de avaliações | Moldura ampliada apenas na conta autenticada, cartões em duas colunas quando há espaço | Capturas responsivas; nenhum overflow observado |
| Imagem de testes não conseguia carregar TestClient do Starlette instalado | `httpx2==2.0.0` em requirements-dev; httpx preservado para os testes ASGI existentes | Suíte completa passa com dependências declaradas |
| Teste de migration codificava `%` do caminho SQLite como `%25`, criando outro arquivo | Corrigida somente a entrada do teste; preservado escape de interpolação do Alembic | Teste passa com nome de arquivo contendo `%` e confirma isolamento entre bancos |
| Next 16.3.5 e sharp transitivo estavam em intervalos afetados de advisories | Next e eslint-config-next 16.4.6; lockfile regenerado/validado no Node 24 Linux | Build Docker, regressão e auditoria de runtime após atualização |

A seção da home é **mais avaliadas**, conforme o contrato existente. Não há
contagem de visualizações; nenhum número de visitas foi inventado. Os critérios
agregados continuam na comparação por disciplina, respeitando insuficiência.
As respostas individuais só aparecem para o próprio usuário autenticado; comentários
e informações de moderação não são acrescentados ao contrato privado desta lista.
A expiração de sessão revalida a conta e descarta a lista, assim como logout.

## Verificações

- Backend no Docker com PostgreSQL 16 novo, banco descartável `ci`, sem dados de produção.
- `alembic upgrade head` em banco vazio: aprovado.
- `python -m unittest discover -s tests`: **456 testes, aprovado, dois ignorados**;
  inclui suites PostgreSQL de abuso, retenção, concorrência e votos.
- Integração HTTP com API/PostgreSQL reais: visitante 401, login de duas contas,
  envio e persistência de avaliação, consulta dos próprios critérios, isolamento
  entre contas, no-store, logout e reenvio neutro 202: aprovados. Dados sintéticos
  criados exclusivamente para esse ensaio foram removidos ao final, sem envio externo.
- Ruff check, Ruff format --check e compileall: aprovados.
- Frontend `npm test`: **99 testes aprovados**, incluindo seis novos de contratos,
  cancelamento, credenciais, respostas inválidas, reenvio e consulta única dos destaques.
- ESLint: aprovado.
- `npm ci` e build de produção no Docker, Next 16.4.6: aprovados, incluindo TypeScript.
- Navegador Brave headless, fixtures HTTP sintéticas: novas telas em **24 combinações**
  (quatro telas × três larguras × dois temas). Paginação, vazio, erro/retry, saída,
  reenvio com falha de rede/429/503, retorno seguro e confirmação inválida cobertos.
- Regressão de navegador após atualização de Next: **18 runners aprovados** (avaliação,
  moderação, denúncia, comentários, cabeçalho, identidades, transições, sessão,
  jornada, compartilhamento, destaques, recuperação de senha, equipe, SEO, solicitações,
  termos, votos e revisão final). A fixture do cabeçalho foi atualizada para responder
  ao novo GET de avaliações; antes disso, seu fallback 401 simulava uma expiração
  contraditória com a sessão autenticada da própria fixture.

Evidências locais em `output/revisao-final/`: capturas, logs e JSONs de auditoria.
Configuração do Docker fica em `.env` ignorado pelo Git dentro desse diretório;
somente credenciais novas do ambiente sintético. Não adicionar esses arquivos ao Git.

O build no host encontrou bloqueio de rede/fontes e restrição de porta do Turbopack.
A verificação de build adotada foi a do Docker; seu artefato foi extraído para os
runners locais existentes de navegador. Não foi alterada a stack para contornar isso.

## Dependências e riscos restantes

Auditoria npm antes: 20 nós afetados (1 crítico, 10 altos, 9 moderados).
Após atualização: 18 nós afetados (0 críticos, 9 altos, 9 moderados), todos em cadeias
de ferramentas de desenvolvimento. `npm audit --omit=dev`: **zero avisos** nessa
consulta. Isso não comprova ausência de vulnerabilidades desconhecidas, nem cobre
bibliotecas nativas, imagens base, Python ou versões efetivas em produção.

Os avisos residuais incluem ESLint/resolução de imports/padrões glob e c8/cobertura.
Algumas sugestões automáticas envolvem trocar versões principais ou downgrade de
ferramentas; não foram aplicadas como parte desta correção. Permanecem rastreáveis
à revisão de dependências da #266 e ao épico #272, sem declaração de aceite integral.

Fontes primárias consultadas:

- [Release Next 16.4.6](https://github.com/vercel/next.js/releases/tag/v16.4.6).
- [Aviso Next/ImageResponse](https://github.com/advisories/GHSA-vcvr-r3jv-pc5j).
- [Aviso de otimização SVG](https://github.com/advisories/GHSA-2464-fhr4-w9xw).
- [Aviso sharp/librsvg](https://github.com/advisories/GHSA-wq5f-xc86-pv6w).
- [TestClient Starlette](https://starlette.dev/testclient/).

O relatório histórico da #266 é mantido como histórico, sem sobrescrever suas
versões ou evidências com resultados desta revisão.

## Ambiente local deixado disponível

API, frontend e PostgreSQL do projeto Compose `undb-revisao-final` estão saudáveis.
Home, professores, disciplinas, conta e reenvio retornaram HTTP 200; `/health`
retornou `{"status":"ok"}`. Interface em `http://localhost:3000`, API em
`http://localhost:8000`. Banco isolado, sem importação da base real do SIGAA;
os registros do teste HTTP final foram removidos. O worker de descarte não foi
iniciado nesse smoke test; sua lógica foi coberta na suíte de retenção.

Para parar somente esse ambiente, na raiz do worktree:

```sh
docker compose --env-file output/revisao-final/.env -p undb-revisao-final stop
```

## Integração e produção

Antes de PR: aguardar a PR da Yasmin, comparar os escopos e revalidar o código
integrado na `develop`. Após a integração aprovada na `main`, repetir os fluxos
na versão final e verificar deploy/configuração/conexão/CORS/logs no Render.

Esta etapa não atesta envio real de e-mail, dados reais do SIGAA, funcionamento
em produção, observabilidade hospedada ou aceite da release. Um defeito bloqueante
na validação posterior volta para correção e nova verificação.

## Prévia solicitada pelo responsável

Após a revisão, o solicitante autorizou utilizar um backup local para visualizar as
mudanças. Em 18/11/2026 foi extraído somente o catálogo institucional do backup
`20261114-214243/antes-pendencias-finais.dump`: 69 unidades, 3.488 disciplinas,
8.280 registros docentes, 5.392 correspondências, 6.575 turmas e 8.280 vínculos.
Contas, sessões, tokens e comentários do backup não foram importados. O destino
é o banco novo do Compose `undb-revisao-final`, preservando o backup original.

Para a prévia foram criados um professor e 12 disciplinas marcados como
demonstração local, quatro contas fictícias e 30 avaliações demonstrativas.
A conta principal tem 12 avaliações, para exercitar a paginação. Os seis
destaques apresentados são identificados como DEMO LOCAL. Essa preparação é
restrita ao banco de prévia, sem alteração de código ou dados de produção.

## Ajuste da prévia mobile solicitado em 18/11/2026

Com o catálogo do backup, as páginas de professores/disciplinas tinham 100 cartões
por página e ultrapassavam 23 mil pixels de altura em 390 px. A paginação passa
a 12 itens, mantendo links HTML e acesso ao catálogo completo. No mobile, cartões
e cabeçalho da busca têm menos espaço decorativo; nomes e unidades continuam
legíveis, sem truncamento. Perfis mostram seis disciplinas inicialmente (duas
quando dentro de resultados de busca), com as restantes em um details acessível.

A pedido do solicitante, o título da home voltou para “Escolha seus professores
com a opinião de quem já cursou.” Os esclarecimentos de metodologia foram preservados.
O texto de apoio dos destaques também voltou à redação anterior.

Build Docker, TypeScript, ESLint e 99 testes de frontend aprovados após a mudança.
As medidas da prévia ficam em `output/mobile-ajuste/antes.json` e `depois.json`.

Conferência no site Docker real em 390 px: professores de 23.444 para 2.311 px;
disciplinas de 23.293 para 2.707 px; perfil demonstrativo com 12 disciplinas de
3.645 para 2.053 px. Verificados 320/390/768/1280, ausência de overflow, duas
páginas com 12 itens sem duplicação, expansão das disciplinas por Enter e título
anterior da home.

## Continuidade — 20/11/2026

Por solicitação explícita de Nicolas, a espera pela PR da Yasmin foi substituída
pela execução local do escopo pendente #265. Não havia PR aberta da autora ao
consultar o GitHub. `origin/develop` continua em `1817919`, sem commits novos a
conciliar. A [conferência de privacidade](privacidade-apis-265-revisao-final.md)
registra matriz atual, cinco novas regressões e correção de revalidação/limpeza
de dados na interface restrita de atendimento. A validação da main/hospedagem
permanece para depois; não foram feitos commit, push, PR ou merge.

Suíte backend no novo PostgreSQL descartável: 461 testes, dois ignorados.
Frontend: 99 testes. Build Docker/TypeScript e lint aprovados. Os resultados de
18/11 acima são históricos, não execução nova de cada verificação de produção.

Regressão ampla de 20/11 concluída: 18 runners de navegador aprovados com o build
final, incluindo atendimento revogado/resposta atrasada e catálogo em lotes de 12.
Conjunto e limitações em [implementação consolidada](revisao-geral-implementacao-2026-11-20.md).
