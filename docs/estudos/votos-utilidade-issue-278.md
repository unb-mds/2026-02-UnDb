# Votos de utilidade — #278

Fonte de produto: `docs/requisitos.md`, RF20 — Utilidade do comentário, autorização
na #278 (R2 de 16/11/2026) e pedido desta sessão. Base: `origin/develop` em `df854bf`.
Implementação com verificações da #278 nesta branch, para revisão humana. Sem merge
ou publicação em produção; a issue não foi fechada manualmente.

## Decisões e contratos

- Mantidas stack e camadas: SQLAlchemy síncrono, PostgreSQL, Alembic, FastAPI e Next.js.
  Sem dependências novas. `feature/278-comentario-util` é aceita pelo CONTRIBUTING.
- `votos_comentario`: chave composta versão/conta não nula, CHECK UTIL/NAO_UTIL e FKs
  com exclusão em cascata. Relação N:N normalizada: o valor depende da chave inteira;
  sem timestamps/histórico ou contadores redundantes. Índice da PK atende consulta
  por versão; índice de conta atende exclusão dos seus votos.
- `GET /api/comentarios/{id}/utilidade`, sessão opcional, retorna somente `uteis`,
  `nao_uteis`, `meu_voto`. Visitante recebe null no estado próprio. Nenhuma lista de
  votantes, identidade, nota individual ou poder novo de moderação.
- `POST /api/comentarios/{id}/voto`, conta confirmada, corpo fechado `{voto}`:
  UTIL/NAO_UTIL/null. Null retira; repetir/trocar/retirar é idempotente. Identidade
  exclusivamente da sessão. 401 sem sessão; 403 não confirmado/próprio autor;
  404 id inexistente ou versão indisponível com mesma mensagem; 422 UUID/corpo inválido.
  Respostas no-store/no-referrer, usando middleware existente de origem/CSRF e logs seguros.
- Lock segue avaliação → versão, como retirada/moderação; upsert e PK garantem
  unicidade. Resumo na transação usa agregação SQL, sem atualizar comentário ou avaliação.
  Mantidas ordenação, notas/agregados, denúncias, publicação e moderação.
- UI isolada em `utilidade-comentario.tsx`, com apenas uma inclusão no item comum.
  Serviço valida resposta e minimiza campos. Troca de sessão cancela consulta/escrita
  anterior e limpa estado próprio. Erros não mostram detalhes internos; há retry de
  leitura, bloqueio durante envio, botões nativos/aria-pressed, status e alerta.
- Resumos são consultados no cliente por versão, sem personalizar a lista pública.
  Trade-off: uma consulta adicional por comentário, sem cache compartilhado de sessão.

## Ciclo de dados e integração

Aplicação do ciclo vigente de RF20/R2-DEC-14 à versão: votos de versão suspensa
permanecem indisponíveis junto com o texto; restauração da mesma versão os preserva.
Substituto começa em zero. Aprovação manual/automática de substituto e rejeição apagam
votos com o texto. Retirada/remoção bloqueia acesso imediatamente e descarta votos
no prazo existente de sete dias. Exclusão física de versão/conta usa cascata no banco.
Sem retenção adicional, cópias ou auditoria nova.

**Ponto a confirmar na #263:** não foi encontrada regra anterior específica para votos;
foi seguido o ciclo da versão conforme autorização expressa do pedido. Não se decidiu
exclusão/desvinculação de notas ao excluir conta nem se criou essa operação.

#206 está fechada e integrada pela #219. Na consulta de PRs abertos havia #280,
com mudanças ainda em revisão no ciclo de exclusão/purga e limitador de abuso.
Esta entrega parte de develop e não antecipa a retenção proposta nessa PR. Coordenar
na integração: revisão Alembic 20261117_03 depende da 20261117_02 de develop (ciência
nos Termos); #280 tem outra linha de revisões. Rebase/merge de migrations deve preservar
histórico aplicado e compatibilizar descarte. Não se importou novo limitador de PR aberta.
#263/#265 seguem abertas; #251 adia busca. Fechamento dessas issues não é pré-condição.

