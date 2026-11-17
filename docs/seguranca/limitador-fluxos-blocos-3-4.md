# Proteção dos fluxos e mensagens temporárias — #266

Fonte: decisão A e EXECUTAR: BLOCO 3 e 4 do PO. Bloco 3: implementado.
Bloco 4: planejado até o registro de suas evidências. Sem execução em produção
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
