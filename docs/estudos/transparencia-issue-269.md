# Entrega local da Issue #269 — transparência e ciência

Data: 17/11/2026 (America/Sao_Paulo). Branch `feature/269-transparencia-termos`, baseada na
`develop` `62faab9` (PR #279). Implementação na worktree `issue-269`; checkout original
com alterações preexistentes preservado. Fonte: [RF26](../requisitos.md#rf26-transparencia-termos-e-ciencia-no-cadastro-269),
escopo consolidado da [#269](https://github.com/unb-mds/2026-02-UnDb/issues/269) e pedido
explícito do PO para executar toda a issue e declarar “sem fins lucrativos”.

## Critérios e resultado local

| Critério da #269 | Entrega / evidência |
|---|---|
| Inventário simples, reaproveitando T01–T18 e #279 | [Inventário consolidado](../transparencia.md), com origem, finalidade, acesso, fornecedor e descarte/limites; votos registrados como evolução ainda não presente na base |
| Política pública, versão/data e links | `/privacidade`, versão 2026-11-17; rodapé/cadastro/Sobre; sumário, referências e metadados próprios |
| Autoria, conta, acesso e limites | Política distingue autoria pública de vínculo interno e identificação contextual; atendimento manual, descarte e backups descritos conforme fatos disponíveis |
| Termos acadêmicos, independência e participação | `/termos-de-uso`, versão/data; projeto independente e sem fins lucrativos, sem endosso oficial comprovado; e-mail confirmado sem prova de experiência |
| Crítica legítima e moderação reais | Sem veto docente, rejeição automática pela IA ou ocultação por votos; 50 contas preservadas como gatilho, não mínimo de atendimento; notas independentes do texto |
| Ciência no cadastro, validada pelo servidor | Checkbox obrigatório/desmarcado, links em outra aba para preservar formulário; booleano estrito e versão atual; instante UTC gerado pelo servidor na mesma transação |
| Contas existentes | Par de colunas nulo, sem backfill/reaceite/bloqueio; login antigo e duplicação sem ciência fictícia verificados em SQLite e PostgreSQL |
| Requisitos/derivados e regressões | RF26, specs, visão, modelo de usuários, inventário e navegação sincronizados; testes e inspeção visual abaixo |

“Sem fins lucrativos” também aparece em Home/Sobre/rodapé. Não foi declarada pessoa
jurídica, garantia de anonimato, autorização de terceiros ou isenção legal por esse caráter.

## Verificações executadas

| Verificação | Resultado |
|---|---|
| `python -m unittest discover -s tests -v` | 345 testes, sem falhas, dois skips preexistentes de identidades/reconciliação |
| `python -m tests.integration_termos` em PostgreSQL local | Upgrade completo com conta anterior, `alembic check`, validação HTTP, persistência versão/instante, CHECK, login legado, downgrade e reaplicação aprovados |
| `python -m tests.integration_acesso` | Navegador → API real → adaptador de e-mail sintético local → PostgreSQL; cadastro/confirmar/login/retorno/persistência e 54 combinações aprovados |
| `npm test` | 83 testes aprovados |
| `npm run test:termos` | 18 combinações: 3 páginas × 3 larguras × 2 preferências do sistema; âncoras, canonical/Open Graph, rodapé, rótulos, teclado, checkbox inicial, bloqueios HTML/React, 422/nova tentativa, payload e reset aprovados |
| `node tests/jornada-247-browser.mjs` | Regressão de telas/retorno/cadastro/conta aprovada, HTTP controlado |
| `npm run lint` / `npm run build` | ESLint e build padrão Next.js/Turbopack, incluindo TypeScript, aprovados |
| `ruff check` / `ruff format --check` / `compileall` | Aprovados |
| `mkdocs build --strict` / `git diff --check` | Aprovados |

Ambiente: macOS, Python 3.12, Node do runtime local, Brave/Chromium headless. Dependências
frontend instaladas pelo lockfile, sem atualização; ambiente Python descartável usa os
requirements existentes e o adaptador de teste `httpx2` exigido pelo Starlette disponível.
Nenhuma dependência de produto nova. PostgreSQL 16.15 temporário obtido do pacote
`@embedded-postgres/darwin-arm64` 16.15.0-beta.19, exclusivo em loopback/porta 55469.
Banco `undb_269_test`, dados sintéticos e adaptadores sem envio de e-mail externo.
Servidor encerrado e diretório de dados eliminado após a validação.

A primeira tentativa de cadeia completa SQLite/SQL offline encontrou limitações em
migration anterior à tarefa. A migration nova teve DDL PostgreSQL isolado conferido e
foi posteriormente validada na cadeia completa em PostgreSQL real, incluindo reversão.
A primeira execução da suíte no sandbox encontrou dois bloqueios de socket; a execução
com sockets locais permitidos passou. Não houve alteração para contornar essas verificações.

## Inspeção visual e revisão

Leitura/teclado e ausência de rolagem horizontal verificados em 320, 768 e 1280 px.
O produto permanece escuro nas duas preferências do sistema. Viewports emulados
não representam teste com smartphone físico ou pesquisa com participantes.
Capturas inspecionadas: Termos em 320 px, Política em 1280 px e cadastro em 320/1280 px.
Os destaques de foco nas imagens são parte da verificação de teclado.

- [Termos em celular](evidencias/issue-269/termos-de-uso-dark-320.png).
- [Política em desktop](evidencias/issue-269/privacidade-dark-1280.png).
- [Cadastro em desktop](evidencias/issue-269/cadastro-dark-1280.png).
- [Resultados estruturados](evidencias/issue-269/resultados.json).
- [Hashes dos arquivos de implementação](evidencias/issue-269/fontes-sha256.json).

Revisão local do diff e do fluxo feita conforme `code-review`, contra RF26 e critérios
consolidados da issue, com atenção a retroatividade, exposição pública, validação antes de
efeitos, coerência editorial e migração. Sem findings pendentes nessa inspeção; não é
revisão independente, aceite formal ou aprovação de PR.

## Publicação e limites preservados

Implementação/verificações locais concluídas. Nicolas autorizou commit, push e abertura
da PR nesta sessão em 17/11/2026, com um ou no máximo dois commits. A entrega foi
organizada em um único commit. Merge, deploy e fechamento oficial da issue permanecem
fora desta etapa; publicação depende do fluxo autorizado correspondente.
O release deve coordenar API/migração e frontend: clientes antigos sem ciência recebem
422 apenas no cadastro; sessões/login não exigem reaceite. A migration deriva de
`20261115_02`; se a PR #280 entrar antes, conferir o grafo Alembic e conciliar as heads
antes da integração, sem alterar migration já aplicada.

Não houve mudança de provedor, custo, segredo, permissão, flag de produção, prazo de
retenção, regra de moderação ou decisão sobre avaliações na exclusão. #263/#265/#267
continuam responsáveis por seus insumos; limites conhecidos constam da Política e do
inventário, sem exigir fechamento integral dessas issues. Regiões/contratos, rotina
hospedada de descarte e cobertura/restauração de backups não foram auditados aqui.
Quando esses fatos mudarem ou #278 for entregue, atualizar a comunicação conforme
[RF26](../requisitos.md#rf26-transparencia-termos-e-ciencia-no-cadastro-269).
