# Gotchas e segurança PostgreSQL

## Comportamentos do dialeto

- Identificadores não quotados são normalizados para minúsculas. Evite nomes quoted/mixed-case que obriguem aspas em toda query.
- FK garante referência, mas não cria índice automático na coluna referenciante.
- Gaps de `IDENTITY`/sequence são normais: concorrência, rollback e cache podem consumir valores. Não os use como contagem, ordem temporal ou evidência de perda.
- `UNIQUE` permite múltiplos `NULL` por padrão; analise `NOT NULL` ou semântica explícita.
- `TIMESTAMP` sem zona e `TIMESTAMPTZ` são semanticamente distintos; o segundo armazena instante normalizado em UTC e mostra na zona da sessão, sem preservar a zona de origem.
- MVCC não elimina manutenção: autovacuum/VACUUM são parte normal do ciclo do banco.

## Segurança

1. A conta da aplicação deve ter apenas privilégios necessários; conta de migration/administração não é automaticamente a mesma conta de runtime.
2. Credenciais e `DATABASE_URL` ficam fora do código e dos logs; nunca exponha senha, URI completa ou dump com dados sensíveis.
3. Use parâmetros do SQLAlchemy/driver para valores. Se for inevitável montar identificadores dinâmicos, use uma lista autorizada/validação estrita e não concatene entrada do usuário.
4. Mantenha aplicação, migrations e administração do banco com responsabilidades e permissões separadas quando a infraestrutura permitir.
5. Privilégios, papéis, row security, extensão ou ajuste de servidor são mudanças operacionais: proponha e peça aprovação, não aplique por esta skill.

## Referências conceituais

- [wshobson/agents — PostgreSQL table design](https://github.com/wshobson/agents/blob/main/plugins/database-design/skills/postgresql/SKILL.md)
- [PostgreSQL — data types](https://www.postgresql.org/docs/current/datatype.html), [constraints](https://www.postgresql.org/docs/current/ddl-constraints.html), [indexes](https://www.postgresql.org/docs/current/indexes.html), [EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html) e [privileges](https://www.postgresql.org/docs/current/ddl-priv.html)
- [SQLAlchemy — PostgreSQL dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [Alembic — autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
