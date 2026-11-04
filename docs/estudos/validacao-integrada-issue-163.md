# Validação integrada RF20–RF22 — Issue #163

**Data:** 04/11/2026. **Responsável da issue/solicitante:** Nicolas.
**Execução técnica:** agente nesta sessão, sob autorização do solicitante.
**Revisor solicitado:** Gabriel (`gabrielrdaraujo`); revisão/aceite humanos pendentes.
**Estado:** verificações técnicas executadas; entrega para revisão, sem declarar merge ou encerramento da issue.
**Base:** `fa6ea376a7a56fec9417b66910d5f12c2a061dcc` em `develop`, mais as correções de teste desta entrega.

## Fontes e escopo

[RF20–RF22, AC20-01 a AC22-06 e R2-DEC-01 a R2-DEC-15](../requisitos.md),
[contrato de API](alinhamento-denuncias-issues-160-161.md),
[comentários #159](interface-comentarios-issue-159.md),
[fila #162](fila-moderacao-issue-162.md) e
[denúncia/agradecimentos #193](denuncia-agradecimentos-issue-193.md).
As PRs #192/#194/#196/#197 já estavam integradas. Não foram alterados requisitos,
modelo de dados, permissões, regras de produto ou código de produção nesta entrega.

O novo roteiro `frontend/tests/fluxo-moderacao-browser.mjs` cruza as três interfaces
com autenticação, FastAPI e PostgreSQL reais, sem substituir HTTP ou autorização:

1. Autor confirmado envia crítica acadêmica negativa; texto fica pendente e não público.
2. Moderador analisa/aprova pela fila. A versão anterior é substituída.
3. Visitante lê sem autoria identificável e registra dois relatos; conta sem e-mail
   confirmado registra outro e recebe 409 na repetição.
4. A fila mostra separadamente uma conta distinta e dois relatos de visitantes.
   O moderador mantém o texto; os relatos são encerrados, sem agradecimento.
5. A conta denuncia novamente; outro acesso de moderação remove a versão.
6. No próximo login da conta, agradecimento fica pendente enquanto a aba está oculta;
   após exibição visível, POST confirma consumo e GET retorna lista vazia.
7. Autor envia novo texto sem restaurar a versão removida; moderador aprova.
   Autor envia outro substituto e retira explicitamente a versão vigente: o substituto
   é cancelado e os critérios permanecem. A fila termina vazia.

Consultas auxiliares apenas conferem respostas reais; as escritas desse percurso são
feitas pelos formulários da aplicação. As contas/papéis e o texto publicado inicial são
fixtures sintéticas da `denuncia_browser_fixture.py`, criadas antes do roteiro.

## Falhas e correções de teste

| Evidência | Correção e verificação |
|---|---|
| [CI 41764883195](https://github.com/unb-mds/2026-02-UnDb/actions/runs/41764883195/job/126360816454): `document.body.innerText` executado antes de existir body | Leitura segura compartilhada em `browser-navigation.mjs`; ausência de body é carregamento. Somente erros transitórios de troca de contexto CDP são tolerados; TypeError inesperado, asserção e timeout continuam falhando. Limites e asserções não foram removidos |
| Revisão da PR #198: o polling de seleção repetia o clique enquanto a consulta do comentário estava em andamento, cancelando a requisição anterior | Aguarda o item habilitado na fila, clica uma única vez e apenas consulta `aria-pressed` até concluir a seleção; depois aguarda a análise interativa. O timeout de 25 segundos e as asserções permanecem |

Três testes determinísticos reproduzem body ausente, troca de contexto e preservação de
erros inesperados. A suíte completa de navegador passou e o runner de denúncia passou
em três repetições adicionais. Isso reduz a corrida conhecida; não prova ausência universal
de intermitência. Nenhum defeito funcional do produto foi confirmado nesta execução.

### Correção após a revisão da PR #198

Na reprodução controlada da revisão, uma consulta de 250 ms não concluía: os cliques
repetidos cancelavam as requisições até o timeout de 25 segundos. Após a correção,
as funções reais `analisar`, `aguardar` e `selecionar` foram exercitadas em simulação
controlada com consultas de 0, 250 e 1000 ms; no último caso, o item também demorou
350 ms para aparecer na fila. Todos os casos concluíram com um clique, uma consulta
concluída e nenhum cancelamento, aguardando também a análise interativa.

Nesta correção, os 61 testes frontend e a verificação de sintaxe do runner passaram.
Não houve nova execução local do percurso completo com navegador/PostgreSQL;
os resultados de integração abaixo pertencem à entrega original. O job de CI
`Moderation end to end (PostgreSQL)` permanece responsável por reproduzir esse percurso
no novo commit.

## Ambiente e resultados

Windows; Node **24.22.1**; Edge/Chromium **156.0.4314.58** headless;
Python **3.12.16** e PostgreSQL **16.15** em containers descartáveis exclusivos.
Banco vazio migrado até `20261101_03`; `alembic check` não identificou diferenças.
Não foram usados dados reais nem serviços de envio de e-mail externos.

| Verificação executada | Resultado |
|---|---|
| `node tests/run-tests.mjs` | **61 testes aprovados** |
| `python -m unittest discover -s tests -q` | **159 testes aprovados** |
| ESLint, TypeScript e `next build --webpack` | Aprovados; Webpack é o compilador suportado usado neste Windows. Script padrão do build preservado |
| `npm run test:browser` | Busca, avaliação, protótipo, fila, denúncia e comentários aprovados com HTTP controlado |
| `node tests/denuncia-browser.mjs`, três vezes adicionais | Todas aprovadas, preservando asserções de envio, privacidade, sessão e consumo |
| `python -m tests.integration_moderacao` | HTTP/PostgreSQL reais: limiar, concorrência, decisões, permissões, descarte, encerramento e agradecimentos aprovados; acrescentadas concessão/revogação operacional e autoria impedida |
| `npm run test:fluxo-moderacao` com fixture real | Percurso das três interfaces acima aprovado; **30 combinações** de etapa × largura (320/768/1280) × tema (claro/escuro), sem overflow horizontal |
| `python -m tests.fluxo_moderacao_check` após o roteiro real | Uma avaliação; critérios 4/MEDIO/chamada verdadeira/material BOM/recomendação verdadeira; nenhuma versão ativa, denúncia aberta ou mensagem pendente; versões substituídas sem texto e decisões com motivo/ator/data/transição |
| `mkdocs build --strict`, `git diff --check` e leitura YAML do workflow | Aprovados |

A integração de API testa o comando operacional de papel sem trocar a sessão: 403 antes,
200 após conceder e 403 após revogar. Caso de autoria do moderador retorna 403, conserva
pendência e não cria decisão; outro moderador pode decidir. Nenhum papel é concedido a
conta real por esses testes.

## Matriz dos critérios e decisões aprovadas

“Verificado” abaixo refere-se à evidência técnica indicada, sem substituir a revisão humana.

| Critério | Origem R2-DEC | Evidência executada e alcance |
|---|---|---|
| AC20-01 | 01/02/04 | Testes de comentário para 1/500 caracteres, roteiro de comentário e percurso integrado: avaliação salva, texto pendente e aprovação por papel autorizado |
| AC20-02 | 01/02 | Limites 0/501 no backend, ausência de texto e comentário inválido na interface; critérios persistem e texto anterior é preservado |
| AC20-03 | 01/03 | Schema público somente id/texto/data, identidade ausente na página e em respostas; agregado insuficiente não expõe os critérios individuais |
| AC20-04 | 04/05 | Roteiro de comentários e integração PostgreSQL: substituto pendente, rejeição com descarte, anterior publicado/suspenso preservado e aprovação sem transferência de denúncias |
| AC20-05 | 05/12 | Reenvio sem texto, retirada pela interface e conferência final no banco: uma avaliação, critérios preservados e substituto cancelado |
| AC20-06 | 03/04 | Crítica acadêmica negativa submetida e aprovada pela interface do moderador; política visível e nenhuma publicação/decisão automática. A avaliação humana de procedência continua sendo responsabilidade do moderador |
| AC21-01 | 06/07 | Percurso integrado: visitante e conta não confirmada; suíte de serviços/backend valida enum fechado, 422 e ausência de registro para motivo/schema inválido |
| AC21-02 | 06/07 | Repetição autenticada 409; dois relatos de visitantes separados da conta na fila; concorrência de repetição testada na API/PostgreSQL |
| AC21-03 | 08 | Integração PostgreSQL: 55 relatos anônimos não suspendem, 49 contas deixam publicado; corrida da 50ª produz uma suspensão, sem contar duplicadas/encerradas |
| AC21-04 | 12 | Integração real e testes de denúncia: versão substituída deixa de aceitar registro, relatos são encerrados na substituição/retirada, sem herança |
| AC21-05 | 11/15 | Percurso integrado: remoção gera mensagem à conta; login com aba oculta não consome; visibilidade confirma e apaga. Suspensão e propriedade da mensagem cobertas na integração de API |
| AC22-01 | 09/10 | Concessão/revogação pelo comando, sessão/permissões reais, visitante/conta comum/não confirmada impedidos; autoria ou denúncia própria rejeitadas |
| AC22-02 | 04/10 | Fila controlada cobre seis caminhos de decisão; API real cobre aprovar/rejeitar/manter/restaurar/remover. Percurso integrado cruza aprovar/manter/remover; critérios preservados |
| AC22-03 | 10/12 | Caso próprio permanece pendente sem decisão; outro moderador resolve. Texto retirado não pode ser restaurado (testes de moderação/integração) |
| AC22-04 | 07/13 | Fila mostra origens separadas e identidade interna autorizada; visitante/autor/denunciante recebem 401/403 nas consultas privadas; projeção pública não contém essas informações |
| AC22-05 | 13/14 | Confirmação de decisão e conferência no banco: ator, motivo, data, versão e transição; resposta exata sem cópia de texto/denúncias; encerramento elimina denúncias |
| AC22-06 | 14 | Teste determinístico na fronteira de sete dias preserva pendente/suspenso e apaga texto/decisão vencidos. Integração PostgreSQL confirma prazo gravado e descarte por consulta com fixture vencida |

## Reprodução e integração contínua

Dependências existentes de `frontend/package-lock.json` e `backend/requirements.txt`.
A API real precisa de PostgreSQL descartável migrado, `DEBUG=True`,
`CORS_ORIGINS=http://localhost:3100`, `UNDB_INTEGRATION_TEST=1` e porta 8000 livre.
O navegador usa 3100/9228 e perfil temporário, removido ao final.

```powershell
# Na raiz; substitua undb-teste-api pelo seu container isolado com backend/ em /app.
$fixture163 = Join-Path $env:TEMP 'undb-fluxo163-fixture.json'
docker exec undb-teste-api python -m tests.integration_moderacao
docker exec undb-teste-api python -m tests.denuncia_browser_fixture | Set-Content -Encoding utf8 $fixture163
$env:FLUXO_MODERACAO_FIXTURE_FILE = $fixture163
Push-Location frontend
npm ci
npm run build
npm run test:fluxo-moderacao
Pop-Location
Get-Content -Raw $fixture163 | docker exec -i undb-teste-api python -m tests.fluxo_moderacao_check
Remove-Item Env:FLUXO_MODERACAO_FIXTURE_FILE
Remove-Item -LiteralPath $fixture163
```

Neste Windows, o build foi `node node_modules/next/dist/bin/next build --webpack`.
Para a suíte controlada, libere 8000 e execute `npm test` e `npm run test:browser`.
Gere uma fixture nova por execução real. Remova somente os recursos descartáveis criados
para o teste. O novo job **Moderation end to end (PostgreSQL)** executa API integrada,
fixture, navegador e invariantes finais no CI; não altera proteções ou critérios de merge.

## Evidências visuais e limites

Capturas sintéticas de 320 px/tema escuro, inspecionadas sem corte de conteúdo ou overflow:
[leitura pública](evidencias/issue-163/publico-320-dark.png),
[fila e dados internos autorizados](evidencias/issue-163/moderacao-320-dark.png),
[agradecimento](evidencias/issue-163/agradecimento-320-dark.png).

Não houve smartphone físico, leitor de tela, pesquisa com usuários ou uso de dados reais.
Condições de retenção foram verificadas com tempo/fixtures controlados; não houve espera
real de sete dias. A escolha de aprovar/manter/remover no roteiro é uma ação automatizada
sob papel sintético de moderador; não é uma avaliação humana real de conteúdo.
A revisão de Gabriel e o aceite/merge permanecem pendentes. Não se afirma conclusão
de requisitos operacionais, SIGAA ou outras issues fora de RF20–RF22.
