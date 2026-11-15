# Recuperação de senha — RF24

Solicitação humana aprovada em 15/11/2026 nesta conversa. Implementação sobre
`origin/develop` `4d5dabf`, com a moldura de conta atual da PR #248, sem mudanças
nos critérios de avaliação, confirmação institucional ou tecnologias.

O link “Esqueci minha senha” do login abre `/esqueci-senha`. A API recebe
`POST /api/auth/recuperar-senha` com `email` institucional e sempre retorna a
resposta genérica 202 para endereços válidos, inclusive se o envio falhar. Falhas
de entrega são registradas sem destinatário/token. O usuário não descobre se
outra pessoa possui conta. O envio usa a interface existente (console/Resend),
sem ativar envio externo nesta tarefa.

O e-mail aponta para `/redefinir-senha?token=...`. O formulário exige confirmação
local da senha; o backend valida o token e 8–128 caracteres, aplica Argon2id e
encerra as sessões anteriores. Não há login automático nem confirmação implícita
de e-mail. Tokens aleatórios têm uma hora, uso único e somente SHA-256 persistido
em tabela separada da confirmação. A troca invalida os outros links da conta.
O bloqueio da linha do usuário serializa redefinições e login no PostgreSQL,
evitando sessão nova com senha antiga depois da troca. Exceções desfazem a transação.
A página usa noindex/no-referrer, remove o token da URL após sucesso e não usa
Web Storage. Em falha de rede, preserva os campos para nova tentativa.

## Preparação e reprodução

Aplicar `alembic upgrade head` no ambiente de destino antes de servir a nova API.
A migration `20261115_01` sucede `20261114_01`. Com `EMAIL_BACKEND=console`, o link
fica nos logs locais da API; `FRONTEND_URL` deve apontar para o frontend utilizado.
Produção exige o provedor e remetente já previstos pelo projeto; não foram configurados.

Com dependências existentes instaladas:

- Backend: `python -m unittest tests.test_auth tests.test_recuperacao_senha -v`.
- Frontend após build: `BROWSER_PATH=... node tests/recuperacao-senha-browser.mjs`.
- `PREVIEW_DIR` opcional salva capturas locais sem credenciais reais.

Verificados: 35 testes de autenticação/recuperação; a suíte completa atual tem 284
casos, dois pulados. O navegador com HTTP controlado passou 18 combinações de
320/768/1280 px e preferência clara/escura (a aplicação mantém o tema escuro),
com logo/moldura atuais, teclado, rótulos, carregamento, erro/retry, confirmação
divergente, sucesso, link ausente e rejeição de token. As capturas móveis e desktop
foram inspecionadas. Não houve envio externo.

A migration teve upgrade/downgrade/upgrade e comparação com metadata em SQLite
isolado, além da geração de SQL PostgreSQL. Não houve execução contra PostgreSQL,
ensaio concorrente real, aplicação em banco operacional ou deploy. Limites de
abuso de requisições continuam como evolução de segurança do projeto; esta entrega
não estabelece uma política global de rate limit.
