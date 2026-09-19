# Verificação do Docker Compose — Issue #34

**Data:** 19/09/2026 (America/Sao_Paulo).
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

## Evidência informada na entrega

A descrição original da PR #105 registra que a autora executou a composição,
confirmou as migrações Alembic e verificou que os dados permaneceram após encerrar e
subir novamente os containers sem remover o volume. Esse relato é preservado como
evidência da entrega, mas não foi reproduzido nesta revisão porque o host do revisor
não possui Docker CLI ou Docker Desktop.

## Verificações da revisão

- `eslint .`: aprovado.
- `next build`: aprovado, incluindo TypeScript e as rotas dinâmicas.
- Diff contra `develop`: limitado a este registro; instruções duplicadas no README e
  uma correção de consulta pertencente à PR #106 foram removidas do escopo.
- Suíte backend local: inconclusiva, pois o runtime disponível não contém FastAPI e
  SQLAlchemy. O check `Backend` do GitHub Actions passou após a correção da branch.

## Limites

Esta verificação não substitui o teste em clone limpo por pelo menos dois membros. A
validação completa do ambiente e esse aceite coletivo continuam na Issue #37.
