# Proteção dos fluxos e mensagens temporárias — #266

Fonte: decisão A e EXECUTAR: BLOCO 3 e 4 do PO. Bloco 3: implementado.
Bloco 4: implementado, com evidências locais abaixo. Sem execução em produção
ou validação jurídica. A continuidade utiliza a PR #280, após integração da #279.

## Matriz implementada no backend

| Operação | Identificação | Ao exceder | Na falha |
| --- | --- | --- | --- |
| Publicar/editar avaliação e comentário associado | ID interno, inclusive moderador como autor | 429 antes do serviço | Seguir com alerta |
| Denunciar comentário | ID interno ou apenas global para anônimo | 429 antes do serviço | Teto global local por processo |
| Criar, consultar, complementar solicitação de titular | ID interno quando autenticado, global para anônimo | 429 | 503 |
| Fila, detalhe e histórico da moderação | Papel moderador + ID interno | 429 | 503 |
| Decidir moderação, exceto remoção urgente | Papel moderador + ID interno | 429 | 503 |
| Apoio de triagem | Papel moderador + ID interno | 429 | 503; controles do provedor já existentes preservados |
| Fila, prévia, histórico e decisão de identidade docente | Papel reconciliador + ID interno | 429 | 503 |

Todas as operações limitadas têm capacidade global. Na moderação, operação inclui
papel e o orçamento global é compartilhado entre contas desse papel. O modelo
existente não possui papel administrador: nenhum papel ou endpoint foi criado.
Remoção urgente, retirada do próprio comentário e atendimento pela equipe mantêm
autenticação/autorização e evento mínimo de uso sem limitador. O HTTP registra
rota/status sem corpo nem identificação. Sessão, logout, health check, leitura
pública e scripts fora do HTTP permanecem fora do limitador. Suspensão de conta,
revogação administrativa, exclusão de conta/avaliação e webhook não existem como
fluxos HTTP neste escopo; quando implementados devem seguir a lista aprovada.

O contador antigo em memória do canal foi removido. Não há IP, cabeçalho encaminhado,
texto, e-mail ou token nas chaves desses fluxos. O canal permanece DESATIVADO por
padrão, com as condições anteriores de ativação preservadas. Orçamentos são
consumidos antes de validação de existência do alvo: tentativas inválidas contam.

## Valores provisórios e limitações

**PROVISÓRIOS, pendentes de validação (item 4).** Variáveis em `core/config.py` e
`backend/.env.example`; ajustes individuais de janela/global/modo em ABUSO_POLITICAS.
Janela padrão 60 s, global padrão 300 por operação; por conta: avaliação 10,
denúncia 5, titular criar/complementar 3, consultar 10. Moderador e reconciliador:
120 por operação/conta. Anônimos compartilham somente o global, sem atribuição
artificial a IP/dispositivo. Isso aumenta falsos positivos coletivos sob abuso.

Os padrões baixos de escrita reduzem repetição de upsert/versões e denúncias em
relação ao trabalho manual; os tetos maiores por papel permitem paginação e
revisão sem bypass de fila. Não são capacidade medida ou política definitiva.
Moderação assistida mantém limites próprios de chamadas/custo existentes.
Esses fluxos não enviam e-mail nem fazem hash de senha; sua calibração não deriva
da cota de e-mail. O global requer medição de carga antes de ajuste operacional.

Fallback de denúncia: 3 tentativas/60 s, global por processo, protegido por lock,
memória constante. Reiniciar o processo reinicia esse orçamento e múltiplas
instâncias multiplicam sua capacidade. É contenção degradada, não solução
distribuída. A política de falha aprovada prevalece sobre override de configuração.
Observe registra o que bloquearia; na falha prevalece a matriz acima.

Contadores normais continuam UNLOGGED no PostgreSQL, com limitações de crash e
failover descritas no Bloco 1. CDN/proxy e topologia continuam pendentes de
validação (item 8); nenhum ambiente de produção acessado.

## Verificação

Testes específicos: `python -m unittest tests.test_protecao_fluxos -q` no backend.
Testes PostgreSQL exigem ABUSO_POSTGRES_TEST_URL para banco local descartável
migrado `undb_266_test` ou CI `ci`; não usar banco de produto. Os testes verificam
matriz, efeitos bloqueados, identidade sem IP, orçamento compartilhado entre
instâncias, observe, limites por papel e exceção de remoção.

## Interface implementada — Bloco 4

O cliente HTTP interpreta Retry-After em segundos inteiros ou data HTTP e gera
mensagem segura para 429/503. Sem cabeçalho válido, orienta nova tentativa em
instantes sem inventar prazo. Corpo de erro não é mostrado nesses status, nem
armazenado nos detalhes de ApiError. CORS expõe somente Retry-After adicionalmente.
Não há repetição automática de escrita nem bloqueio permanente no navegador.

Cadastro, login, recuperação/redefinição, confirmação, avaliação, denúncia,
moderação, identidade e canal usam a mensagem comum. Campos permanecem no
formulário; moderação preserva a ação/motivo em 429/503 e mantém a atualização
para conflitos e impedimentos. Alertas existentes usam role=alert ou aria-live;
apoio e detalhes de moderação também anunciam espera. A confirmação pode ser
repetida pelo botão existente. Nenhum segredo é guardado para persistir formulários.

## Evidências locais e correções de integração

- Backend: 69 testes selecionados passaram; suíte completa com 406 testes, sem
  falhas, dois skips antigos de identidades/reconciliação para undb_207_test.
- Frontend: 91 testes passaram; lint, typecheck e build Next.js passaram, sem
  alteração de dependências/lockfile.
- Navegador Edge com HTTP controlado: avaliação/cadastro/confirmação, denúncia,
  recuperação/redefinição e moderação passaram. Cenários 429/503 verificam espera,
  preservação de campos e ausência de detalhes internos; moderação preserva motivo
  e ação. Recuperação mantém alertas acessíveis; suites existentes verificam teclado,
  rótulos, temas e larguras.
- HTTP real/PostgreSQL: moderação e avaliação passaram, incluindo concorrência,
  autorização e persistência. Nenhum e-mail real foi enviado.
- Upgrade/check, downgrade do núcleo, downgrade base e reaplicação passaram.
  Este bloco não altera esquema; núcleo e integração #277 permanecem preservados.
- Ruff check/format, compileall, MkDocs estrito e diff --check passaram.

O CI anterior do Bloco 2 falhou no percurso de login da moderação. O ensaio agora
gera segredo HMAC temporário sem imprimi-lo nos logs. Ensaios intensivos de
persistência usam override sintético de tentativas (100) para não testar limites
acidentalmente; testes específicos continuam exercitando os limites efetivos.
Isso não modifica configuração de produto nem autoriza mudança em produção.

Uma tentativa local de suíte após integração encontrou contadores expirados
deixados pelo ensaio anterior e falhou nos testes globais de limpeza. O roteiro
foi isolado executando a suíte antes das integrações: passou. A execução de Edge
exigiu permissões de subprocesso fora do sandbox local. Essas ocorrências não
são registradas como validação de produção.

Resultados sanitizados em `evidencias/issue-266/bloco-3/resultados.json` e
`evidencias/issue-266/bloco-4/resultados.json`. CI Linux do novo push: pendente de
validação até registro na PR. Blocos 5–8 continuam planejados; a #266 não é declarada
concluída. Calibração, topologia, operação e validações jurídicas permanecem pendentes.
