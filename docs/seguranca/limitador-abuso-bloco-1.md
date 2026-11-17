# Limitador de abuso — #266, Bloco 1

Estado: **implementado** como núcleo reutilizável, sem endpoints de produto
vinculados. Fonte: decisões A e regras gerais do pedido `EXECUTAR: BLOCO 1`.
Vincular autenticação é o Bloco 2; demais fluxos e substituição do contador em
memória do canal são o Bloco 3. Não foi iniciado nenhum deles.

## Histórico e destino

A PR #279 já estava integrada quando esta execução começou. O PO orientou abrir
outra PR em rascunho usando a mesma branch remota `fix/266-sessoes-abuso-logs` e
uma worktree baseada em `f8efeff`. A worktree anterior e os quatro commits locais
foram preservados em `archive/266-retomada-local`; não houve merge ou rebase.
Registros deste bloco ficam no repositório e na nova PR, sem comentários em issues.

## Contrato e camadas

- Domínio: `domain/email.py` fornece `strip().casefold()`, igual à regra já usada
  pelos schemas. Não remove aliases/pontos nem consulta existência de conta.
  `domain/limite_abuso.py` contém políticas e resultado estruturado.
- Núcleo: `core/limite_abuso.py` deriva HMAC-SHA256 com segredo exclusivo de
  ambiente. As entradas possíveis são e-mail normalizado, UUID de conta ou hash
  de token. Operação, tipo e marcador global possuem separação de domínio. O
  valor da identidade não aparece no `repr`; não existe tipo/chave por IP.
- Repositório: `INSERT ... ON CONFLICT DO UPDATE ... RETURNING` incrementa uma
  linha, reseta a janela expirada e preserva a espera ainda ativa atomicamente.
- Serviço: transação exclusiva do limitador, primeiro global e depois identidade.
  Uma negação confirma os contadores, independentemente do rollback do chamador.
  Erro durante a transação reverte ambos os incrementos. Falhas não registram
  exceção, SQL, parâmetros, chave, e-mail, token, senha ou corpo.
- Dependência FastAPI: `exigir_limite(operacao, resolver_identidade, fallback_local)`.
  Identidade deve ser resolvida pelo futuro fluxo, nunca por um header de bypass.
  Sem resolver, aplica somente orçamento global. Nenhum router existente a utiliza.
- Handlers registrados: 429 e 503 genéricos, com `Retry-After`, `no-store` e
  `no-referrer`. A resposta não informa qual orçamento foi excedido ou se conta existe.

O retorno é `ResultadoLimite(permitido, retry_after, motivo, excedido,
indisponivel, acao_falha)`. Os motivos são enums, não mensagens do banco.
O serviço não implementa login, envio de e-mail, autorização, bloqueio permanente,
remoção de conteúdo ou política de moderação.

## Modelo e migração

`20261117_01` cria `contadores_abuso` como **UNLOGGED** em PostgreSQL, com:

- PK `(operacao, chave)`; chave HMAC com 64 caracteres, sem FK para identidade.
- Quantidade positiva, início e expiração UTC e próxima tentativa opcional.
- Constraint de expiração posterior ao início e índice de expiração usado na purga.

Os atributos dependem da chave composta; não há cópia do e-mail, token ou conta.
O mapping ORM registra a natureza descartável em `info`; a propriedade UNLOGGED
é estabelecida pela migration, não pelo `create_all` dos testes SQLite legados.
Não há fallback SQLite para a execução do limitador.
Downgrade remove índice/tabela e preserva as tabelas anteriores. Tokens, sessões,
avaliações e suas retenções não foram alterados.

## Políticas e configuração

Todos os números abaixo são **PROVISÓRIOS, pendentes de validação (item 4)**.
Não representam medição de capacidade ou cota comprovada do provedor.

| Variável | Padrão | Finalidade |
|---|---|---|
| `ABUSO_HMAC_SECRET` | vazio | Segredo exclusivo; ausência causa falha fechada, sem usar SECRET_KEY como fallback |
| `ABUSO_POLITICAS` | `{}` | Registro explícito de operações; operação não registrada gera 503 na dependência |
| `ABUSO_QUANTIDADE_PADRAO` | 100 | Perfil genérico, inativo sem registro; teto de referência para futura configuração de autenticação |
| `ABUSO_JANELA_SEGUNDOS_PADRAO` | 60 | Janela fixa do perfil genérico, ancorada na primeira tentativa |
| `ABUSO_QUANTIDADE_GLOBAL_PADRAO` | 100 | Capacidade global do perfil, inclusive clientes que trocam identificadores |
| `ABUSO_JANELA_GLOBAL_SEGUNDOS_PADRAO` | 60 | Janela global independente da individual |
| `ABUSO_STATEMENT_TIMEOUT_MS` | 250 | Limite de cada comando SQL do pool dedicado |
| `ABUSO_LOCK_TIMEOUT_MS` | 100 | Limite de espera por lock |
| `ABUSO_CONNECT_TIMEOUT_SEGUNDOS` | 2 | Abertura da conexão psycopg2 |
| `ABUSO_POOL_TIMEOUT_SEGUNDOS` | 0,25 | Espera por conexão livre |
| `ABUSO_POOL_TAMANHO` | 2 | Conexões por processo, sem overflow |
| `ABUSO_RETRY_FALHA_SEGUNDOS` | 5 | Retry-After de indisponibilidade |
| `ABUSO_LIMPEZA_INTERVALO_SEGUNDOS` | 60 | Intervalo do comando em modo contínuo |
| `ABUSO_LIMPEZA_LOTE` | 1000 | Máximo de registros por transação de limpeza |