## Verificações observadas

Ambiente local: Python 3.12.16 em venv existente, Node 24.14.1, npm e PostgreSQL local
com cliente 14.24. CI usa Node 22/PostgreSQL 16; isso limita equivalência de ambiente.
Dados exclusivamente sintéticos; banco local exclusivo `undb278_test`. Nenhuma operação
em produção, e-mail real, dependência nova ou alteração de arquivo .env.

| Comando (na pasta correspondente) | Resultado |
|---|---|
| Backend: `python -m ruff check .` | Passou |
| Backend: `python -m ruff format --check .` | Passou, 170 arquivos; primeira execução pediu formatação em dois arquivos, corrigida |
| Backend: `python -m compileall -q app alembic` | Passou |
| Backend: `python -c 'from app.main import app; assert app is not None'` | Passou |
| Backend: `python -m coverage run --branch --source=app -m unittest discover -s tests -v` | 356 testes: sem falhas, dois skips opcionais preexistentes de identidades/reconciliação; 11 testes novos executados, incluindo os três PostgreSQL |
| Backend: `python -m coverage report` | Passou, 87% global; não é critério novo de cobertura |
| `alembic upgrade head; alembic check; alembic downgrade 20261117_02; alembic upgrade head; alembic check` | Passou em PostgreSQL exclusivo; sem divergência modelo/schema |
| `alembic downgrade base; alembic upgrade head; alembic check` | Passou |
| Ciclo legado do CI: downgrade base, upgrade 20260911_01, `python -m tests.migration_legacy_check seed`, upgrade head, verify-upgrade, check, downgrade 20260911_01, verify-downgrade, upgrade head | Passou |
| `docker build -t issue278-backend-ci .` e imagem executando `alembic heads` | Passaram; imagem contém `20261117_03 (head)` |
| Frontend: `npm run lint` | Passou após correção final de tokens |
| Frontend: `npm run typecheck` | Passou |
| Frontend: `npm run test:coverage` | 85 testes passaram, zero falhas |
| Frontend: `npm run build` | Passou, inclusive após correção final dos tokens |
| `node --check frontend/tests/votos-comentario-browser.mjs` | Sintaxe passou; não prova comportamento |
| Frontend: `node tests/votos-comentario-browser.mjs` com BROWSER_PATH/PREVIEW_DIR | Passou na execução final: 320/390/768/1440 px, Tab/Enter/Space, foco preservado, contraste renderizado, erros/carregamento/retry e troca de sessão |
| Frontend: `npm run test:browser` local com Chromium temporário | Parou no teste anterior `avaliacao-browser.mjs`: timeout de formulário direto. Esse percurso passou no CI/Edge; não foi declarado sucesso local da suíte completa |
| `git diff --check` | Passou |

Os testes backend cobrem autenticação, confirmação, autoria, corpo fechado, todas as
versões indisponíveis, idempotência, unicidade, resumo por sessão, logs/cache, ordem,
critérios/agregados/denúncias/publicação preservados, substituição manual/automática,
suspensão/restauração, limite do descarte e cascatas de conta/versão. PostgreSQL cobre
requisições de serviço simultâneas iguais/diferentes, retirada e disputa com indisponibilidade.
A primeira tentativa isolada herdou DEBUG=release do ambiente e falhou antes dos testes;
as execuções registradas usaram configuração sintética explícita (DEBUG=False).

## Conclusão das verificações de acessibilidade

A indisponibilidade inicial de navegador foi superada usando um executável oficial
**Chrome for Testing Headless Shell 157.0.8103.78**, temporário em `/tmp`. Não foram
instalados pacotes ou adicionadas dependências ao projeto. O roteiro continua usando
Node/CDP existente e aceita Edge/Chromium em BROWSER_PATH.

