# Verificação do Docker Compose — Issue #34

**Data:** 20/09/2026 (America/Sao_Paulo).
**Escopo:** execução conjunta de backend e PostgreSQL, migrações e persistência do
volume, conforme a Issue #34.

## Configuração inspecionada

A configuração funcional foi integrada anteriormente pela PR #93. A revisão da PR
#105, já alinhada à `develop`, confirmou no estado atual do repositório:

- serviço `db` com a imagem oficial `postgres:16` e volume nomeado
  `postgres_data` montado em `/var/lib/postgresql/data`;
- health check do PostgreSQL com `pg_isready`;
- serviço `backend` dependente do banco saudável;
- `DATABASE_URL` usando o hostname interno `db`, sem `localhost` entre containers;
- execução de `alembic upgrade head` antes do início do Uvicorn;
- variáveis de exemplo em `backend/.env.example` e procedimento de inicialização
  documentado no README.

## Verificações da revisão

- O job `Docker Compose` valida a configuração com `docker compose config --quiet`.
- O mesmo job constrói e inicia `backend` e `db` pela composição e exige resposta do
  endpoint `/health`.
- A inicialização do backend executa `alembic upgrade head`; em seguida, o job consulta
  `alembic_version` diretamente no PostgreSQL para confirmar conexão e migração.
- O job executa `docker compose down` sem remover volumes, reinicia o serviço `db` e
  exige que a revisão Alembic permaneça idêntica. Ao final, remove o volume descartável
  do CI mesmo se alguma etapa falhar.
- O check `Backend` continua cobrindo testes determinísticos, consistência dos modelos,
  ciclo de migrações e conteúdo da imagem do backend.

## Limites

O host desta revisão não possui Docker CLI ou Docker Desktop, portanto a execução do
novo job depende do GitHub Actions. Esta verificação automatizada cobre apenas backend,
PostgreSQL, migrações e persistência básica da Issue #34. O teste do ambiente completo
em clone limpo por pelo menos dois membros, incluindo o frontend e a ausência de passos
manuais adicionais, continua reservado à Issue #37.
