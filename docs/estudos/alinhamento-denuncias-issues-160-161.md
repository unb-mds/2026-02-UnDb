# Contrato compartilhado e análise de origem — Issues #160/#161

**Estado:** contrato de implementação consolidado após autorização explícita do PO
para a entrega coordenada das #160/#161. A análise preparatória abaixo é histórica;
a seção final registra sua resolução e o contrato vigente desta implementação.
**Data da inspeção:** 01/11/2026.
**Resultado atual:** APIs RF21/RF22 implementadas conjuntamente; evidências abaixo.
As seções anteriores à resolução pelo PO descrevem a análise preparatória histórica.

## Fontes e evidências

- [Requisitos](../requisitos.md): RF20–RF22, AC21-01 a AC22-06 e R2-DEC-01 a
  R2-DEC-15. As regras de produto aprovadas permanecem a fonte de verdade.
- [Arquitetura](../arquitetura.md), [especificação](../../specs.md), `AGENTS.md`,
  `CLAUDE.md`, `CONTRIBUTING.md` e skills locais aplicáveis.
- Issues [#145](https://github.com/unb-mds/2026-02-UnDb/issues/145),
  [#154](https://github.com/unb-mds/2026-02-UnDb/issues/154),
  [#156](https://github.com/unb-mds/2026-02-UnDb/issues/156),
  [#160](https://github.com/unb-mds/2026-02-UnDb/issues/160),
  [#161](https://github.com/unb-mds/2026-02-UnDb/issues/161),
  [#162](https://github.com/unb-mds/2026-02-UnDb/issues/162) e
  [#163](https://github.com/unb-mds/2026-02-UnDb/issues/163), consultadas no GitHub.
- [PR #180](https://github.com/unb-mds/2026-02-UnDb/pull/180): integrada em
  `5360ff46bb390c7e0ff26f5849257cf77727d1a0`; detalha produto, sem aprovar schema.
- [PR #191](https://github.com/unb-mds/2026-02-UnDb/pull/191): integrada em
  `4126897e89e119696f3c137c2491771959f52bbd`, base `origin/develop` inspecionada.
  A revisão disponível registra aprovação humana. Resultados descritos na PR
  são evidência histórica, não testes reexecutados nesta análise.

O checkout inicial estava limpo em `feature/186-integracao-visual`, em `edd9188`,
sem a #156. `git fetch origin` confirmou a base integrada mais recente. A branch
`feature/160-denuncia-conteudo` foi criada a partir dela, preservando a branch
anterior. Não foi realizado merge, push, PR ou alteração de Issues.

A #161 estava aberta, com zero comentários. A busca por PRs de denúncia/moderação
não identificou implementação adicional; a busca por branch contendo `161` não
retornou resultados. Isso não comprova ausência de trabalho não publicado.
Na base integrada não foram encontrados modelos, routers ou serviços de denúncia
e moderação. A seção de contratos da #156 em `specs.md` declara explicitamente
que os contratos RF21/RF22 ainda não estão definidos.

## O que pode ser reutilizado

| Componente integrado | Uso na #160 e limite observado |
|---|---|
| `ComentarioVersao.id` | UUID identifica uma versão; não usar o ID da avaliação como alvo |
| `ComentarioVersao.avaliacao_id` e `substitui_id` | Associação à avaliação e à versão substituída |
| `EstadoComentario` | `PENDENTE`, `PUBLICADO`, `SUSPENSO`, `REMOVIDO`, `RETIRADO`, `SUBSTITUIDO`; não criar enum paralelo |
| `comentario_repository.listar_publicados` | Consulta pública filtra `PUBLICADO`; suspensão pode reutilizar esse filtro |
| `ComentarioPublicoResponse` | Retorna somente `id`, `texto`, `created_at`; preservar privacidade |
| `obter_sessao_opcional` | Sessão válida identifica conta sem exigir e-mail confirmado |
| `comentario_service.retirar` | Retirada já existe; precisa integrar encerramento na mesma transação |
| Migration `20261024_01` | Base de comentários, dependente de `20260921_01`; não editar migration aplicada |
| `tests/test_comentario.py` | `unittest`, HTTP ASGI e SQLite em memória; ampliar a estrutura existente |
| CI do backend | Testes determinísticos, migrações e consistência com PostgreSQL 16 |

Não existe papel de moderador no modelo `Usuario`. Não existem aprovação,
rejeição, manutenção, restauração e remoção humanas implementadas nessa base.
`texto` é obrigatório e tem tamanho mínimo no modelo/migration da #156: o descarte
aprovado exige alinhamento sobre sua representação física na #161.

## Regras compartilhadas já aprovadas

- Apenas versões textuais são denunciáveis; critérios estruturados não são alvos.
- Contas confirmadas ou não e visitantes podem registrar motivos da lista RF21.
- Uma denúncia aberta por conta/versão; visitantes podem repetir, sem deduplicação
  por navegador. A fila separa origens e contagens.
- Suspensão por 50 contas autenticadas distintas com denúncias abertas da mesma
  versão publicada. Visitantes e denúncias encerradas não contam.
- Suspensão oculta o texto público, conserva o texto para revisão e preserva notas.
- Denúncias e identidades são privadas; somente moderadores autorizados consultam
  registros internos, respeitando impedimento sobre comentário/denúncia próprios.
- Decisão humana encerra as denúncias relacionadas; retirada encerra como
  `conteúdo retirado`; substituição aprovada encerra como `versão substituída`.
- Denúncias encerradas são descartadas, sem arquivo permanente. Decisões duram
  sete dias; texto removido/retirado dura sete dias; substituído/rejeitado não é
  conservado. Estados do produto não impõem enums ou tabelas específicos.
- Suspensão pelo limiar e remoção humana de denunciado geram agradecimento às
  contas relacionadas com denúncia aberta; apagar após primeira exibição.
- Não há consulta pública de denúncias nem painel posterior do denunciante.

## Proposta técnica conjunta para revisão

Esta seção não é contrato aprovado e não autoriza implementação dependente.
Mantém FastAPI, SQLAlchemy síncrono, PostgreSQL, Alembic, Pydantic e as camadas
existentes. Não requer biblioteca, provedor ou serviço novo.

### Persistência e estados

1. Uma tabela `denuncias` com UUID próprio, FK obrigatória `comentario_versao_id`,
   FK opcional `denunciante_id` para `usuarios`, motivo fechado obrigatório e
   `created_at` com fuso. Conta nula representa visitante. Não coletar IP,
   fingerprint ou identidade adicional do visitante.
2. Cada linha representa uma denúncia **em aberto**. Encerramento remove a linha
   na transação da ação correspondente; não persistir linhas `ENCERRADA` nem
   snapshots de denúncias em auditoria. O registro aberto contém versão, ator
   quando existir, motivo, data e estado inicial implícito. A decisão tem seu
   registro separado e prazo próprio.
3. `UNIQUE(comentario_versao_id, denunciante_id)` impede repetição autenticada;
   valores nulos permitem repetições de visitantes no PostgreSQL. O índice atende
   à consulta por versão e à duplicidade; não criar outro índice equivalente.
   FKs não devem apagar registros silenciosamente como substituto do encerramento.
4. Reutilizar `EstadoComentario`; responsabilidade da #161 representar rejeição,
   descarte do texto e retenção sem contornar constraints da #156. Não incluir
   texto ou denúncias encerradas nos registros privados de decisão.
5. Agradecimentos persistidos por conta, versão e evento, sem identidade de autor
   ou outros denunciantes. A apresentação e confirmação de primeira exibição
   precisam de contrato próprio; nenhuma leitura pública pode consumir mensagens.

Os atributos propostos dependem da PK de sua própria entidade; identidade nominal
continua em `usuarios`, texto em `comentario_versoes`. Não duplicar nomes, e-mails,
texto ou contagens derivadas em `denuncias`. A contagem deve ser calculada sobre
registros abertos. O modelo físico, inclusive agradecimentos e decisões, precisa
de aceite conjunto antes da migration.

Alternativa considerada: armazenar denúncias abertas e encerradas com enum e índice
único parcial. Ela exigiria apagar as encerradas imediatamente para cumprir
R2-DEC-14; não fornece um arquivo permitido. Recomenda-se representar apenas as
abertas, reduzindo o risco de contagem ou retenção indevida. Isso é uma escolha
técnica proposta, não alteração do ciclo de vida aprovado.

### Concorrência e integração

- Repositório bloqueia a linha da versão para serializar registro, decisão,
  retirada e substituição; todas essas operações precisam seguir a mesma ordem.
- Na mesma transação: validar alvo e estado, identificar origem pela sessão,
  rejeitar duplicidade, inserir, contar `DISTINCT denunciante_id` não nulos e,
  quando aplicável, mudar `PUBLICADO` para `SUSPENSO` e criar agradecimentos.
- Encerramento é operação interna compartilhada com a #161 e a retirada da #156,
  sem `commit` próprio. Não criar endpoint público de encerramento/restauração.
- Codificações propostas de causa de encerramento: `MANTIDO`, `RESTAURADO`,
  `REMOVIDO`, `CONTEUDO_RETIRADO`, `VERSAO_SUBSTITUIDA`. Correspondem a ações,
  sem presumir que remoção declara toda denúncia procedente.
- Na #161, manter/restaurar/remover encerra as denúncias da versão analisada;
  aprovar substituto encerra as da anterior; rejeitar outro texto não as encerra.
- Aprovação inicial de comentários na #161 deve poder operar sem denúncias.
  A conclusão da #160 exige teste real dessas integrações, não apenas mocks.

### API candidata

| Operação proposta | Entrada / saída | Acesso |
|---|---|---|
| `POST /api/comentarios/{versao_id}/denuncias` | Somente `motivo`; `201` com mensagem de confirmação, sem protocolo ou identidade | Sessão opcional; não exigir e-mail confirmado |
| `GET /api/moderacao/comentarios/{versao_id}/denuncias` | Registros abertos separados por origem e contagens; identidades internas autenticadas | Moderador confirmado e autorizado, conforme dependência única da #161 |

Motivos candidatos como códigos técnicos: `OFENSA_PESSOAL`, `XINGAMENTO`,
`PALAVRAO`, `AMEACA`, `DISCRIMINACAO`, `EXPOSICAO_DADOS_PESSOAIS`, `SPAM`.
Não aceitar texto livre, `usuario_id`, origem, estado ou contagem enviados pelo cliente.
Erros propostos: `422` para motivo/schema inválido; `404` para alvo inexistente ou
indisponível; `409` para denúncia autenticada já aberta; `401`/`403` para consultas
internas sem autenticação/permissão. Esses códigos e payloads aguardam alinhamento.
Não adicionar consulta pública de denúncias ou exposição de contagens internas na
resposta pública de comentários.

## Decisões necessárias antes do código dependente

| ID | Pergunta / encaminhamento | Impacto |
|---|---|---|
| PD-160-01 | Existe contrato da #161 em trabalho não publicado? Se houver, fornecer referência. Caso contrário, aprovar ou corrigir a proposta conjunta acima, incluindo persistência, transações, encerramento, rotas e erros. | Evita modelos/enums/endpoints paralelos |
| PD-160-02 | Uma versão já `SUSPENSO` ainda aceita novas denúncias por UUID conhecido, ou registro só é permitido enquanto `PUBLICADO`? Pendentes nunca publicados não são expostos pela API pública. | Define elegibilidade sem escolher comportamento de produto por suposição |
| PD-160-03 | Qual entrega da #161 fornecerá papel/dependência de moderador, decisões, descarte e agradecimentos? Se ainda não existir, confirmar divisão de trabalho; incorporar suas ações à #160 exigiria ampliação explícita do escopo. | Consulta privada e integração não podem ser declaradas concluídas sem isso |

As regras de produto existentes não precisam ser reaprovadas. Não há bloqueio pela
lista de filtro nem pela ausência de IA. A limitação de identificar impedimento de
visitante permanece a aprovada; não acrescentar coleta de identidade.

## Verificação necessária após o alinhamento

- Ampliar testes existentes: alvo textual válido/inexistente/não elegível,
  visitante, conta não confirmada, duplicidade e vínculo exato da versão.
- Cobrir 49/50 contas, repetições, visitantes, versões distintas, encerramento e
  nova denúncia após decisão, sem contagem ou suspensão herdadas.
- Cobrir identidade privada, acesso autorizado/não autorizado, impedimentos,
  retirada/substituição, agradecimento após próximo acesso e consumo após exibição.
- Usar PostgreSQL para concorrência entre denúncia, suspensão, decisão e retirada,
  constraints, upgrade/downgrade/upgrade e `alembic check`.
- Executar suíte do backend, compilação e Docker Compose conforme CI; não afirmar
  validação de RF21/RF22 antes da implementação e integração.

Nesta análise foram inspecionados código, testes, migration e workflow existentes.
Os três links locais do documento foram verificados, assim como a marcação
`Proposed` e os três identificadores de pendências. `git diff --check` e
`git diff --cached --check` passaram; o diff documental foi revisado integralmente.
Nenhum teste funcional foi executado. O Docker não estava disponível: pipe
`docker_engine` ausente; a leitura
da configuração do Docker também foi negada pelo ambiente restrito. Python
disponível no PATH é 3.14; o launcher `py` não enumerou instalações. Esses fatos
não comprovam regressão do produto nem validam o fluxo solicitado.

Ao final daquela etapa, este documento era a única alteração preparatória. Ainda
não havia migration, endpoint ou funcionalidade adicionada; isso foi implementado
após a autorização coordenada descrita a seguir.

## Resolução pelo PO e contrato de implementação

Na continuação desta tarefa o PO confirmou: não existe contrato externo da #161;
as duas issues devem ser implementadas conjuntamente; somente `PUBLICADO` aceita
novas denúncias; autorização, decisões, descarte e agradecimentos integram a entrega.
Autorizou também commits locais, começando pelo documento preparatório exclusivo.
PD-160-01/02/03 estão resolvidas por essas instruções, sem reaprovar as regras RF20–22.

As escolhas de persistência e transação descritas acima são adotadas. Complementos:

- Permissão `Usuario.moderador`, inicialmente falsa, consultada no servidor a cada
  operação. Conta precisa estar autenticada e confirmada. Designação/revogação é
  comando operacional `python -m app.commands.moderador EMAIL conceder|revogar`,
  executado pelo operador por determinação do PO para membros da equipe. Nenhuma
  API de cadastro, sessão ou usuário comum permite conceder papel.
- A fila privada `GET /api/moderacao/comentarios` aceita filtro `estado` e inclui
  pendentes, publicados denunciados e suspensos. Vazia retorna `[]`. Detalhe em
  `GET /api/moderacao/comentarios/{id}`; registros de decisão em
  `GET /api/moderacao/comentarios/{id}/decisoes`. Identidade do autor e denúncias
  com nome/e-mail são exclusivamente internas. Impedimento proíbe decidir, sem
  restringir a consulta interna autorizada prevista em RF22.
- `POST /api/moderacao/comentarios/{id}/acoes` recebe `acao` e `motivo` não vazio.
  Ações: `APROVAR`, `REJEITAR`, `MANTER`, `RESTAURAR`, `REMOVER`. Retorna `200`
  com decisão, versão e estado. `APROVAR/REJEITAR` exigem `PENDENTE`;
  `MANTER` exige `PUBLICADO` com denúncia aberta; `RESTAURAR` exige `SUSPENSO`;
  `REMOVER` exige publicado denunciado ou suspenso. Estado incompatível retorna
  `409`; impedimento de autoria ou denúncia própria retorna `403`.
- Decisões contêm UUID, versão, moderador, data, ação, motivo e estados anterior/
  posterior, sem cópia do texto ou das denúncias descartadas. Após sete dias são
  apagadas. Não são produzidas decisões humanas fictícias para suspensão automática.
- Adicionar `REJEITADO` a `EstadoComentario`; texto passa a admitir `null` apenas
  em estados descartáveis. Rejeição e substituição apagam texto imediatamente;
  retirada/remoção conservam internamente até `descartar_em = evento + 7 dias`.
  Metadados mínimos da versão persistem para vínculos e estado do autor. A resposta
  do autor admite `texto: null`; a resposta pública continua exigindo texto.
- A aprovação usa a versão anterior vigente da avaliação, inclusive suspensa ou
  removida, sem restaurá-la. Envio de edição nunca torna anterior suspenso público.
  A aprovação substitui a anterior, encerra denúncias e descarta o texto anterior.
- Todas as escritas de versões da mesma avaliação adquirem primeiro lock da
  avaliação e depois da versão. Isso também serializa edições, retirada e aprovação;
  o lock inclui versões relacionadas antes de decidir e é mantido até o commit.
- Encerrar remove denúncias na mesma transação; a causa acompanha a operação
  interna. Retirada/substituição não produzem arquivo nem agradecimento. Manter/
  restaurar permite novas denúncias após o encerramento, sem contagem herdada.
- `GET /api/agradecimentos` exige conta autenticada (confirmada ou não), lista
  apenas `id` e mensagem, sem versão/autor/denunciantes. `POST /api/agradecimentos/
  {id}/exibido` apaga somente mensagem própria após a primeira exibição e retorna
  `204`; mensagem alheia/inexistente retorna `404`. GET não consome mensagens.
- Uma mensagem por conta e evento de suspensão/remoção, para todas as contas com
  denúncia aberta da versão na transação; visitantes não recebem mensagens.
- Descarte executável por `python -m app.commands.descartar_moderacao`, com modo
  `--continuo` para operação no Compose. Consultas internas e do autor também
  descartam dados vencidos antes de responder. O worker deve ser mantido ativo;
  não há alteração do prazo de sete dias por configuração.
- Registro de denúncia retorna `201` com confirmação; duplicidade autenticada
  `409`; alvo não publicado/inexistente `404`; motivo inválido `422`. A resposta
  não revela se o evento suspendeu o texto ou qual a contagem. Consultas privadas
  exigem moderador (`401/403`). Nenhum endpoint público consulta denúncias.

As migrations serão novas, posteriores a `20261024_01`; migrations aplicadas não
serão editadas. Downgrade não pode recriar texto descartado: se houver versões com
texto nulo, deve recusar a reversão para o schema antigo em vez de inventar texto.
O contrato é compartilhado pelas duas issues e referenciado em `specs.md`.

## API entregue para as interfaces #159/#162

Todas as rotas têm prefixo `/api`; schemas Pydantic filtram as respostas. Erros
seguem o padrão existente `{"detail": "mensagem"}`. Não há acesso a denúncias por
autor ou denunciante comum nem enum/modelo paralelo de versões.

| Método e rota | Entrada / saída | Permissão e erros |
|---|---|---|
| `POST /comentarios/{versao_id}/denuncias` | `DenunciaCreate {motivo}` → `201 ConfirmacaoDenuncia {mensagem}` | Visitante ou conta confirmada ou não; `404` alvo não publicado/inexistente, `409` duplicidade aberta, `422` motivo/schema inválido |
| `GET /moderacao/comentarios?estado=` | `list[ComentarioModeracaoResponse]`; `[]` se vazia | Moderador confirmado; `401/403`, `422` filtro inválido |
| `GET /moderacao/comentarios/{versao_id}` | `ComentarioModeracaoResponse` | Moderador confirmado; `401/403/404` |
| `GET /moderacao/comentarios/{versao_id}/denuncias` | `DenunciasDaVersao` | Moderador confirmado; `401/403/404` |
| `GET /moderacao/comentarios/{versao_id}/decisoes` | `list[DecisaoResponse]` ainda no prazo | Moderador confirmado; `401/403/404` |
| `POST /moderacao/comentarios/{versao_id}/acoes` | `AcaoModeracaoRequest {acao, motivo}` → `200 DecisaoResponse` | Moderador confirmado e sem impedimento; `401/403/404/409/422` |
| `GET /agradecimentos` | `list[AgradecimentoResponse {id, mensagem}]` | Conta autenticada, confirmada ou não; `401`; leitura não consome |
| `POST /agradecimentos/{id}/exibido` | Sem corpo → `204`, sem conteúdo | Conta destinatária; `401/404`; apagar após primeira exibição |

`ComentarioModeracaoResponse` contém `id`, `texto` opcional, `estado`, `autor`
(`id/nome/email` internos), `substitui_id` e `created_at`. `DenunciasDaVersao`
separa arrays `autenticadas`/`visitantes`, `contas_distintas` e `total_visitantes`.
Cada denúncia interna informa UUID, versão, motivo, `EM_ABERTO`, data e identidade
de conta quando existir. `DecisaoResponse` contém UUID, versão, moderador, ação,
motivo, estados anterior/posterior e data, sem cópia de texto ou de denúncias.

Na integração com a #156, `GET /comentarios/meu` admite texto nulo após descarte,
e `PATCH /comentarios/{id}/retirar` encerra denúncias e cancela substitutos na mesma
transação. A leitura pública de comentários continua expondo apenas `id`, `texto`,
`created_at`, sem estados, identidades, critérios individuais ou dados internos.
Nenhuma interface da #159/#162 foi implementada nesta entrega.

## Arquivos e migrations

| Camada | Arquivos criados ou alterados |
|---|---|
| Models | `denuncia.py` (`Denuncia`, `Agradecimento`), `decisao_moderacao.py`, `usuario.py` (papel), `comentario_versao.py` (descarte), `enums.py`, `__init__.py` |
| Schemas | `denuncia.py`, `moderacao.py`, `comentario.py` (texto descartado opcional) |
| Repositories | `denuncia_repository.py`, `moderacao_repository.py`, `comentario_repository.py` (locks e versões vigentes) |
| Services | `denuncia_service.py`, `moderacao_service.py`, `comentario_service.py`, `avaliacao_service.py` |
| HTTP/auth | `routers/denuncias.py`, `routers/moderacao.py`, `core/auth.py`, `main.py` |
| Operação | `commands/moderador.py`, `commands/descartar_moderacao.py`, `docker-compose.yml` |
| Testes | `test_denuncia.py`, `test_moderacao.py`, `integration_moderacao.py`, `migration_moderacao_check.py`, helper HTTP de `test_comentario.py` |
| Documentação | Este documento, `specs.md`, `README.md`, esclarecimento autorizado em `docs/requisitos.md` |

Migrations novas, sem alterar as da #156:

- `20261101_01_moderacao.py`: papel inicialmente falso; enum `REJEITADO`; texto
  descartável opcional com constraint de texto obrigatório em estados ativos;
  prazo de descarte e tabela de decisões privadas.
- `20261101_02_denuncias.py`: FKs para versão/conta, motivo fechado, unicidade
  conta/versão com visitantes repetíveis e agradecimentos persistentes até exibição.
- `20261101_03_retencao_legada.py`: aplica sete dias a retiradas/remoções legadas
  pela data do evento, descartando imediatamente textos cujo prazo já expirou.
  Foi criada após a primeira aplicação das anteriores, preservando suas versões.

O descarte mantém somente metadados mínimos de versão; denúncias encerradas e
decisões vencidas são apagadas. O processo contínuo verifica vencimentos a cada
60 segundos. Consultas internas e do autor executam a limpeza antes da resposta.
O operador deve manter `descarte-moderacao` ativo, inclusive quando não houver acessos.
Não há configuração que prolongue o prazo de sete dias.

## Evidências de validação da implementação

Ambiente principal de validação: imagem do backend `python:3.12-slim`, PostgreSQL
16 em container descartável, dependências existentes de `backend/requirements.txt`.
O host Windows possui Python 3.14.7, utilizado adicionalmente para as primeiras
verificações; não foi adotado como runtime do projeto. Nenhuma dependência nova.

| Verificação executada | Resultado |
|---|---|
| `python -m unittest discover -s tests -q`, Python 3.12 | **157 testes aprovados** |
| `python -m tests.integration_moderacao`, Python 3.12/PostgreSQL 16 | Aprovado: HTTP real, repetição concorrente, corrida da 50ª denúncia, 49/50 contas, 55 visitantes, versões distintas, suspensão, decisões concorrentes, impedimento, encerramento, retirada, agradecimentos e descarte |
| `python -m tests.integration_avaliacao --api-only`, Python 3.12/PostgreSQL 16 | Aprovado: regressão da #156, permissões, oito envios concorrentes com uma avaliação, substituição e comentário inválido independente dos critérios |
| `alembic upgrade head` em banco vazio | Aprovado |
| `alembic downgrade 20261024_01` e novo `upgrade head`, banco vazio | Aprovado |
| `alembic check`, inclusive em Python 3.12 | Sem diferenças entre models e banco |
| Dados legados: `tests.migration_legacy_check seed`, `tests.migration_moderacao_check seed/verify` entre revisões | Aprovado: critérios e texto pendente preservados, retirada antiga descartada, nenhum papel concedido automaticamente |
| Downgrade com texto já descartado | Recusado como esperado; transação preservou `20261101_03` e os dados |
| `python -m compileall -q app alembic` na imagem | Aprovado |
| `docker compose config --quiet` e inicialização de backend/db/descarte no projeto isolado | Aprovado; `/health` respondeu `{"status":"ok"}` e migration `20261101_03` aplicada |
| `docker compose up --build --wait`, composição completa isolada | Backend, banco, descarte e frontend iniciados; build Next.js/TypeScript aprovado e health checks passaram |
| Links locais e `git diff --check` | Verificados sem falhas |

O teste HTTP integrado usa sessões reais do servidor e PostgreSQL migrado; não
substitui dependências. Cada execução remove somente suas fixtures por UUID.
Para reproduzir, configure `DATABASE_URL` para banco descartável, aplique as
migrations e execute os módulos acima a partir de `backend/`. A regressão de
avaliações exige também `UNDB_INTEGRATION_TEST=1`. O teste de migration legado
começa em `20260911_01`, recebe dados institucionais, avança para `20261024_01`,
recebe comentários legados e depois avança para `head`.

Falhas de ambiente resolvidas: instalação inicial bloqueada pelo sandbox;
dependências existentes instaladas em venv temporário autorizado. Docker estava
parado e foi iniciado para as verificações. A primeira execução da suíte na imagem
não continha `pegar_id.py`, requerido pelos testes SIGAA existentes; ao disponibilizar
o helper do repositório, a suíte completa passou. Não foi feita correção do produto
para ocultar essa falha de montagem do ambiente.

Durante o build do frontend, `npm ci` informou 20 vulnerabilidades nas dependências
do lockfile existente (16 moderadas, três altas, uma crítica). Nenhuma dependência
ou lockfile do frontend foi alterado nesta entrega; a análise e correção desses
alertas permanecem fora do escopo das APIs. O build terminou com sucesso.

Não há lint, formatador ou verificação estática de tipos configurados para Python
no repositório; não se declara aprovação de ferramentas inexistentes. O lint do
workflow é do frontend. A integração de navegador das interfaces #159/#162 e a
homologação integral da #163 continuam fora deste escopo. O impedimento de denúncia
anônima mantém a limitação aprovada: não há identidade cadastrada para detectá-lo.
Não há decisão essencial de produto pendente nesta implementação; filtro e IA
continuam fora do fluxo humano entregue.

Commits locais da entrega até a validação funcional:

| Hash | Mensagem |
|---|---|
| `0d393f6` | `docs(moderation): definir contrato inicial de moderação` — exclusivamente o documento preparatório autorizado |
| `7df0e8e` | `docs(moderation): consolidar contratos de denúncias e moderação` |
| `842a635` | `feat(moderation): implementar autorização e revisão humana de comentários` |
| `7922204` | `feat(reports): adicionar persistência e validação de denúncias abertas` |
| `bc96ff1` | `feat(reports): expor API de denúncias e suspensão automática de versões` |
| `a4c0ad0` | `feat(moderation): integrar encerramento de denúncias e descarte de registros` |
| `20715f0` | `test(moderation): verificar fluxos integrados de denúncia e revisão` |
| `f08a749` | `fix(reports): preservar cookie de sessão ao confirmar exibição de mensagens` — mantém renovação de RF02 na resposta 204, verificada por HTTP real |

O commit final de documentação é posterior a esta tabela e pode ser consultado
no histórico. Até a conclusão da implementação, não havia push ou PR. A publicação
foi autorizada posteriormente pelo solicitante; merge e encerramento manual das
Issues continuam dependendo de autorização própria.

Na preparação da PR, o solicitante pediu mensagens de commit em português.
Os nove commits locais foram traduzidos antes do primeiro push, preservando
árvores de arquivos, autoria e datas. Os hashes acima refletem essa tradução.
A referência local `backup/160-161-mensagens-originais` preserva o histórico
anterior; nenhum código foi alterado nesse procedimento.
