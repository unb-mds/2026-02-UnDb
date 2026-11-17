# Transparência da R2 — Issue #269

Fonte de produto: [RF26](requisitos.md#rf26-transparencia-termos-e-ciencia-no-cadastro-269).
Autorização: consolidação pelo PO em 16/11/2026 e pedido de execução integral com
“sem fins lucrativos” nesta sessão em 17/11/2026. Base inspecionada: develop `62faab9`.
Este registro substitui as pendências de R2 absorvidas de #261/#268; os estudos antigos
preservam seu contexto histórico. Não é auditoria de produção nem parecer jurídico.

## Inventário factual simplificado

Reaproveita [T01–T18](estudos/inventario-tecnico-pr277.md), a PR #277 e as correções de
[erros/logs/origens da #279](seguranca/revisao-sessoes-abuso-logs-issue-266.md).
PostgreSQL é o armazenamento da aplicação (Neon na configuração documentada);
acesso direto depende das permissões operacionais, não da atribuição de uma issue.

| Origem / dados | Finalidade | Acesso / armazenamento ou fornecedor | Descarte vigente / limite |
|---|---|---|---|
| T01; nome, e-mail, UUID, hash de senha, confirmação, papéis e criação fornecidos pela conta | Cadastro e autorização | `usuarios`; própria conta e funções autorizadas; PostgreSQL/Neon | Sem prazo geral de descarte implementado; sem exclusão integral automática |
| RF26; versão dos Termos e instante UTC gerado pelo servidor | Registrar ciência no novo cadastro | `usuarios.termos_versao/termos_ciencia_em`, sem exposição na consulta pública | Par nulo nas contas antigas, sem backfill; mesma lacuna de guarda da conta |
| T02–T04; links/tokens, hashes e validades gerados pelo sistema | Confirmação, sessão e recuperação | Tabelas de tokens/sessão; cookie HttpOnly; destinatário e link no Resend | Confirmação 24 h, sessão 7 dias de inatividade, recuperação 1 h/uso único; validade não é limpeza geral. Logout remove sessão; redefinição invalida sessões/links |
| T05–T08; nomes/identificadores docentes, unidades, disciplinas, turmas, vínculos e execução vindos do SIGAA público/revisão | Catálogo, atualização e reconciliação | Catálogo público; revisão por reconciliador; tabelas próprias em PostgreSQL; importador local | Sem prazo geral; preservação de histórico e atualização não são exclusão de todos os dados |
| T09; conta, cinco critérios, professor/disciplina e datas informados na avaliação | Unicidade, substituição e agregados | `avaliacoes`, vínculo privado; agregado público a partir de três, sem notas individuais | Novo envio substitui; destino ao excluir conta ainda depende de decisão específica na #263 |
| T10; texto opcional, versões, estados e datas enviados pelo autor | Publicação/revisão/retirada | `comentario_versoes`; público só publicado; autor e moderação autorizados | Limpeza de texto RETIRADO/REMOVIDO após 7 dias via rotina; pendente/suspenso preservado; execução hospedada não verificada |
| T11–T13; denúncia/motivo, conta quando existente, decisões/atores e agradecimentos | Análise, impedimentos, revisão e comunicação | Tabelas de moderação, acesso por papel/objeto; sem denunciantes públicos | Denúncia encerrada descartada pelo fluxo; decisões com prazo próprio de 7 dias; agradecimentos têm ciclo próprio |
| T14; texto integral elegível e resultado de classificação | Apoio à triagem, quando habilitada | OpenAI Moderations API; sem envio pelo canal de contato | Contrato, regiões, retenção externa e suboperadores não confirmados; filtros não garantem anonimização |
| T15; categoria, alvo, descrição/evidência textual, protocolo, hash de chave, complementos e respostas | Contato e atendimento manual sem login estudantil | `solicitacoes_titulares/eventos_solicitacoes`; portador da chave consulta respostas/complementos; triagem/providências internas; allowlists de atendimento | Sem descarte geral implementado. Recebimento depende de configuração/retenção aprovada; não ativado por esta entrega; #263 acompanha |
| T16–T17; identificador HMAC temporário do cliente, eventos e metadados de conexão | Proteção contra abuso e operação | HMAC em memória por processo, janela 60 s; logs de aplicação/servidor/provedores separados | Janela do HMAC não equivale à guarda de IP/logs. #279 sanitiza aplicação; borda/proxy e prazos não verificados |
| T18; possíveis cópias dos dados anteriores | Recuperação | Backups/exportações e permissões reais ainda a conferir na #267 | Não há período/cobertura/restauração comprovados nesta revisão; não prometer apagamento instantâneo ou recuperação garantida |
| #278, quando entregue; conta, voto e versão do comentário | Unicidade, troca/retirada e contagem | Ainda não existe na base `62faab9`; contrato exige contagem pública e estado próprio | Coordenar com #263/#265, sem herdar votos entre versões ou decidir retenção por suposição |

## Serviços conhecidos e o que não foi confirmado

Fonte: [hospedagem](hospedagem.md), [continuidade](continuidade-operacional.md),
serviços de e-mail/triagem e configuração no código. Serviços documentados:
Vercel (frontend), Render (API), Neon (PostgreSQL), Resend (transacional),
OpenAI (moderação externa quando habilitada), Registro.br (domínio/DNS).
Nenhum painel, banco real ou credencial foi acessado nesta entrega.

Não se presume contrato, região final de processamento, uso secundário, prazo do
provedor, suboperador, garantia de disponibilidade ou cobertura de backup. A região
mostrada em um painel no passado não comprova todos os locais de tratamento.
A Política expõe esses limites; não afirma anonimato absoluto nem conformidade integral.
Não são atribuídas bases legais genéricas ou consentimento em nome de terceiros.
Revisão jurídica formal não é pré-condição desta R2 conforme autorização da #269.

## Contato, pedidos e moderação

O fluxo existente é `/contato` → protocolo/chave → consulta/complementos → resposta
manual autorizada; triagem/providências internas ficam separadas. Ver [canal](canal-titulares.md).
A página informa indisponibilidade do recebimento; esta entrega não ativa flags nem
promete SLA. Nicolas acompanha a operação; permissões documentadas continuam vigentes.

A #263 acompanha política operacional, pedidos e efeitos da exclusão; a #267,
roteiro/recuperação. Esses insumos não exigem fechamento integral para redigir a Política.
A decisão ausente sobre avaliações na exclusão não é resolvida aqui e não bloqueia
contato/textos. Excluir conta, retirar comentário e desativar acesso são operações distintas.

Crítica legítima negativa é permitida; discordância docente e impopularidade não
removem conteúdo. Triagem externa não rejeita automaticamente; sinais/falhas aguardam
revisão humana. 50 contas distintas continuam como gatilho de suspensão, não mínimo
para analisar um relato fundamentado. Votos não alteram notas ou moderação.

## Publicação e ciência

Páginas `/privacidade` e `/termos-de-uso`, versão `2026-11-17`, com data legível,
links no rodapé, cadastro e Sobre. Home/Sobre/rodapé/Termos/Política explicitam natureza
acadêmica estudantil independente e sem fins lucrativos. Isso não declara pessoa jurídica
ou vínculo oficial com a UnB.

O cadastro exige `ciencia_termos: true` estrito e versão vigente. Data é gerada pelo
servidor, persistida atomicamente com a conta e não aceita do cliente. Duas colunas
nulas preservam contas existentes sem ciência fictícia ou bloqueio de login. CHECK
exige o par completo ou ausente; não há índice novo nem retenção nova.

A migração Alembic é aditiva e reversível. Downgrade remove exclusivamente o registro
de ciência; não executar downgrade em produção sem avaliar perda dessa evidência.
Deploy exige coordenar backend/migração e frontend: clientes antigos sem os campos
novos passam a receber 422 no cadastro; login existente permanece compatível.
Commit, push e PR foram autorizados por Nicolas na continuação desta sessão, com um
único commit preparado. Deploy, ativação do contato e aceite final permanecem fora desta etapa.

## Fontes públicas de referência

- [LGPD atualizada na Câmara dos Deputados](https://www2.camara.leg.br/legin/fed/lei/2018/lei-13709-14-agosto-2018-787077-normaatualizada-pl.html): referência para informações e pedidos de direitos; não fundamenta promessa de eliminação incondicional.
- [Histórico do inventário](estudos/inventario-tecnico-pr277.md).
- [Regras de produto](requisitos.md) e [contratos derivados](https://github.com/unb-mds/2026-02-UnDb/blob/develop/specs.md).

## Evidências da entrega local

[Verificações, capturas, rastreabilidade e publicação pendente](estudos/transparencia-issue-269.md).
