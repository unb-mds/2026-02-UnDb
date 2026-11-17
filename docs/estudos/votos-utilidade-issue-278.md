# Votos de utilidade — #278

Fonte de produto: `docs/requisitos.md`, RF20 — Utilidade do comentário, autorização
na #278 (R2 de 16/11/2026) e pedido desta sessão. Base: `origin/develop` em `df854bf`.
Implementação para revisão humana; sem merge, deploy ou conclusão da issue.

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
| Frontend: `npm run test:browser` e `node tests/votos-comentario-browser.mjs` | Falharam na pré-condição: Edge/Chromium ausente em BROWSER_PATH; nenhum cenário visual/teclado foi executado |
| `git diff --check` | Passou |

Os testes backend cobrem autenticação, confirmação, autoria, corpo fechado, todas as
versões indisponíveis, idempotência, unicidade, resumo por sessão, logs/cache, ordem,
critérios/agregados/denúncias/publicação preservados, substituição manual/automática,
suspensão/restauração, limite do descarte e cascatas de conta/versão. PostgreSQL cobre
requisições de serviço simultâneas iguais/diferentes, retirada e disputa com indisponibilidade.
A primeira tentativa isolada herdou DEBUG=release do ambiente e falhou antes dos testes;
as execuções registradas usaram configuração sintética explícita (DEBUG=False).

## Acessibilidade e pendências

Usa tokens existentes e `.button`: alvo mínimo 44 px, foco compartilhado, botões nativos,
aria-pressed e texto de seleção/retirada. Revisão matemática dos tokens atuais:
foreground/panel 17,60:1; foreground/raised 16,27:1; muted/background 7,82:1;
danger/background 9,45:1; on-disabled/disabled-surface 7,45:1. Pares de texto atendem
4,5:1; foco/background 14,96:1. Isso é inspeção estática, sem comprovação visual.

**Pendente:** executar e inspecionar teclado/foco, carregamento/erro, contraste renderizado
com os controles e desktop/celular em 320, 390, 768 e 1440 px. Roteiro CDP está integrado
a `npm run test:browser`, mas não foi executado. Não há screenshots/evidências visuais.
Não foram executados Compose nem percursos E2E completos com navegador/backend real.
CI remoto e revisão humana devem ser acompanhados após push. Usar **Refs #278**.
