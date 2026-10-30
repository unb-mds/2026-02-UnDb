# Navegação integrada — Issue #155

## Base, investigação e autoridade

Reavaliação de 27–28/10/2026. Foram consultadas no GitHub as descrições e comentários
atuais de #155, #144, #148, #153, #157 e #158, além das PRs #183/#184 e suas revisões.
As duas últimas estão integradas e as dependências encerradas; a #155 permanece aberta.
Base desta implementação: `ed9aa0f660d26d33e84fc57bf8d3201f966dafa3`, merge da #184.

O checkout inicial estava em `feature/155-navegacao-busca-resultados`, sobre `91ecb79`,
com 18 arquivos da tentativa anterior sem commit. Esse conjunto foi preservado
integralmente em stash identificado `backup local da tentativa anterior da issue 155 -
2026-10-27`. Foi criada `feature/155-navegacao-integrada` sobre `origin/develop`, sem
merge, reset ou descarte. Somente os módulos reaproveitáveis da #155 foram recuperados
e revisados; as entregas finais de #157/#158 são a base efetiva.

`docs/specs.md` não existe; a especificação derivada é `specs.md` na raiz. Requisitos,
arquitetura, estudos da #148/#153 e relatórios de verificação das #157/#158 foram
confrontados com código e testes atuais. Skills aplicadas: implementation, testing,
gerador-paginas-next-tailwind, project-governance, fastapi, requirements e code-review.

**Decisão autorizada nesta reavaliação:** ampliar `return_to` de forma retrocompatível,
permitindo apenas `busca`, `q` e `ordem` e até 2.048 caracteres no destino completo,
validado no frontend e no backend. A autorização humana foi solicitada porque o
contrato final da #158 proibia query e limitava o campo a 200 caracteres. Registrada
em [requisitos](../requisitos.md) e propagada para a especificação. Não há nova regra
de autenticação ou armazenamento de respostas.

## Matriz de rastreabilidade

