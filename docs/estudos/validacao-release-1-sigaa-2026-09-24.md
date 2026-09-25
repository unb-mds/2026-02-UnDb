# Validação local da importação SIGAA para a Release 1

**Data:** 24/09/2026 (America/Sao_Paulo; registros do banco em 25/09 UTC).

**Base:** `develop` no merge `bb1eef3`, com correção local para respostas sem resultados.

**Ambiente:** Docker Desktop 29.8.0, PostgreSQL 16 em projetos Compose isolados
`undb-r1-validation` e `undb-r1-all-units`, backend Python 3.12, período consultado
2026.2.

## Cobertura observada

O formulário público de consulta de turmas do SIGAA retornou 211 opções com IDs únicos.
Foram selecionadas as 55 cujo nome começa por `DEPARTAMENTO` ou `DEPTO`. Esse critério
identifica os departamentos explícitos no formulário; as outras 156 opções incluem
faculdades, institutos, programas de pós-graduação e unidades administrativas. A lista
foi obtida por `python pegar_id.py`, em `backend/`.

Uma amostra fora das 55 opções confirmou ofertas de graduação em outras categorias:
`INSTITUTO DE FÍSICA` reportou 204 e o campus Gama/FCTE reportou 229 ofertas em
2026.2. O PO confirmou depois que a cobertura deve abranger todas as opções com
turmas de graduação, inclusive institutos, faculdades e campi.
Uma tentativa para a Faculdade de Direito redirecionou para a página inicial e não
foi conclusiva.

O comando `scripts/cron/sigaa-import.sh` foi executado com as 55 opções contra o banco
isolado. A primeira execução processou 3.461 ofertas em 37 departamentos e falhou em 18:
dois redirecionamentos temporários do SIGAA e 16 respostas com zero ofertas sem total
numérico. Na repetição somente das falhas, um redirecionamento foi resolvido e 17
departamentos permaneceram com zero ofertas e total desconhecido. A resposta HTML
dessas 17 consultas continha explicitamente a mensagem de ausência de resultados.

Após a correção local do parser, a execução integral `6792be57-a690-41b1-a913-0e3a282dd14f`
terminou com `status=sucesso`: 55/55 departamentos sem erro, 38 com ofertas e 17 com
zero ofertas, 3.516 ofertas extraídas e 3.516 processadas. O banco continha 38 unidades
com ofertas, 1.802 disciplinas e 3.516 turmas ativas. Reimportações anteriores e a
execução final não produziram turmas duplicadas na contagem observada.

A suíte backend passou com 94 testes após a correção, incluindo casos de resposta
explícita com zero resultados e de resposta inesperada sem total. `git diff --check`
também passou.

## Validação ampliada para todas as unidades

Após a definição do escopo, as 211 opções do formulário foram passadas ao mesmo comando,
com filtro de nível `GRADUAÇÃO`. A execução `bca88ca7-c5f8-4432-821f-3d97ba849243`
validou 205 opções: 67 com ofertas e 138 sem turmas de graduação. Seis consultas falharam
por redirecionamento ou timeout. A repetição somente dessas seis, registrada como
`0864e60d-cd44-487c-b6ee-eb9ea3c67921`, passou integralmente: duas com ofertas e
quatro sem turmas. Assim, as 211 opções foram consultadas com resultado válido ao longo
das duas execuções, mas não houve uma execução única sem falhas transitórias.

As respostas válidas reportaram 6.555 linhas de oferta em 69 unidades; 142 opções não
tinham turmas de graduação em 2026.2. O banco terminou com 69 unidades com ofertas,
3.486 disciplinas e 6.554 turmas ativas. A diferença de uma linha vem do campus
Ceilândia: o SIGAA lista duas vezes a turma `FCE0794/03`, uma com docente identificada
e outra com `A DEFINIR DOCENTE`. O importador atual grava somente o docente da última
linha para essa turma. Além disso, 136 registros de professor no banco de teste têm
o nome literal `A DEFINIR DOCENTE`. Essas duas falhas de fidelidade precisam de
correção antes da release.

A execução foi iniciada com uma lista gerada manualmente a partir do formulário. O
agendador atual exige `SIGAA_DEPARTAMENTOS` configurado explicitamente e não enumera
as 211 opções por conta própria. A atualização futura de novas opções da fonte ainda
depende dessa configuração ou de automação adicional.

## Atualização periódica

O script de cron funcionou em execução controlada e gravou o histórico em
`importacao_execucoes`, incluindo sucessos e falhas. Não há crontab configurado para o
usuário local (`crontab -l` retornou `no crontab`), portanto **a execução periódica
automática ainda não foi demonstrada**. A instalação do agendamento local e a
observação de uma execução disparada no horário são necessárias para validar o RF18
operacionalmente.

## Limite para promoção

A correção do parser está rastreada na Issue #129 e precisa entrar em `develop` antes
da branch de release. A consulta a todas as 211 opções foi demonstrada localmente,
mas a perda de vínculo docente, o marcador tratado como professor, a configuração
da lista completa para execuções futuras e o agendamento real permanecem pendentes
antes da promoção para `main`.
