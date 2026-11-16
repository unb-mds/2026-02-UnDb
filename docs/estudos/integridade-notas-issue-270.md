# Integridade das notas — portão de aprovação da #270

Estado: entrega documental parcial; novos comportamentos permanecem **decisão pendente**.
Origem: [#270 — LEGAL-05](https://github.com/unb-mds/2026-02-UnDb/issues/270),
no [épico #272](https://github.com/unb-mds/2026-02-UnDb/issues/272).
Consulta em 15/11/2026 (America/Sao_Paulo). Não houve acesso a produção, dados privados
ou credenciais. Esta análise não comprova fraude nem validação jurídica.

## 1. Critérios e autorização

A tabela foi preparada antes de qualquer implementação funcional. `IMPLEMENTÁVEL`
autoriza somente o trecho sustentado; `SOMENTE DOCUMENTAÇÃO/PROPOSTA` não autoriza
comportamento; `BLOQUEADO` identifica implementação que exige insumo ausente.
A fonte de requisitos continua sendo [docs/requisitos.md](../requisitos.md).

| Critério da #270 | Classificação | Evidência e limite | Pergunta objetiva ao PO / condição de retomada |
|---|---|---|---|
| 1. Documentar controles e limites | IMPLEMENTÁVEL, somente documentação | RF01–RF03/RF14 e seção 11; #50 integrada pelas PRs #122/#126; código conferido na seção 3 | Nenhuma nova regra necessária; preservar upsert e vínculo professor–disciplina |
| 2. Propor declaração e implementar conforme aprovação | SOMENTE DOCUMENTAÇÃO/PROPOSTA | A issue autoriza propor; não foi localizada aprovação de apresentação/registro de declaração em requisitos na base consultada | Aprova o texto proposto na seção 4? Quando apresentar e o que registrar, inclusive em substituições e contribuições anteriores? |
| 3. Sinais, dados mínimos, limiares e responsável | SOMENTE DOCUMENTAÇÃO/PROPOSTA | #261 e #264 abertas; definição operacional coletiva de dados em #260 não aprova sinais nem responsáveis pela revisão numérica | Quais dados/fontes estritamente necessários, critérios e responsável serão aprovados, após avaliação de privacidade? |
| 4. Contestação numérica e revisão fundamentada | BLOQUEADO | #263 aberta, PR #275 integrada em d99916e; RF25 permite receber e encaminhar, sem alterar notas; #264 aberta e sem regra de revisão numérica aprovada | Qual regra de revisão numérica complementará o contrato da #263, com manutenção da avaliação e comunicação segura? Reutilizar RF25; aprovar regras específicas antes de implementar |
| 5. Invalidação/reversão e registro restrito | BLOQUEADO | RF20–RF22 preservam notas nas ações textuais; #261/#262/#264 abertas; retenção numérica não aprovada | Quem pode invalidar/restaurar, com quais fundamentos, impedimentos, acesso, evento inicial e prazo de descarte? |
| 6. Recálculo de indicadores, contagens e destaques | BLOQUEADO | RF08/RF09/RF15, RNF02 e fórmulas vigentes autorizam agregação atual; não autorizam excluir/incluir avaliações por revisão | Qual política de elegibilidade resultará da decisão de invalidação/restauração? Preservar fórmulas e mínimo de três |
| 7. Cenários sintéticos, falsos positivos e contestação | SOMENTE DOCUMENTAÇÃO/PROPOSTA | Há regressões vigentes; oráculos de fraude e invalidação ainda dependem dos critérios 3–6 | Aprovar casos e resultados esperados antes de automatizar novos cenários; plano na seção 5 |
| 8. Eventual prova por matrícula | IMPLEMENTÁVEL, somente registrar exclusão do escopo | RF01/RF14, seção 11 e #41 encerrada como não planejada; instrução expressa da #270 | Qualquer estudo futuro exige análise jurídica/técnica própria e fonte autorizada; nenhum acesso nesta entrega |

Nenhum novo comportamento funcional passa pelo portão nesta base. Não foram alterados
requisitos aprovados, derivados, API, interface, schema, migrations, retenção ou dependências.
A issue permanece parcialmente atendida e não deve ser fechada por esta entrega documental.

## 2. Base e dependências conferidas

Working tree inicialmente limpo. Branch `feature/270-reduzir-manipulacao-notas`, prefixo
aceito por `CONTRIBUTING.md`, criada de `origin/develop@0717614820cb14e31bc928ec0d5ce739d028cf98`.
O endereço antigo do remoto (`unb-mds/G7-2026-2`) e o endereço atual da issue retornaram
o mesmo SHA de develop; não foi necessário alterar o remoto.

Na conferência final, develop avançou novamente para `d99916e93186864c2769ae95ea577bba477b4e17`
com o merge da #275. RF25 foi conferido como aprovado para recebimento/encaminhamento,
sem alterar notas e sem autorizar ativação antes de retenção/configuração. O levantamento
e os testes abaixo permanecem referidos à base inicial `0717614`; não representam
reteste do código recém-integrado da #263.

Develop avançou desde a auditoria `7b0bd73`: integrou #259 (detecção textual da #252)
e #274 (continuidade da #260). Main continua em `a3afa44`. Essas entregas não aprovam
regras de integridade numérica. A governança vigente atribui decisões sobre dados à equipe
em conjunto; papéis de recebimento não equivalem a autorização para invalidar notas
([continuidade operacional, seção 2](../continuidade-operacional.md)).

Estados consultados no GitHub (descrição/estado, sem código de dependências):

| Issue | Estado real observado | Integração / insumo relevante |
|---|---|---|
| [#50](https://github.com/unb-mds/2026-02-UnDb/issues/50) | Fechada, concluída | PRs [#122](https://github.com/unb-mds/2026-02-UnDb/pull/122) e [#126](https://github.com/unb-mds/2026-02-UnDb/pull/126) confirmadas como merged em develop; unicidade/substituição, sem refazer |
| [#41](https://github.com/unb-mds/2026-02-UnDb/issues/41) | Fechada, não planejada | Matrícula/histórico individual indisponível na fonte pública; verificação não implementada |
| [#160](https://github.com/unb-mds/2026-02-UnDb/issues/160) e [#161](https://github.com/unb-mds/2026-02-UnDb/issues/161) | Fechadas, concluídas | PR [#192](https://github.com/unb-mds/2026-02-UnDb/pull/192) confirmada merged em develop; denúncias/moderação de texto, critérios estruturados preservados |
| [#261](https://github.com/unb-mds/2026-02-UnDb/issues/261) | Aberta | Inventário, minimização, bases e fornecedores; insumo de integridade ainda não integrado |
| [#262](https://github.com/unb-mds/2026-02-UnDb/issues/262) | Aberta | Retenção/exclusão e efeito sobre avaliações/agregados ainda pendentes |
| [#263](https://github.com/unb-mds/2026-02-UnDb/issues/263) | Aberta; PR integrada na conferência final | PR [#275](https://github.com/unb-mds/2026-02-UnDb/pull/275) fechada, `merged=true`, em d99916e; RF25 aprovado em requisitos. Recebimento ainda condicionado a retenção/configuração/homologação; não criar paralelo |
| [#264](https://github.com/unb-mds/2026-02-UnDb/issues/264) | Aberta | Governança, revisão e comunicação fundamentada propostas; regras numéricas não integradas |
| [#268](https://github.com/unb-mds/2026-02-UnDb/issues/268) | Aberta | Política precisa descrever apenas tratamentos reais e aprovados |
| [#269](https://github.com/unb-mds/2026-02-UnDb/issues/269) | Aberta | Termos/ciência não substituem declaração específica ou prova de experiência |
| [#271](https://github.com/unb-mds/2026-02-UnDb/issues/271) | Aberta | Metodologia deve distinguir conta institucional, experiência e limites amostrais |
| [#272](https://github.com/unb-mds/2026-02-UnDb/issues/272) | Aberta | Registro e fluxo de retomada lidos; nenhum comentário retornado na consulta |

A busca de PRs relacionadas localizou #275 para o canal e #274 para continuidade;
não localizou entrega de regras numéricas das demais dependências. Issue aberta não é
bloqueio genérico: os bloqueios acima indicam precisamente o insumo ausente.

## 3. Controles atuais e limites

- [Modelo](https://github.com/unb-mds/2026-02-UnDb/blob/0717614820cb14e31bc928ec0d5ce739d028cf98/backend/app/models/avaliacao.py): unicidade de
  `(usuario_id, professor_id, disciplina_id)` e vínculo interno de autoria; não há
  garantia de anonimato absoluto nem comprovação de experiência.
- [Repository](https://github.com/unb-mds/2026-02-UnDb/blob/0717614820cb14e31bc928ec0d5ce739d028cf98/backend/app/repositories/avaliacao_repository.py),
  `salvar_ou_substituir`: `ON CONFLICT DO UPDATE` na chave composta, substituindo
  critérios e `updated_at`, preservando ID e criação. A constraint arbitra concorrência;
  contas diferentes continuam podendo avaliar o mesmo par. Não é detecção de coordenação.
- [Service](https://github.com/unb-mds/2026-02-UnDb/blob/0717614820cb14e31bc928ec0d5ce739d028cf98/backend/app/services/avaliacao_service.py), `registrar_avaliacao`:
  valida existência e vínculo professor–disciplina, resolve identidade docente e persiste
  transacionalmente. O vínculo é de oferta institucional, **não matrícula do aluno**.
  Autenticação e confirmação do e-mail são exigências vigentes de RF01/RF02/RF14;
  nenhuma delas prova que o estudante cursou aquela disciplina.
- `consultar_agregado` lê as avaliações do par e conta os registros na consulta.
  Abaixo de três retorna quantidade, `dados_suficientes=False` e nenhum critério.
  Não há filtro de invalidação numérica no modelo/repository consultados.
- [Domínio de agregação](https://github.com/unb-mds/2026-02-UnDb/blob/0717614820cb14e31bc928ec0d5ce739d028cf98/backend/app/domain/avaliacoes.py): média de didática
  com uma casa; moda de dificuldade (empate para maior dificuldade); maioria para
  chamada e disponibilidade, com empate conflitante; qualidade por moda somente com
  maioria que disponibiliza material (empate para melhor qualidade); recomendação
  percentual inteiro. Arredondamento half-up. Não há nota geral composta.
- Comparação ordena suficientes primeiro, recomendação decrescente, quantidade
  decrescente e nome. [Destaques por volume](https://github.com/unb-mds/2026-02-UnDb/blob/0717614820cb14e31bc928ec0d5ce739d028cf98/backend/app/repositories/disciplina_repository.py),
  `listar_mais_avaliadas`, contam avaliações por disciplina e ordenam quantidade,
  nome e ID, com limite padrão seis. Esse destaque não mede qualidade e não aplica
  o mínimo de três do indicador professor–disciplina.
- RF20–RF22 autorizam ação sobre **texto** sem remover os cinco critérios nem mudar
  contagens/agregação. Não usar denúncia textual como invalidação numérica. Retenção
  vigente: decisão e texto retirado/removido por sete dias a partir do respectivo
  evento; denúncia encerrada não é conservada. Isso não autoriza criar histórico
  numérico nem estender retenção para viabilizar recurso.

Limitações: unicidade por conta não impede múltiplas contas coordenadas; amostra pequena,
subjetividade e opiniões semelhantes não demonstram fraude. Uma nota muito negativa,
isoladamente, não prova fraude. Não foi medida incidência de abuso, qualidade de detector
ou taxa de falsos positivos nesta análise estática.

## 4. Propostas para decisão humana

**Declaração — decisão pendente:** texto candidato para discussão:
“Declaro que esta avaliação reflete minha experiência acadêmica real com este professor
nesta disciplina.” A redação não foi aprovada nem colocada na interface. O PO deve decidir
apresentação, obrigatoriedade, registro mínimo, tratamento de substituições e avaliações
anteriores. Ciência dos Termos é assunto distinto; não inventar declaração retroativa.
Não exigir histórico, credencial ou dado privado do SIGAA.

**Análise proporcional — decisão pendente:** #261 deve fornecer avaliação de necessidade,
fontes, acesso e privacidade; #264, responsável elegível e procedimento humano. Cabe ao
PO e à equipe aprovar dados, critérios e limiares com revisão jurídica pertinente.
Não foram escolhidos sinais, identificadores novos ou valores. Definições sensíveis
futuras precisam de acesso restrito, sem heurísticas de evasão nesta documentação.

**Contestação/revisão — decisão pendente:** reutilizar RF25 da #263 integrado em d99916e,
sem novo contrato paralelo. RF25 permite pedido de revisão por complemento e resposta
restrita ao solicitante; não autoriza alterar notas. #264 e o PO precisam aprovar
fundamento, impedimentos, encaminhamento,
comunicação segura e possibilidade de manter a avaliação. Discordância, denúncia e
suspeita não devem ser documentadas como confirmação automática de fraude.

**Invalidação/reversão — decisão pendente:** aprovar autoridade, evidência mínima,
justificativa, reversibilidade, acesso restrito e ciclo de descarte antes de alterar dados.
#261/#262 devem delimitar retenção por categoria/evento; não extrapolar os sete dias de
moderação textual para uma nova categoria nem ampliar o prazo vigente. A política de
inclusão nos agregados/contagens/destaques precisa de decisão expressa. A validação
jurídica permanece humana e não realizada nesta entrega.

## 5. Plano sintético de verificação futura

Plano proposto, **não testes implementados/executados de novas regras**. Homologar
oráculos com o PO e revisão humana; usar contas, professores e disciplinas inteiramente
sintéticos em ambiente descartável. Nunca criar avaliações fictícias de docentes reais
em produção. Não publicar identidade de autores, chaves de acesso ou registros privados
em testes, logs, API pública ou exemplos.

| Cenário | Verificação após aprovação / referência vigente |
|---|---|
| Inserção, reenvio e concorrência | Reutilizar `tests.test_avaliacao` e `tests.integration_avaliacao` da #50; não duplicar implementação; teste concorrente real exige PostgreSQL descartável |
| Suspeita sem fraude / controles negativos | Revisão pode manter contribuição legítima; nota negativa isolada, opiniões parecidas e discordância não constituem oráculo de fraude; medir falsos positivos em casos homologados |
| Fraude justificada | Evidência sintética homologada; decisão humana motivada conforme política aprovada, sem regra automática inventada |
| Invalidação/restauração 3→2→3 | Após decisão autorizada: em 3, critérios disponíveis; em 2, quantidade e insuficiência sem valores; ao restaurar 3, fórmulas originais e contagem consistentes; repetir deve respeitar contrato aprovado |
| Destaques e comparação | Conferir contagens por disciplina, ordenação/empates e remoção de destaque quando aplicável à política futura; mínimo de três permanece por par, sem impor esse mínimo ao destaque por volume |
| Texto versus critérios | Retirada/remoção de comentário preserva notas e agregados conforme RF20–RF22; invalidação numérica exige percurso próprio aprovado |
| Privacidade e revisão | Acesso indevido negado, resposta segura e possibilidade de manutenção/reversão; retenção conforme decisão, sem reproduzir conteúdo privado em evidências públicas |

Não existem resultados de detecção, falsos positivos ou recálculo por invalidação a
reportar. Casos propostos não comprovam precisão em produção nem eficácia antifraude.

## 6. Retomada e registros publicados

Pendências recebidas: regras numéricas de #261/#262/#264 e integração de #263
(esta última resolvida na conferência final de merge, sem homologar ativação).
Na consulta inicial, o épico não retornou comentários; os exemplos de execução fora de ordem são exemplos,
sem evidência de pendência concreta resolvida pela #270. A PR #275 foi conferida inicialmente
como aberta e, na conferência final, como integrada em d99916e. Foram lidos somente os
novos requisitos RF25 e documentos de contrato/continuidade, sem código da dependência.
O canal não altera notas; as pendências de revisão numérica continuam. Nenhuma pendência
de política numérica ou jurídica foi declarada resolvida. Foi entregue o diagnóstico
rastreável que pode alimentar inventário, canal, política, Termos e metodologia.

Na revisão de 16/11/2026 (America/Sao_Paulo), o solicitante autorizou explicitamente
publicar os registros antes preparados como rascunhos. Foram reconferidos os comentários
do épico e das dependências. O [registro da #263](https://github.com/unb-mds/2026-02-UnDb/issues/272#issuecomment-6905832664)
já documentava PEND-263-RET/INV/ESC/OPS/ABUSO; os encaminhamentos da #270 abaixo
complementam esse registro, sem declarar suas pendências resolvidas.

**Registro da #270 no épico:** [pendências e condições de retomada](https://github.com/unb-mds/2026-02-UnDb/issues/272#issuecomment-6915576664).
Os checklists foram publicados nos destinos e seus conteúdos conferidos após a criação:

| ID | Insumo / condição de retomada | Checklist no destino | Estado |
|---|---|---|---|
| PEND-270-INV | Conferir categorias e necessidade dos dados de integridade antes de propor sinais; fornecer decisão de privacidade à #270 e revisar este diagnóstico | [#261](https://github.com/unb-mds/2026-02-UnDb/issues/261#issuecomment-6915584669) | Aguardando decisão/insumo |
| PEND-270-RET | Aprovar retenção/eventos/descarte e efeitos sobre avaliações; reconciliar futura invalidação/reversão, sem ampliar retenção vigente | [#262](https://github.com/unb-mds/2026-02-UnDb/issues/262#issuecomment-6915586369) | Aguardando decisão/insumo |
| PEND-270-CANAL | Com RF25 integrado pela #275, após homologação/ativação, conferir categorias, encaminhamento de notas e comunicação segura; não criar contrato paralelo | [#263](https://github.com/unb-mds/2026-02-UnDb/issues/263#issuecomment-6915587665) | Contrato integrado; operação pendente |
| PEND-270-REV | Fornecer regras, responsável elegível, impedimentos e revisão motivada, inclusive manutenção de avaliação legítima; retomar testes e comunicação da #270 | [#264](https://github.com/unb-mds/2026-02-UnDb/issues/264#issuecomment-6915588958) | Aguardando decisão/insumo |

Cada issue fornecedora deve conferir esta entrega ao produzir o insumo e reconciliar
documentação, código e testes da #270 no escopo aprovado, registrando evidências na
origem, no destino e no épico. PO valida destino/responsáveis e decisões; publicação
não cria designação pessoal ou jurídica nem aprova novas regras numéricas.

**Impacto sobre as demais entregas:** #268 não deve anunciar coleta/invalidação futura;
#269 não deve apresentar declaração ou sanção como existente; #271 pode consumir os
limites de conta institucional, amostra e destaque por volume aqui conferidos. Todas
seguem abertas na consulta. Não há ajuste em entrega incompatível identificado nesta
base; quando produzirem texto/funcionalidade, conferir contra este registro e contra
requisitos aprovados. Esses encaminhamentos não são critérios funcionais atendidos.

Pendências resolvidas: levantamento/classificação documental e confirmação da integração
do contrato RF25 pela #263; esta entrega apenas reconhece esse insumo, não o reimplementa.
Remanescentes: decisões de produto/dados/retenção, validação jurídica, homologação/ativação do
canal e implementação/testes dos comportamentos aprovados posteriormente. Na entrega
original não houve edição externa; os registros acima foram publicados durante a revisão
autorizada. Nenhuma pendência funcional foi resolvida apenas por esses encaminhamentos.

## 7. Verificações da entrega original

Ambiente local: Python 3.12.16 no `backend/.venv`; Node 24.14.1 (CI usa Node 22).
Ferramentas Ruff, coverage e MkDocs instaladas das listas já versionadas usando `uv pip`,
pois o venv não tinha pip. Nenhuma dependência do projeto foi adicionada ou alterada.
Comandos backend abaixo usam esse Python (`.venv/bin/python`).

| Comando / diretório | Resultado observado |
|---|---|
| `python -m ruff check .` / backend | Aprovado |
| `python -m ruff format --check .` / backend | Aprovado; 148 arquivos |
| `python -m compileall -q app alembic` / backend | Aprovado |
| `DEBUG=False SECRET_KEY=issue270-synthetic-only DATABASE_URL=sqlite:// python -m coverage run --branch --source=app -m unittest discover -s tests -v` / backend | 310 testes; 308 aprovados e dois pulados por exigirem PostgreSQL descartável |
| `python -m coverage report` / backend | Aprovado; total 86%, sem impor meta nova |
| `docker build -t issue270-backend-ci .` / backend | Aprovado; imagem local construída |
| `npm run lint` / frontend | Aprovado |
| `npm run typecheck` / frontend | Aprovado |
| `npm run test:coverage` / frontend | 83 testes aprovados, sem falhas ou pulados |
| `npm run build` / frontend | Aprovado (Next.js) |
| `backend/.venv/bin/python -m mkdocs build --strict --site-dir /tmp/issue270-site` / raiz | Aprovado após corrigir links de código para o commit fixo |
| `git diff --check` / raiz | Aprovado |

A primeira execução backend sem configuração explícita falhou: `DEBUG=release` herdado
do ambiente era inválido (57 testes contabilizados, duas falhas e 23 erros). A execução
completa com valores sintéticos explícitos acima substitui esse resultado para avaliação
da suíte, sem esconder a falha de preparação. O primeiro build documental apontou cinco
links de código fora do diretório de documentação; corrigidos para URLs no commit da base,
e o build estrito foi repetido com sucesso.

A suíte determinística exercita os testes existentes de substituição, autorização,
vínculo e agregação; não equivale a contenção real de upsert no PostgreSQL. Não foram
executados nesta entrega: migrações em PostgreSQL, integração API/PostgreSQL, Compose,
navegador ou produção. Não há migration, interface ou mudança funcional neste diff.
A revisão visual em 320/390/768/1440 px não se aplica à entrega documental; futura
interface dependerá dessa checagem. Testes de novos controles continuam condicionados
às decisões da seção 1. Aceite e merge permanecem humanos.

## 8. Revisão da PR #276 — 16/11/2026

Escopo: os dois arquivos do diff em `c2725ec` contra `develop@d99916e`, incluindo
controles da seção 3 confrontados com os cinco arquivos de código citados em `0717614`
(sem alterações nesses arquivos em `d99916e`), requisitos vigentes e RF25 integrado.
Descrições e comentários da #270, do épico e das dependências de retomada foram conferidos.

Finding confirmado: a seção 6 deixava os registros exigidos pelo fluxo de execução fora
de ordem da #270 somente como textos para publicação. Sem registro no épico e checklists
nos destinos, as entregas fornecedoras não recebiam a retomada da #270. Correção em
`d49c732`: publicação autorizada e conferida dos cinco comentários, com links e estados
na seção 6.

Verificação local da revisão: `venv/Scripts/python.exe -m mkdocs build --strict --site-dir
site/review-pr276` e `git diff --check`, na raiz, aprovados com Python 3.14 e MkDocs 1.6.1.
O build valida a documentação local; o conteúdo dos comentários remotos foi conferido
separadamente. As suítes e builds da seção 7 são evidências da entrega original, não
reexecutadas nesta revisão documental. Sem mudança funcional, novos testes, ativação,
merge ou conclusão da #270.