O perfil genérico de 100/60 s limita o número de operações potencialmente caras
e permite testar o núcleo sem inventar uma cota de e-mail. O custo efetivo de
Argon2 e a capacidade disponível precisam orientar os perfis do Bloco 2; não se
deve ativar envio baseado nesse perfil genérico. A quota diária reservada ao
projeto não está comprovada no repositório e precisa ser configurada antes disso.

A referência de 100 falhas consecutivas vem de
[NIST SP 800-63B, seção 3.2.2](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/#rate-limiting-throttling).
Ela não transforma uma janela de tentativas em controle de falhas consecutivas,
nem comprova conformidade. Diferenciar tentativa de falha e reiniciar após sucesso
faz parte do futuro fluxo de autenticação. O gancho `reiniciar_identidade` mantém
o orçamento global. O pedido do PO preserva atraso temporário sem bloqueio permanente.

Uma operação registrada em `ABUSO_POLITICAS` pode sobrescrever `quantidade`,
`janela_segundos`, `quantidade_global`, `janela_global_segundos`, `modo`, `falha`,
`atraso_apos`, `atraso_inicial_segundos` e `atraso_maximo_segundos`.
O padrão é `enforce`, falha `fechar` e atraso desabilitado (zeros). Nenhum
valor de política é aceito de requisição HTTP. Valores inválidos são recusados.

`observe` confirma contagens e emite eventos mínimos do que excederia o orçamento,
mas retorna permitido; não instala atraso na próxima tentativa. Não converte
indisponibilidade em liberação: o comportamento de falha continua independente.

O atraso é exponencial, limitado pelo máximo configurado e pela expiração da janela.
Tentativas durante a espera não aumentam o contador individual nem prolongam essa
espera. O orçamento global continua sendo consumido. Não há `sleep` na requisição.
Trocar tokens/identificadores não evita o orçamento global. O custo dessa linha
global e o efeito de rajadas nas bordas da janela são pendentes de validação.

Rotacionar ABUSO_HMAC_SECRET ou mudar a normalização/separação de chaves pode
conceder novo orçamento; deve ser coordenado entre instâncias. Chaves antigas
expiram pela janela e são removidas pelo mesmo comando de limpeza.

## Falha e limpeza

`fechar` retorna indisponível/negado; `seguir` retorna indisponível/permitido com
evento mínimo. `local` exige fallback explicitamente fornecido pelo futuro fluxo;
sem ele, a dependência nega com 503. O contador local para denúncias é planejado
para o Bloco 3 e não foi implementado aqui. Autenticação/autorização nunca são
desativadas por esses modos.

O pool usa a mesma DATABASE_URL com sessão separada e parâmetros SQL ocultos.
Os timeouts são por conexão/lock/comando, não promessa de prazo total da requisição.
Cada processo pode usar até ABUSO_POOL_TAMANHO conexões adicionais; o orçamento
de conexões do ambiente é pendente de validação operacional.

```text
cd backend
python -m app.commands.limpar_contadores_abuso
python -m app.commands.limpar_contadores_abuso --continuo
```

O comando remove expirados em lotes com `FOR UPDATE SKIP LOCKED` e transação curta;
reexecução é idempotente. Só imprime quantidade removida. Agendamento/execução no
ambiente hospedado são **planejados**, não realizados. Nenhuma thread ou tarefa
de purga é iniciada ao importar a API. A janela reinicia mesmo antes da limpeza.

Compartilhamento entre processos está implementado no mesmo PostgreSQL escritor.
Segundo a [documentação PostgreSQL](https://www.postgresql.org/docs/16/sql-createtable.html#SQL-CREATETABLE-UNLOGGED),
UNLOGGED pode ser truncada após crash/encerramento não limpo e não replica seu
conteúdo para standby. Não se promete continuidade do orçamento após esses eventos.
Reinícios dos processos da API não apagam o estado no banco. Não há controle de
CDN/proxy implementado, nem confiança em cabeçalhos encaminhados.

## Verificação reproduzível

Executar com Python 3.12 e dependências existentes. Para testes reais, aplicar as
migrações e definir `ABUSO_POSTGRES_TEST_URL` exclusivamente para banco descartável
`undb_266_test` ou `ci` em loopback, com psycopg2. Os testes recusam outro destino.
Sem essa variável, os testes PostgreSQL são pulados explicitamente; isso não é
evidência de execução. CI aplica a migration antes da suíte e fornece a URL local.

```text
python -m ruff check .
python -m ruff format --check .
python -m compileall -q app alembic
python -m unittest tests.test_limite_abuso tests.test_limite_abuso_postgres -q
python -m unittest discover -s tests -q
alembic upgrade head
alembic check
alembic downgrade 20261115_02
alembic upgrade head
```

Tipagem do frontend não se aplica a este bloco, que não altera TypeScript.
Não foi introduzido verificador de tipos Python novo.
Estado das verificações locais e CI será registrado nesta entrega; produção,
quota real, calibração e operação do job são **pendentes de validação**.