A primeira execução real identificou dois problemas: Enter no roteiro CDP estava sem
seu caractere nativo de ativação; e `disabled` no produto removia o foco durante o envio.
O roteiro agora envia Enter completo, além de Tab e Space. O produto usa `aria-disabled`
com a trava síncrona de envio já existente: mantém foco, informa indisponibilidade e
bloqueia tentativas duplicadas, inclusive de teclado. O teste comprova que o foco
continua no botão após a resposta e que o próximo Tab alcança a opção seguinte.

O prazo de inicialização do helper CDP passou a ser opcional, mantendo o padrão de
25 s das demais suítes. Este roteiro usa 60 s para acomodar inicialização/hidratação
no ambiente local; nenhuma asserção funcional foi removida e nenhum SLA foi criado.
A fixture CORS acompanha a API real; os recursos auxiliares são sintéticos.

Verificação em **320, 390, 768 e 1440 px**: sem rolagem horizontal, controles dentro
do viewport e alvos de pelo menos 44 × 44 px; rótulo do grupo, seleção via aria-pressed,
foco visível de 2 px, Tab/Enter/Space para votar/trocar/retirar. Capturas inspecionadas:

| Largura | Evidência de seleção e foco |
|---|---|
| 320 px | [Celular 320](evidencias/issue-278/votos-320-selecionado-foco.png) |
| 390 px | [Celular 390](evidencias/issue-278/votos-390-selecionado-foco.png) |
| 768 px | [768](evidencias/issue-278/votos-768-selecionado-foco.png) |
| 1440 px | [Desktop 1440](evidencias/issue-278/votos-1440-selecionado-foco.png) |

Também foram verificados [carregamento](evidencias/issue-278/votos-carregando-401.png),
[erro](evidencias/issue-278/votos-erro-403.png) e
[falha de leitura com retry](evidencias/issue-278/votos-falha-leitura.png).
Respostas 401/403/404/503 mostram alerta, preservam contagens e não apresentam sucesso
fictício ou detalhes internos. Um segundo clique durante envio não gera outra escrita.
Falha de leitura não inventa contagens. Troca de sessão limpa estado próprio e cancela
requisição anterior; resposta atrasada não restaura o voto da sessão antiga.

Contraste calculado **no navegador a partir das cores renderizadas**, incluindo estados
normal, carregando e erro: todos os pares de texto medidos atendem 4,5:1. Métricas,
viewports e resultados em [resultados.json](evidencias/issue-278/resultados.json);
[hashes das evidências](evidencias/issue-278/sha256.json). A inspeção das capturas
confirmou rótulos legíveis, quebra de texto e foco visível nos controles.

Reprodução, em `frontend/`, com um executável Edge/Chromium disponível:

```sh
BROWSER_PATH=/caminho/do/navegador PREVIEW_DIR=/tmp/votos-278 node tests/votos-comentario-browser.mjs
```

Após a correção: `npm run lint`, `npm run typecheck`, `npm run test:coverage` (85 testes)
e `npm run build` passaram. A tentativa local da suíte completa parou no teste anterior
de formulário, antes dos votos; não se alterou esse fluxo nem se declarou sucesso local.
No [CI anterior](https://github.com/unb-mds/2026-02-UnDb/actions/runs/44013643740), backend,
Gitflow, Compose e E2E de avaliação/moderação passaram; o frontend falhou especificamente
no Enter incompleto do roteiro antigo, agora corrigido e exercitado localmente.
A execução do CI da revisão final deve ser consultada no PR #283.

## Limites remanescentes

Não houve teste com participantes, operação em produção nem novo serviço. As evidências
visuais usam HTTP sintético; testes HTTP/backend e PostgreSQL validam os contratos e
persistência reais separadamente. O CI já executou E2E de avaliação/moderação e Compose;
não se afirma que esses percursos foram executados localmente nesta continuação.
O ponto documental de aplicação do ciclo da versão aos votos segue registrado na #263,
conforme autorização expressa; não bloqueia esta implementação nem amplia retenção.
A compatibilização com a PR #280 permanece assunto de integração, sem antecipar mudanças
em revisão. Após aprovação humana, o PR pode encerrar a #278 via `Closes #278`; não há
merge ou fechamento manual autorizado nesta sessão.
