# Revisão da PR #225 — 12/11/2026

Solicitação de Gabriel: revisar a continuidade da #223 e corrigir findings em
commits separados. Revisão técnica e correções locais; sem aprovação formal,
push, merge ou operação em produção.

## Escopo e fontes

- [PR #225](https://github.com/unb-mds/2026-02-UnDb/pull/225), head
  `763ef5a5d39cf9c94ea19801ea734abac404ae19`, base `develop` `658de6e`.
- [PR #223](https://github.com/unb-mds/2026-02-UnDb/pull/223), sua descrição,
  discussão e implementação de reconciliação, usada como contexto.
- RF23, RF03 e RNF02 em [requisitos](../requisitos.md), extensão de
  [specs](https://github.com/unb-mds/2026-02-UnDb/blob/763ef5a5d39cf9c94ea19801ea734abac404ae19/specs.md), evolução do ADR 07 em
  [arquitetura](../arquitetura.md) e [guia operacional](../identidades-docentes.md).
- Skills canônicas de revisão, implementação, testing e governança; orientações
  técnicas de FastAPI, modelagem, PostgreSQL e frontend, preservando seus estados.

Inspecionados o diff textual da PR, o coletor, os fluxos de importação/decisão e
aplicação administrativa, permissões, models/migration, contratos, interface e
testes relacionados. As capturas históricas da PR não foram tratadas como prova
de execução atual. Os novos testes de navegador usam somente HTTP fictício.

## Findings corrigidos

### 1. A prévia sem união era recusada pelo frontend

`PreviaResponse` serializa `turmas` e `avaliacoes` como `null` quando não há
união. `consultarPrevia` só aceitava números ou campos ausentes. A tela mostrava
erro e mantinha a confirmação desabilitada justamente nesse fluxo.

O contrato TypeScript agora distingue prévia com/sem união: aceita contagens
nulas sem união e exige números quando há união. Os dois testes de contrato
falharam antes da correção e passaram depois. O navegador também confirmou o
carregamento da prévia e o envio da decisão.

Commit: `7b681cb`.

### 2. Destino existente dispensava a validação institucional da origem

Em `resolver`, uma origem com identidade A podia receber uma inferência para B
já cadastrado. A existência do destino pulava `vincular`, deixando a ocorrência
`CONFIRMADA` apesar da identidade conflitante.

A validação agora ocorre também para destinos existentes. O conflito deixa a
ocorrência `PENDENTE`, com motivo `CONFLITO_INSTITUCIONAL`, sem destino agendado
nem alteração dos vínculos. O teste reproduziu `CONFIRMADA` antes e passou após
a correção, preservando os dois identificadores e UUIDs.

Commit: `8727d17`.

### 3. O lote só verificava a identidade da primeira origem

Entre a confirmação e a aplicação, outra ocorrência podia definir uma identidade
divergente para uma origem secundária. O lote validava apenas a primeira origem;
a reconciliação da #223 verifica colisões de avaliações, mas desconhece a nova
tabela institucional. O grupo podia ser unido incorretamente.

Todas as origens são revalidadas dentro do savepoint antes de mover dependentes.
O teste antes retornava `APLICADA`; agora retorna `BLOQUEADA`, mantém as
confirmações, desfaz a identidade criada no início do grupo e preserva o UUID,
a avaliação e a identidade divergente da outra origem. Validado em PostgreSQL.

Commit: `ffc3685`.

### 4. Uma decisão atrasada apagava a nova seleção da fila

Após enviar uma decisão, atualizar a fila e selecionar outro docente, o callback
de sucesso do formulário desmontado executava `atualizar` no componente pai.
Isso apagava a seleção atual e exibia sucesso de uma interação antiga.

O formulário cancela a espera pelo POST ao desmontar e ignora seus callbacks
posteriores. O teste de navegador falhou antes com a seleção de Docente Beta
apagada e passou depois. Cancelar a espera não promete desfazer uma decisão que
o servidor já tenha persistido; a leitura seguinte continua sendo a autoridade.

Commit: `239cb85`. O runner foi integrado a `test:browser` em `5f6cac7`.

### 5. Decisões aguardavam sem limite o lock da importação

O importador mantém o advisory lock transacional enquanto consulta o SIGAA.
A decisão aguardava esse mesmo lock sem timeout; o limite da reconciliação era
configurado apenas depois da aquisição desse lock.

`bloquear` agora aplica o mesmo limite de cinco segundos já usado pela #223.
Na API, SQLSTATE `55P03` causa rollback e resposta 409 orientando nova tentativa.
O teste com duas conexões ficou bloqueado até a liberação manual antes da
correção. Depois, recebeu 409, comprovou ausência de decisão/auditoria parcial e
conseguiu decidir uma única vez após liberar o lock.

Commit: `39c0198`.

## Verificações executadas

| Verificação | Resultado |
| --- | --- |
| Ruff e formatação do backend | Aprovados; 128 arquivos formatados |
| Compilação Python de `app` e `alembic` | Aprovada |
| Identidades e reconciliação | **33 testes aprovados**: 29 com PostgreSQL 16, três do coletor e um HTTP com fixture SQLite; conflitos, colisões, rollback, contenção e nova tentativa |
| Alembic em PostgreSQL 16 vazio | Cadeia até `20261111_01` aprovada; `alembic check` sem divergências |
| Frontend unitário | **77 testes aprovados** |
| ESLint | Aprovado |
| Build padrão Next.js/Turbopack em Docker/Linux | Aprovado, usando o lockfile |
| Build local Next.js/Webpack | Aprovado, incluindo TypeScript |
| `npm run test:identidades` | Aprovado: prévia nula, POST atrasado, 403, teclado e overflow em 320/768/1280 px |
| MkDocs estrito e `git diff --check` | Aprovados |

O teste emulou preferências clara e escura do sistema. A aplicação atual fixa o
tema escuro em seu layout/CSS; isso não constitui validação de um tema claro da
aplicação. Capturas locais foram produzidas e as larguras 320 e 1280 px foram
inspecionadas visualmente. A suíte completa de navegador anterior não foi
reexecutada; o novo runner integra o comando usado pelo CI.

O PostgreSQL foi um container exclusivo `undb-review-225-postgres`, banco
descartável `undb_207_test`, porta local 55425, sem dados reais. As credenciais
são apenas de fixture local. Não houve concessão de papel ou operação no banco
da aplicação pública.

## Limitações e falha preexistente

A suíte completa em Python 3.12/Linux executou **221 testes: 218 aprovados,
dois pulados** (exclusivos de PostgreSQL) **e uma falha** em
`test_explicit_migration_connection_does_not_migrate_runtime_database`.
A mesma falha já foi reproduzida e registrada na
[revisão da #223](reconciliacao-professores-issue-207.md). O teste, a configuração
e `alembic/env.py` estão idênticos a `origin/develop`; não são mudanças da #225.
A suíte inteira não é declarada verde.

No Windows/Python 3.14 também houve `WinError 32` na limpeza de SQLite do outro
teste de conexão de migration. O build padrão Turbopack falhou no Windows ao
conectar seu processo auxiliar; o build padrão passou em Linux e o build
Webpack local passou sem alterar configuração versionada.

Não foram refeitas coleta institucional real, implantação, backup/restauração,
união de dados reais ou verificação operacional de produção. As evidências
históricas da PR conservam seu próprio escopo. As cinco correções foram
verificadas; a aprovação humana e a aplicação operacional permanecem separadas.
