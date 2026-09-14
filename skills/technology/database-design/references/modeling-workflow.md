# Workflow de modelagem e validação

## Fontes e estados

Monte rastreabilidade: afirmação, fonte, estado (`Defined`, `Proposed`, `Pending Decision` ou `Not Currently Applicable`) e impacto. Ausência de requisitos/arquitetura não autoriza preencher lacunas pelo schema existente.

## Entregável mínimo

1. Requisitos usados como fonte.
2. Entidades, atributos e chave candidata/primária.
3. Relacionamentos, cardinalidades e participação quando houver fonte.
4. PK, FK, UNIQUE, NOT NULL, CHECK, DEFAULT e constraints compostas, com justificativa.
5. Dependências funcionais, forma normal, redundância e anomalias.
6. Índices e padrão de consulta que os justifica.
7. Riscos, conflitos e pendências com responsável pelo handoff.
8. Impacto proposto em SQLAlchemy, migration e testes.

## Comparação de artefatos

Compare entidades, colunas, nulidade, FKs, constraints e índices entre modelo, SQLAlchemy, migration e banco. `relationship()` habilita navegação ORM, mas não substitui `ForeignKey`; mapeamento declarativo deve materializar constraints do modelo. Alembic versiona evolução em migrations revisáveis; `create_all` não substitui migration auditável para evolução autorizada.

## Referências conceituais externas

- [wshobson/agents — PostgreSQL table design](https://github.com/wshobson/agents/tree/main/plugins/database-design/skills/postgresql)
- [sickn33/agentic-awesome-skills — database design](https://github.com/sickn33/agentic-awesome-skills)
- [softaworks/agent-toolkit — database schema designer](https://github.com/softaworks/agent-toolkit/tree/main/skills/database-schema-designer)
- [PostgreSQL — constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) e [indexes](https://www.postgresql.org/docs/current/indexes.html)
- [SQLAlchemy — declarative](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html) e [relationships](https://docs.sqlalchemy.org/en/20/orm/relationships.html)
- [Alembic — tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
