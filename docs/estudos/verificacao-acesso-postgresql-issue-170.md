# Verificação de acesso PostgreSQL — #170

Data: 10/11/2026. Base: `develop` em `976d93b`. Relacionada à
[#170](https://github.com/unb-mds/2026-02-UnDb/issues/170).

## Mudança e fonte

O critério ainda pendente exige segredos externos e acessos mínimos. O operador
confirmou que a API pública usa `neondb_owner`; suas consultas mostraram poderes
administrativos. O novo papel `undb_api` foi criado pelo operador via SQL e teve
senha definida privadamente. As capturas fornecidas mostraram a execução dos
GRANTs e ausência de poderes administrativos, de papéis herdados e de CREATE
efetivo no banco/schema. Não foram copiadas senhas ou conexões para o relatório.

O backend passa a usar `MIGRATION_DATABASE_URL` no Alembic, preservando
`DATABASE_URL` para sessões da API. Sem a nova variável, o comportamento anterior
permanece. Não há migration de schema ou mudança de dados nesta entrega.

## Verificações locais executadas

Ambiente isolado: Python 3.12, dependências declaradas do backend e PostgreSQL 16
descartável em Docker. Nenhuma conexão ao Neon foi usada nesses testes.

A suíte determinística completa passou com **186 testes**, incluindo a preparação
da #164 na mesma PR. Lint (`ruff check`),
formatação (`ruff format --check`) e `git diff --check` passaram. O comando
`alembic check` não detectou diferenças entre migrations e modelos no PostgreSQL.

- Testes de regressão executam o Alembic de verdade: conexão separada migra
  somente o banco administrativo; ausência da variável mantém o destino antigo;
  configuração inválida falha sem migrar o banco da API. A URL do teste contém
  percent-encoding para verificar a interpolação da configuração.
- Migrações completas até `head` executadas por `neondb_owner`, enquanto
  `DATABASE_URL` apontava para `undb_api`. A senha administrativa de teste
  contém `%`, com percent-encoding na URL. Os testes usam credenciais fictícias.
- Script de GRANTs aplicado ao banco de teste. Com `undb_api`, CREATE TABLE,
  UPDATE em professores, leitura de `alembic_version` e leitura de
  `importacao_execucoes` foram recusados com SQLSTATE `42501`.
- Cadastro, confirmação de e-mail com remetente simulado, login, renovação e
  logout executados pelos services reais com sessões `undb_api`. Fixtures
  removidas administrativamente. Não houve envio de e-mail externo neste teste.
- Integração HTTP existente `tests.integration_moderacao` executada com o servidor
  usando `DATABASE_URL` limitada e fixtures/limpeza administrativas. Passou por
  avaliações, comentários, limiar 49/50, concorrência, privacidade, ações de
  moderação, retenção e agradecimentos. Não foi um teste de navegador/frontend.

## Pendências para aceite no ambiente público

1. Integrar e promover o código pelo fluxo autorizado, com revisão humana.
2. Configurar `MIGRATION_DATABASE_URL` administrativa e depois `DATABASE_URL`
   limitada no Render, sempre no mesmo banco/branch e com TLS. Não reutilizar a
   conexão limitada nos comandos do importador.
3. Conferir privilégios efetivos por tabela e validar o deploy: migrações,
   catálogo, cadastro, confirmação, sessão, avaliação e moderação. `/health`
   sozinho não valida o banco. Registrar revisão, data e resultados sem segredos.
4. O ensaio de backup/restauração do Neon continua sem evidência de execução.
   O roteiro já está em `docs/hospedagem.md`; os testes locais não o substituem.

A issue não está concluída somente por esta entrega de código. O segredo
administrativo continua no ambiente do serviço para o Alembic; esta mudança
separa os privilégios das conexões, não oferece isolamento do segredo em outro
serviço. Não foram modificadas a #207, suas regras ou identidades de docentes.
A pedido do PO, esta PR também prepara a auditoria e a rotina periódica da #164,
mantendo seus critérios operacionais e pendências separados.
