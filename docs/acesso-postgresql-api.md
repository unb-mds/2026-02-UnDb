# Separar acesso da API e das migrações — #170

Registro e preparação de 10/11/2026. O operador confirmou que o Render usa
`neondb_owner`. A consulta fornecida mostra `CREATEDB`, `CREATEROLE`,
`REPLICATION` e `BYPASSRLS` habilitados nesse papel. Isso não demonstra acesso
mínimo. Este roteiro não afirma que a troca no ambiente público foi executada.

Na sessão, o operador criou `undb_api`, executou os GRANTs e confirmou a definição
de senha privada. A consulta de conferência apresentada retornou poderes
administrativos falsos, lista vazia de papéis herdados e `CREATE` falso no banco
e no schema `public`. Isso comprova a preparação mostrada no Neon, mas ainda não
o uso desse papel pela API pública. A matriz de privilégios efetivos por tabela e
a validação após a troca no Render continuam necessárias.

## Comportamento do backend

- `DATABASE_URL`: conexão das sessões da API e dos comandos de importação.
- `MIGRATION_DATABASE_URL`: conexão usada somente pelo Alembic. Se a variável
  não existir, o comportamento anterior permanece: Alembic usa `DATABASE_URL`.
- No inicializador hospedado, `alembic upgrade head` continua precedendo Uvicorn.
  Não é necessário mudar o Docker Command para usar a nova variável.

As duas conexões devem apontar para o mesmo banco, branch Neon e schema,
usando o driver `postgresql+psycopg2` e TLS. A conexão administrativa continua
armazenada no ambiente do serviço: esta alteração separa os privilégios das
conexões, mas não isola o segredo administrativo do processo hospedado.

## Ordem de aplicação

1. Publicar o ajuste do Alembic pelo fluxo autorizado do projeto. Não trocar
   `DATABASE_URL` por um papel limitado antes dessa publicação.
2. No Render, configurar `MIGRATION_DATABASE_URL` com a conexão administrativa
   privada, mantendo por enquanto `DATABASE_URL` como está. Fazer deploy e
   verificar as migrações. Não publicar os valores em capturas ou issues.
3. No SQL Editor do Neon, no banco usado pela API, criar o papel com SQL.
   Papéis criados pelo painel do Neon podem receber `neon_superuser`.

   ```sql
   CREATE ROLE undb_api WITH LOGIN
     NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
   ```

   O papel ainda não tem senha nem permissões para servir a API. Definir uma
   senha exclusiva por um mecanismo privado, por exemplo `\password undb_api`
   em psql. Nunca salvar a senha neste documento. Se ela for definida pelo SQL
   Editor, não compartilhar o texto/histórico contendo a senha.

4. Conferir o schema efetivamente publicado antes de conceder acesso:

   ```sql
   SELECT tablename, tableowner
   FROM pg_tables WHERE schemaname = 'public'
   ORDER BY tablename;

   SELECT sequence_name FROM information_schema.sequences
   WHERE sequence_schema = 'public';
   ```

5. As capturas do operador mostram 15 tabelas em `neondb`, incluindo as tabelas
   de moderação, todas com proprietário `neondb_owner`. Os GRANTs preparados
   estão em [170-acesso-api.sql](https://github.com/unb-mds/2026-02-UnDb/blob/develop/scripts/sql/170-acesso-api.sql). Eles concedem
   `CONNECT`, `USAGE`, leitura no catálogo e operações de escrita mapeadas nos
   repositories de contas, avaliações e moderação em `develop`. O operador já
   executou os GRANTs na sessão; a validação da API pública com o novo papel
   permanece pendente. Não concede escrita
   no catálogo, acesso ao histórico de importação ou `alembic_version`. Os
   modelos observados usam UUIDs; não há concessão indiscriminada a sequências.
6. Conferir permissões herdadas de outros papéis e de `PUBLIC`, propriedade
   de objetos e `CREATE` efetivo no schema/banco. Os atributos `NO...` sozinhos
   não comprovam acesso mínimo. Não revogar privilégios globais de `PUBLIC`
   sem conferir o impacto sobre os outros consumidores.
7. Atualizar somente `DATABASE_URL` no Render para o novo papel, mantendo
   `MIGRATION_DATABASE_URL` administrativa. Senhas com caracteres especiais
   precisam de percent-encoding na URI. Não trocar a conexão do importador
   pela conexão da API: ele precisa escrever no catálogo.
8. Fazer deploy e testar consulta real do catálogo, cadastro, confirmação,
   login, logout, avaliação e os fluxos de moderação publicados. `/health`
   sozinho não comprova acesso ao banco. Conferir que migrações continuam
   funcionando e não aparecem erros de permissão nos fluxos.
9. Registrar na #170 a revisão publicada, os privilégios efetivos, a matriz de
   acesso e as verificações, sem credenciais nem dados pessoais. O ensaio de
   restauração permanece uma verificação separada.

Não conceder automaticamente escrita em toda tabela futura. Cada nova migration
deve considerar os GRANTs necessários para os papéis de execução. Isso evita
conceder acesso involuntário a tabelas administrativas ou futuras.

## Consultas de conferência

```sql
SELECT rolname, rolcanlogin, rolsuper, rolcreatedb, rolcreaterole,
       rolreplication, rolbypassrls
FROM pg_roles WHERE rolname = 'undb_api';

SELECT granted.rolname AS papel_concedido
FROM pg_auth_members m
JOIN pg_roles granted ON granted.oid = m.roleid
JOIN pg_roles member_role ON member_role.oid = m.member
WHERE member_role.rolname = 'undb_api';

SELECT has_database_privilege('undb_api', current_database(), 'CONNECT') AS conectar,
       has_database_privilege('undb_api', current_database(), 'CREATE') AS criar_schema,
       has_schema_privilege('undb_api', 'public', 'USAGE') AS usar_schema,
       has_schema_privilege('undb_api', 'public', 'CREATE') AS criar_objeto;

SELECT tablename,
       has_table_privilege('undb_api', format('%I.%I', schemaname, tablename), 'SELECT') AS ler,
       has_table_privilege('undb_api', format('%I.%I', schemaname, tablename), 'INSERT') AS inserir,
       has_table_privilege('undb_api', format('%I.%I', schemaname, tablename), 'UPDATE') AS atualizar,
       has_table_privilege('undb_api', format('%I.%I', schemaname, tablename), 'DELETE') AS excluir,
       has_table_privilege('undb_api', format('%I.%I', schemaname, tablename), 'TRUNCATE') AS truncar
FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
```

Referências: [papéis Neon](https://neon.com/docs/manage/roles),
[privilégios PostgreSQL](https://www.postgresql.org/docs/current/ddl-priv.html).

Ver [verificação local da #170](estudos/verificacao-acesso-postgresql-issue-170.md)
para o escopo dos testes e os passos ainda pendentes no ambiente hospedado.
