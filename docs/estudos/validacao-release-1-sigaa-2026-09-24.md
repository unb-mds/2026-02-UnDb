# Validação local da importação SIGAA para a Release 1

**Data:** 24/09/2026 (America/Sao_Paulo; registros do banco em 25/09 UTC).

**Base:** `develop` no merge `bb1eef3`, com correção local para respostas sem resultados.

**Ambiente:** Docker Desktop 29.8.0, PostgreSQL 16 em projeto Compose isolado
`undb-r1-validation`, backend Python 3.12, período consultado 2026.2.

## Cobertura observada

O formulário público de consulta de turmas do SIGAA retornou 211 opções com IDs únicos.
Foram selecionadas as 55 cujo nome começa por `DEPARTAMENTO` ou `DEPTO`. Esse critério
identifica os departamentos explícitos no formulário; as outras 156 opções incluem
faculdades, institutos, programas de pós-graduação e unidades administrativas. Esta
execução não determina se alguma dessas opções adicionais precisa entrar no escopo do
RF17. A lista foi obtida por `python pegar_id.py`, em `backend/`.

Uma amostra fora das 55 opções confirmou ofertas de graduação em outras categorias:
`INSTITUTO DE FÍSICA` reportou 204 e o campus Gama/FCTE reportou 229 ofertas em
2026.2. Isso reforça a necessidade de decidir se o RF17 exige também essas unidades.
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

## Atualização periódica

O script de cron funcionou em execução controlada e gravou o histórico em
`importacao_execucoes`, incluindo sucessos e falhas. Não há crontab configurado para o
usuário local (`crontab -l` retornou `no crontab`), portanto **a execução periódica
automática ainda não foi demonstrada**. A instalação do agendamento local e a
observação de uma execução disparada no horário são necessárias para validar o RF18
operacionalmente.

## Limite para promoção

A correção do parser está rastreada na Issue #129 e precisa entrar em `develop` antes
da branch de release. A cobertura das 55 opções explicitamente identificadas como
departamentos foi demonstrada neste
ambiente; a interpretação das demais opções acadêmicas para RF17 e o agendamento real
permanecem pendentes antes da promoção para `main`.
