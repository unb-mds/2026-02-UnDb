# Autenticação e proteção contra abuso — Bloco 2

Estado: implementado. Fonte: decisões A e pedido EXECUTAR: BLOCO 2 do PO.
Continuidade na PR #280, pois a #279 já foi integrada. Blocos 3–8: planejados.

## Comportamento implementado

Cadastro, login, confirmação, reenvio e recuperação/redefinição usam o núcleo
PostgreSQL do Bloco 1 antes dos efeitos de autenticação. Chaves de e-mail usam
normalização do domínio e HMAC; tokens usam hash e capacidade global por operação
contra sua rotação. Não há chave por IP nem bypass por papel.

Restrições retornam 429; falha do limitador retorna 503. Ambos incluem Retry-After,
no-store e no-referrer. Sessões válidas e logout continuam sem limitador.
Cadastro, recuperação e reenvio retornam 202 neutro para contas existentes ou
inexistentes quando permitidos; falha de envio também mantém resposta neutra.
Restrição ou falha do limitador não envia e-mail nem altera conta/sessão/token.
Falha na configuração do transporte retorna 503 genérico com Retry-After.

`POST /api/auth/reenviar-confirmacao` aceita e-mail e retorno interno opcional,
mantém links anteriores válidos e não altera senha/conta existente. Login verifica
hash fictício também quando a conta não existe; isso reduz o atalho de tempo,
sem prometer tempo constante. Sucesso reinicia apenas o contador individual antes
de criar sessão. Redefinição também reinicia esse contador; falha nesse passo
desfaz alterações de senha, tokens e sessões.

## Parâmetros e justificativa

Todos são **PROVISÓRIOS, pendentes de validação (item 4)**. Os nomes completos e
padrões estão em `backend/.env.example` e `backend/app/core/config.py`.

| Operação | Identidade / janela | Capacidade global |
| --- | --- | --- |
| Login | 100 tentativas / 900 s; atraso após 3, inicial 1 s, máximo 60 s | 30 / 60 s |
| Cadastro, reenvio, recuperação | 3 / 900 s por operação e destino | 30 / 60 s por operação |
| Intervalo compartilhado de e-mail | 1 / 60 s por destino entre os três fluxos | 30 / 60 s |
| Orçamento diário compartilhado | reserva antes de consultar a conta | 80 / dia UTC |
| Confirmação | 10 / 900 s por token | 30 / 60 s |
| Redefinição | 10 / 900 s por token | 10 / 60 s |

O teto de login usa 100 como referência superior aprovada; o atraso progressivo
reduz repetição antes do hash de senha custoso. O orçamento expira ou reinicia no
sucesso; não há bloqueio permanente nem alegação de conformidade NIST para um
contador estrito de falhas consecutivas. Os tetos globais provisórios limitam
trabalho de hash; capacidade e falsos positivos precisam de medição operacional.

Referência externa consultada: [cotas oficiais Resend](https://resend.com/docs/knowledge-base/account-quotas-and-limits).
O plano Free informa 100/dia, reset UTC e cota compartilhada incluindo recebimento.
O padrão 80 deixa margem de 20 nessa referência; **não comprova o plano da equipe**.
Responsável operacional deve configurar `AUTH_EMAIL_COTA_DIARIA_PROVEDOR` e
`AUTH_EMAIL_ORCAMENTO_DIARIO` conforme a cota efetivamente reservada. Configuração
com orçamento maior ou igual à cota suspende o fluxo. Contas inexistentes também
reservam orçamento: preserva resposta neutra, mas permite esgotamento sem envio.
Outros consumidores e cotas mensais do provedor não são coordenados por este módulo.

`AUTH_ABUSO_MODO=enforce` é padrão; cada perfil admite override em ABUSO_POLITICAS.
`observe` registra o que bloquearia e permite continuar, podendo exceder orçamento.
Não usar observe como garantia de proteção da cota. Falha sempre suspende autenticação.
`ABUSO_HMAC_SECRET` privado é obrigatório; ausência causa 503 sem fallback em memória.
UNLOGGED compartilha contadores entre instâncias no mesmo escritor, mas crash,
failover ou rotação do segredo podem reiniciá-los. CDN/proxy, disponibilidade e
proteção da cota externa permanecem pendentes de validação operacional.

Validades anteriores foram preservadas e tornadas configuráveis: confirmação 24 h,
sessão 7 dias, recuperação 60 minutos. Não há nova migração neste bloco.

## Logs e ensaios

O transporte console registra apenas evento constante, inclusive em DEBUG. Não
imprime e-mail/link/token. O ensaio de acesso usa transporte sintético em arquivo
temporário privado, separado de stdout/logs, removido ao final. Isso substitui a
leitura antiga de links dos logs; execução manual por logs de container precisa
ser adaptada para transporte sintético antes de ser utilizada.

Implementação principal: `auth_abuso_service.py`, `dependencia_auth_abuso.py`,
`routers/auth.py`, `auth_service.py`. Testes: `test_auth_abuso_http.py` e
`test_auth_abuso_postgres.py`; regressões anteriores preservadas.

## Evidências locais

- Windows, Python 3.12.16, PostgreSQL 16.16 descartável em loopback, papel API sem DDL.
- 61 testes específicos passaram, incluindo concorrência do núcleo, timeout real,
  janela UTC, orçamento compartilhado, observe, 100 falhas, atraso, reset e rollback.
- Suíte completa: 402 testes, sem falhas, 2 skips antigos de identidades/reconciliação
  que exigem banco dedicado `undb_207_test`.
- Integrações `python -m tests.integration_avaliacao` e
  `python -m tests.integration_acesso`: passaram com navegador Edge e PostgreSQL.
  Acesso inclui 54 combinações de tela/tema/largura. Nenhum e-mail real enviado.
- Alembic upgrade/check, downgrade do núcleo e até base, reaplicação, limpeza CLI
  e check final: passaram. Banco e papéis do ensaio removidos.
- Frontend `npm ci --ignore-scripts` e `npm run build`: passaram com lockfile
  preservado. Sem alteração de produto no frontend; tratamento visual é Bloco 4.

Resultados estruturados: `evidencias/issue-266/bloco-2/resultados.json`.
CI Linux do novo push: pendente de validação até registro na PR. Não há evidência
de produção nem validação jurídica. Issue #266 permanece com pendências dos demais
blocos e das validações humanas aprovadas; este documento cobre somente Bloco 2.