Fontes: [ALUNO-01](relato-usabilidade-aluno-01-issue-148.md),
[ALUNO-02](relato-usabilidade-aluno-02-issue-148.md),
[consolidação da #148](observacao-jornada-busca-comparacao.md),
[reteste](resultados-reteste-jornada-issue-153.md),
[ajustes do protótipo](ajustes-prototipo-jornada-issue-153.md).

| Achado | Fonte/trecho | Evidência e limite | Ajuste | Rotas/componentes | Requisito | Verificação |
|---|---|---|---|---|---|---|
| OBS-03 / RT-01 | ALUNO-01 §3: pesquisa perdida ao voltar; reteste §2: elogiou retorno | Problema relatado e melhora percebida; histórico/termo não confirmados pelo participante | URL como fonte da busca; contexto nos links de ida/volta e no acesso | buscas, detalhes, consulta, avaliar, contexto-busca | RF04–RF07; #155 | Lógica; navegador: retorno, histórico, recarga e autenticação |
| OBS-09 / RT-02 | Reteste §2: dúvida sobre nome/departamento; §4: mover ordenação à lista | Dúvida relatada; solução posterior não retestada | Nome/unidade na lista, sem nova consulta, com explicação institucional | busca-institucional, ordenarResultados | RF05–RF07; RF13 preservado | Conjunto completo, acentos/homônimos, união código/nome e ausência de HTTP ao ordenar |
| OBS-01/02/04/10; A02-01/03 | Relatos §3: confusão, matéria/unidade e número pouco claros | Causa da repetição/número não confirmada; nenhuma união por nome autorizada | Reutilizar cartões e disciplinas da #157; propagar contexto sem duplicar apresentação | ProfessorResultado, DisciplinasProfessor, detalhes/comparação | RF05–RF12, ADR07, RNF02 | Vínculos por UUID, atalhos e regressão real da #157 |
| OBS-06; A02-02; RT-03 | Relatos: difícil chegar à avaliação; reteste menciona formulário visual | Não há medição de cliques nem confirmação de envio no reteste | Atalho da #157 leva ao formulário da #158 com busca preservada | resultados/professor → avaliar → conta → avaliar | RF14, RF01/RF02 | Jornada com API/PostgreSQL, confirmação console, duas abas e gravação nos destinos |
| OBS-05/08 / RT-04 | Login pouco intuitivo; sugestão de revelar senha; reteste apontou pesquisa acima da conta | Falha visual no protótipo, sem falha real de autenticação comprovada | Entrada única de conta, senha acessível; manter formulários #158 sem etapas de pesquisa | cabecalho, CampoSenha, LoginForm, CadastroForm | RF01/RF02/RF04/RF14 | Mouse/Enter/Tab, foco/rótulos, validações e estados reais de acesso |
| Estados inicial/vazio/erro | Critério da #155 | Critério técnico; não alegado como achado empírico | Mensagens distintas, repetir consulta e descartar resposta obsoleta | busca-institucional e serviços existentes | RF05/RF06; RF10 trata ausência de avaliações | Navegador com erro/recuperação e corrida de respostas |

RT-03 é atendido pela apresentação entregue na #158, reutilizada integralmente.
OBS-07 (rótulos dos critérios) também permanece nessa entrega. Foto do SIGAA,
localização física, perfil/histórico e mudanças de escalas/comparação estão excluídos.
Nenhum teste técnico abaixo é apresentado como reteste com alunos; isso continua #166.

## Contratos e integração

- Os repositories atuais retornam todas as correspondências com `.all()`, sem
  paginação, `limit`, `offset` ou cursor. `buscarDisciplinas` já une por ID as consultas
  por código e nome. Ordenar depois dessa união organiza todo o resultado atual.
  Uma API paginada futura deverá ordenar antes de paginar; ordenação local de páginas
  não é garantida por esta implementação e exigirá revisão própria do contrato.
- `departamento` é a unidade institucional disponível; não representa sala ou prédio.
  A comparação continua no backend por recomendação, contagem e nome; nenhuma nota
  composta, novo critério ou percentual artificial foi criado.
- `ProfessorResultado` e `DisciplinasProfessor` da #157 recebem o contexto opcional;
  suas consultas, apresentação, estados independentes e IDs foram preservados.
- Login, cadastro, confirmação e avaliação da #158 foram reutilizados. Cada link
  conserva seu destino e contexto; não há localStorage, sessão global do frontend
  ou rascunho. `return_to` antigo continua válido. Parâmetros extras/duplicados,
  fragmentos, origem externa, controles e escapes inválidos são recusados.
- Cabeçalho preserva o destino ao entrar pela avaliação ou circular entre login e
  cadastro. Na confirmação, só a ação de sucesso oferece a continuidade contextual;
  um token inválido/consumido não oferece essa ação.
- A única mudança de API é a ampliação autorizada da validação de `return_to`.
  Cookies, tokens, exigência de e-mail confirmado, schemas de consulta/avaliação,
  persistência, escalas e agregação não foram modificados. Não há migration nova.

## Plano executado e verificações

1. Revisar a tentativa anterior contra as dependências integradas.
2. Reaproveitar o estado de URL e ordenação, conectando-os aos componentes finais.
3. Integrar conta/senha e contexto nos links autenticados com validação dos dois lados.
4. Cobrir contratos, estados, histórico, teclado e jornada real; revisar diff e evidências.

Ambiente: Windows, Node.js 24.21.0, Next.js 16.3.5, Edge headless, Python 3.12 na
imagem local do backend, PostgreSQL 16 em banco descartável. O build padrão usa
Turbopack; não foram alteradas dependências, lockfiles ou configuração de build.

| Comando | Resultado |
|---|---|
| `npm test` em `frontend/` | **26 testes aprovados**: 20 anteriores e 6 de busca/retorno. Incluem 155 itens, homônimos, acentos, união código/nome, falha parcial, parâmetros recusados e limite Unicode consistente com Pydantic |
| `npm run lint` em `frontend/` | Aprovado sem warnings finais |
| `npm run build` em `frontend/` | Aprovado com Turbopack padrão, TypeScript e geração das rotas |
| `python -m unittest discover -s tests -q` em `/app` da imagem local do backend, com código montado somente para leitura | **106 testes aprovados**, incluindo três testes novos do contrato de retorno |
| `alembic upgrade head` no banco isolado | Aprovado até `20260921_01`; nenhuma migration nova criada |
| `npm run test:browser`, com `PREVIEW_DIR` temporário | Suíte completa aprovada: #155, regressões de avaliação/acesso/confirmação e protótipo existente |
| `node tests/acesso-browser.mjs`, com `E2E_ACESSO_CONTAINER=undb-155-api`, manifesto de `tests.integration_acesso --prepare` e `PREVIEW_DIR` de evidências | **48 combinações aprovadas**, telas → API → e-mail console → PostgreSQL, sem mocks HTTP |
| `node tests/resultados-browser.mjs`, com `RESULTADOS_FIXTURE_FILE` de `tests.seed_resultados` e `PREVIEW_DIR` de evidências | **48 combinações aprovadas**, API/PostgreSQL reais, preservando a regressão da #157 |
| `node --check frontend/tests/acesso-browser.mjs` e `node --check frontend/tests/resultados-browser.mjs` | Aprovados |
| `git diff --check` | Aprovado; apenas avisos de conversão LF/CRLF do Git |

A suíte controlada cobre ambas as buscas em 320/768/1280 px e claro/escuro:
inicial, termo curto, carregamento, resultados, troca de ordem sem HTTP, retorno,
histórico, recarga, vazio, erro e recuperação. Verifica corrida de respostas, links
relacionados, senha por Enter, Tab do campo ao seletor, rótulos e foco visível.
Nenhuma fixture foi incluída no produto; o cenário controlado só roda no processo de teste.

A jornada real começa nas buscas: o primeiro destino usa o atalho de avaliar no
cartão do professor; o segundo parte da busca de disciplina. Ambos preservam
termo/modalidade/ordem até login/cadastro, nos links reais emitidos pelo serviço
console, após confirmação em abas distintas e até o retorno à lista depois do envio.
Foram verificadas credenciais inválidas, sessão ativa/ausente, e-mail pendente,
rejeição sem perder respostas, cookies HttpOnly/SameSite, logout e token consumido.
O banco confirmou **duas avaliações**, cada uma no professor correto, com respostas
negativas preservadas. O cenário de confirmação inválida não oferece ação contextual.

A regressão da #157 verifica agrupamento sem duplicatas, homônimos por ID,
turma ausente, conflito, contagens, ocultação de critérios abaixo de três avaliações,
ordenação da comparação e falha real de transporte complementar sem esconder o
professor. Os seletores agora reconhecem a mesma rota com query de contexto; as
asserções de entidade, contagem, foco e privacidade foram mantidas.

### Evidências e inspeção visual

- [Resultado estruturado de acesso](evidencias/issue-155/acesso/resultado.json).
- [Resultado estruturado de resultados/comparação](evidencias/issue-155/resultados/resultado.json).
- [Busca agrupada, 320 escuro](evidencias/issue-155/acesso/busca-professores-dark-320.png).
- [Confirmação, 320 escuro](evidencias/issue-155/acesso/confirmacao-dark-320.png).
- [Avaliação gravada, 1280 claro](evidencias/issue-155/acesso/sucesso-light-1280.png).
- [Comparação, 320 escuro](evidencias/issue-155/resultados/comparacao-dark-320.png).

Essas quatro capturas foram inspecionadas visualmente, junto das verificações
automáticas de largura, foco, textos e interações. Há 32 capturas e dois resumos
estruturados no repositório; os manifestos temporários com dados dos testes ficam
fora dele. Não há tokens ou senhas nos resumos/capturas versionados.

### Falhas encontradas e correções necessárias

1. O primeiro build acusou flag de regex incompatível com o alvo ES2017. A separação
   da query passou a usar operações de string; o build padrão passou depois disso.
2. A primeira jornada real não encontrava os professores preparados pela #158:
   `nome_normalizado` estava vazio, pois a preparação antiga só abria os IDs. O driver
   agora preenche esse campo com o normalizador existente para professores/disciplinas.
   Não houve alteração da importação, consulta ou dado de produção.
3. O primeiro teste real completo detectou retorno contextual no cabeçalho de uma
   confirmação já consumida. O cabeçalho só reaproveita `returnTo` em login/cadastro;
   a confirmação oferece continuidade exclusivamente na ação de sucesso da #158.
   Reexecutada com dados novos, a jornada completa passou.
4. O lint inicial apontou um import sem uso, removido. Na revisão, o limite de
   caracteres do frontend foi alinhado à contagem Unicode do Pydantic e ganhou
   cobertura de fronteira nos dois lados.
5. A regressão controlada de hidratação agora finaliza a navegação anterior em
   `about:blank` antes de pausar scripts, sem ignorar erros ou retirar asserções.
   As visitas genéricas de conta usam a entrada única e o link de cadastro atual,
   conforme o novo cabeçalho, mantendo a verificação de isolamento dos destinos.

### Limites e verificações não executadas

- `python -m mkdocs --version` falhou por módulo ausente. O build de documentação
  não foi executado; links locais e Markdown foram revisados diretamente.
- Não houve teste com dispositivo físico, leitor de tela, nova importação SIGAA
  ou participante. Os viewports móveis são emulados. Reteste qualitativo é #166;
  envio externo de e-mail é #165. O adaptador console é o modo real de desenvolvimento.
- Os dados da API/PostgreSQL são sintéticos, persistidos e isolados, sem mock de
  resposta nas duas suítes reais. Não representam dados de produção ou métricas de uso.
- O contexto autenticado obedece ao limite autorizado de 2.048 caracteres. Queries
  de retorno fora do contrato não são aceitas como destino. Uma futura paginação
  de busca exigirá revisão antes de afirmar ordenação global.
- Foi usada a imagem local existente do backend, sem rebuild de imagem ou mudança
  de infraestrutura. A única alteração de contrato foi expressamente autorizada.

## Revisão, limpeza e critérios de aceite

O diff contra `ed9aa0f` foi revisado, incluindo arquivos novos, testes e evidências.
As entregas #157/#158 não foram reimplementadas. Não foram incluídos dados do usuário,
`.env`, credenciais, logs de produto ou alterações alheias. O backup da tentativa
anterior permanece em stash. Containers `undb-155-api`/`undb-155-db` e rede
`undb-155-net`, criados para esta tarefa, foram encerrados/removidos; containers
preexistentes não foram alterados. A revisão local não substitui a revisão humana.

- [x] Ajustes relacionados aos achados #148 e RT-01 a RT-04, com limites de evidência.
- [x] Termo, modalidade e ordem preservados em links, histórico, recarga e acesso.
- [x] Ordenação na lista por nome/unidade, sem refazer consulta.
- [x] Alcance global conferido no contrato atual sem paginação.
- [x] Disciplinas agrupadas e avaliação direta reutilizando #157.
- [x] Conta identificável, controle de senha e continuidade real reutilizando #158.
- [x] Estados e interações verificados em desktop e viewport móvel, com teclado.
- [x] Requisitos/contratos preservados, salvo ampliação de retorno autorizada.

Não há dependência bloqueadora de #157/#158 restante nesta entrega. A #155 está
pronta para revisão dentro dos limites registrados; publicação/aceite são humanos.

Branch local: `feature/155-navegacao-integrada`. Implementação, contratos e testes
no commit `660528e` (`feat(ux): integrar navegação e contexto das buscas (#155)`).
Este relatório e as evidências compõem um segundo commit documental. Nenhum push,
PR, merge ou encerramento de issue foi executado nesta tarefa.

## Proposta de PR para develop

**Título:** `feat(ux): integrar navegação, busca e retorno à avaliação (#155)`

**Descrição sugerida:**

> Preserva termo, modalidade e ordenação da busca nos resultados, detalhes e fluxo
> de avaliação, reutilizando os componentes finais de #157/#158. Adiciona ordenação
> por nome/unidade sem nova consulta, recuperação de busca e controle acessível de senha.
>
> Amplia `return_to` somente com os parâmetros de busca autorizados, mantendo
> validação nos dois lados, isolamento por link e compatibilidade com destinos antigos.
>
> Validação: 26 testes frontend, 106 backend, lint, build padrão, suíte controlada
> completa e duas suítes com API/PostgreSQL reais (48 combinações cada) aprovados.
> Evidências e matriz na documentação da #155. Viewport móvel emulado e e-mail console;
> reteste com alunos e envio externo seguem nas issues próprias.
>
> Closes #155
