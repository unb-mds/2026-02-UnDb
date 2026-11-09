# Inicialização da API no Render

Correção complementar à revisão da PR #209, solicitada para desbloquear a
demonstração em `undb.app.br` (#169). Não altera contratos da UI #203.

O build Docker terminou, mas os dois deploys observados falharam com status 127:
o shell tentou executar toda a sequência `alembic ... && ... uvicorn ...` como
um único nome de programa. A inicialização agora fica em um módulo Python,
sem shell ou aspas no campo Docker Command.

## Configuração

Depois de integrar a correção na branch selecionada pelo serviço, configure:

```text
python -m app.commands.iniciar_servidor
```

Use esse valor em **Settings → Build & Deploy → Docker Command**. O módulo
já é incluído pelo `COPY app ./app` do Dockerfile existente. Root Directory:
`backend`; Dockerfile Path: `./Dockerfile`; Docker Build Context: `.`.
Selecione plano Free e região Virginia; deixe Pre-Deploy Command vazio.

Configure `DATABASE_URL` com a conexão direta do Neon, prefixo
`postgresql+psycopg2://` e TLS (`sslmode=require`), `SECRET_KEY` gerada no painel,
`DEBUG=False`, `CORS_ORIGINS=https://undb.app.br` e
`FRONTEND_URL=https://undb.app.br`. Não envie credenciais ao Git.
`EMAIL_BACKEND=console` permite testar a infraestrutura, mas não envia e-mails;
o cadastro só poderá ser validado com Resend e domínio verificado configurados.

O comando valida `PORT` (padrão 10000), aplica `alembic upgrade head` e inicia
Uvicorn em `0.0.0.0` na porta configurada pelo Render. Uma falha nas migrações
impede o servidor de iniciar. O processo é substituído por Uvicorn para receber
sinais de encerramento diretamente. O fluxo local de Docker Compose é preservado.
`pool_pre_ping=True` detecta conexões encerradas antes de reutilizá-las; não
recupera transações interrompidas.

## Verificação

Os testes `tests.test_iniciar_servidor` verificam a ordem migração/servidor,
o bloqueio do servidor quando a migração falha e a rejeição de porta inválida
antes de qualquer migração. Eles não substituem o teste no Render com Neon.

Após o deploy, confira os logs de migração, o retorno de `/health` e uma busca
real para verificar acesso ao banco. `/health` verifica apenas o processo.
Não execute downgrade automaticamente para reverter um deploy; migrações e
código precisam ser avaliados separadamente. Antes de migrar uma base com dados,
faça backup em armazenamento privado do time.

A PR tem destino `develop`, enquanto o serviço observado usa `main`. O comando
novo só estará disponível após a correção chegar à branch publicada. Não troque
a branch do ambiente ou considere a PR integrada antes de seguir o fluxo humano
de revisão e release.
