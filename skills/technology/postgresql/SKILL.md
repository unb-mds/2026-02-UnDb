---
name: postgresql
description: Aplica, revisa e valida particularidades do PostgreSQL na realização de um modelo relacional autorizado. Use ao escolher tipos, constraints, índices, consultas, privilégios ou migrations PostgreSQL, sem decidir o modelo de dados ou alterar código.
metadata:
  project-version: "0.1.0"
  project-status: "proposed"
  project-category: "technology"
  project-scope: "postgresql-specific-database-practices"
  agent-agnostic: "true"
---

# PostgreSQL

## 1. Objective

Orientar a criação, revisão e manutenção técnica do banco PostgreSQL do G7 para realizar um modelo de dados autorizado com integridade, segurança e desempenho verificável.

## 2. Scope

Esta skill cobre semântica e recursos específicos do PostgreSQL: tipos, constraints, chaves e FKs, `NULL`, índices, planos de consulta, MVCC/VACUUM, identificadores, segurança de acesso e a tradução para SQLAlchemy síncrono e Alembic. Ela não decide entidades, regras de produto, cardinalidades ou o modelo relacional.

## 3. When to use

Use ao converter um modelo autorizado em DDL/mapping PostgreSQL; revisar uma migration, constraint, índice, tipo ou query; investigar plano de execução, N+1, manutenção do banco ou privilégio; ou verificar a compatibilidade entre PostgreSQL, SQLAlchemy e Alembic.

## 4. When not to use

- `database-design` analisa e prepara propostas de modelo conceitual/lógico, normalização e regras estruturais; requisitos e arquitetura preservam a autoridade sobre decisões aprovadas.
- `requirements` define regras de produto e critérios de aceite.
- `architecture` trata decisões sistêmicas de maior nível.
- `implementation` altera código e migrations autorizados.
- Uma futura `migrations` pode governar o ciclo operacional de migrations; esta skill apenas trata implicações PostgreSQL de uma migration.

## 5. Expected inputs

Use somente fontes autorizadas: requisito e modelo aprovados; schema, migration e mapping atuais; padrões de consulta; resultado de `EXPLAIN`/`EXPLAIN ANALYZE` quando houver; e permissões/ambiente conhecidos. A stack definida pelo ADR 01 em `docs/arquitetura.md` é PostgreSQL, SQLAlchemy síncrono, Alembic e `psycopg2`; não substitua nenhum elemento.

## 6. Pre-conditions

1. Confirme a fonte da regra e classifique decisões como `Defined`, `Proposed`, `Pending Decision` ou `Not Currently Applicable`.
2. Determine se a questão é de modelo (`database-design`), produto (`requirements`), arquitetura, implementação ou PostgreSQL.
3. Inspecione os artefatos PostgreSQL/SQLAlchemy/Alembic relevantes e separe fato, inferência e proposta.
4. Para performance, obtenha consulta representativa e evidência; não use preferência como justificativa.

## 7. Procedure

1. Parta do modelo e das regras já autorizados. Relate, sem corrigir silenciosamente, divergências entre documentação, mapping, migration e banco.
2. Escolha ou revise o tipo PostgreSQL pelo significado, domínio, volume, precisão, consulta e interoperabilidade; não por hábito. Leia [data types](references/data-types.md).
3. Materialize invariantes com `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL`, `CHECK`, `DEFAULT` e constraints compostas quando o banco puder garanti-los. Avalie `NULL` em `UNIQUE` explicitamente. Leia [constraints](references/constraints.md).
4. Relacione cada índice a join, filtro, ordenação ou constraint conhecida. Avalie ordem de colunas e custo de escrita; não indexe indiscriminadamente. Leia [indexes](references/indexes.md).
5. Para suspeita de desempenho, examine query, cardinalidade e plano com `EXPLAIN`; use `EXPLAIN ANALYZE` somente de modo seguro e com autorização para executar a consulta. Investigue N+1 e leituras excessivas antes de propor índice ou desnormalização. Leia [performance](references/performance.md).
6. Revise identificadores, MVCC, VACUUM, sequences/identity, timezone e demais comportamentos do dialeto antes de concluir que há defeito. Leia [PostgreSQL gotchas](references/postgresql-gotchas.md).
7. Preserve segurança: menor privilégio, credenciais em configuração externa, queries parametrizadas e separação entre papel da aplicação e administração do banco.
8. Produza uma decisão técnica proposta ou revisão; faça handoff para `database-design`, `requirements`, `architecture` ou `implementation` conforme a pendência.

## 8. Expected output

Produza, conforme o caso: decisão técnica e estado; justificativa e fontes; SQL/mapping/migration afetado; constraints e índices; riscos e conflitos; impacto em SQLAlchemy e Alembic; verificações necessárias; e aprovação ou handoff pendente.

## 9. Constraints

Nunca troque PostgreSQL, ORM, driver ou ferramenta de migration; invente regra de produto/modelo; altere schema aprovado sem autorização; transforme preferência técnica em decisão definida; exponha credencial/senha; construa SQL dinâmico com dados não parametrizados; ou alegue ganho de performance sem evidência.

## 10. Human approval

O agente pode analisar, revisar e preparar propostas. Mudança de schema, índice, privilégio, configuração de manutenção, tipo que altere semântica, ou resolução de conflito permanece `Pending Decision` até aprovação humana aplicável; `implementation` executa a mudança aprovada por migration Alembic.

## 11. Verification

- [ ] O modelo/requisito usado como fonte foi identificado.
- [ ] Tipo, nulidade e constraint representam o significado autorizado.
- [ ] `UNIQUE` foi avaliada quanto a `NULL` e concorrência quando aplicável.
- [ ] Cada FK e índice tem justificativa explícita; nenhum índice de PK/UNIQUE foi duplicado.
- [ ] Performance usa query e plano/evidência, quando é a motivação.
- [ ] Mapping SQLAlchemy, migration Alembic e schema foram comparados quando acessíveis.
- [ ] Credenciais, parâmetros e privilégios respeitam os limites de segurança.
- [ ] Conflitos, riscos e decisões pendentes estão explícitos.

## 12. Interaction with other skills

`project-governance` e `skill-authoring` definem autoridade e ciclo desta skill. `database-design` analisa o modelo e prepara propostas sem aprová-las; `requirements` fornece regras de produto autorizadas; `architecture` fornece decisões estruturais aprovadas e recebe novas decisões; `implementation` aplica alterações autorizadas; `testing` verifica efeitos. Esta skill aplica PostgreSQL à stack definida e não substitui essas responsabilidades.

## 13. Handling uncertainty and failures

Se regra, query, versão do PostgreSQL, permissão ou estado do banco estiver ausente, declare o limite e continue somente a análise sustentada. Se documentação, modelo, SQLAlchemy, migration, banco, Issue ou PR divergirem, cite o conflito e mantenha sua resolução como `Pending Decision`. Se `EXPLAIN ANALYZE` puder executar mutação ou causar impacto, não o execute sem contexto seguro e autorização.

## 14. Example: Avaliações do G7

Para `UNIQUE(usuario_id, professor_id, disciplina_id)`, confirme três FKs não nulas e a constraint composta no banco/migration; PostgreSQL cria o índice único que a sustenta, portanto não duplique esse índice. A constraint garante uma linha por combinação, mas o reenvio que substitui a anterior continua sendo responsabilidade do repository/service autorizado. Revise o mapping SQLAlchemy, a migration e testes de violação de unicidade, FK e atualização; não acrescente regras de produto.
