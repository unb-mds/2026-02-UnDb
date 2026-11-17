# Validações pendentes — #266

Estado deste registro: pendente de validação. Fonte: decisões A–F e execução dos
Blocos 1–8 pelo PO nesta conversa. A entrega técnica não equivale a aceite da issue.
O projeto será mantido após o release; os itens abaixo serão tratados nessa fase,
com acompanhamento de Nicolas e decisões pelos papéis indicados. Este documento
não declara nenhuma pendência concluída e não comprova configuração em produção.

## Matriz única de acompanhamento

Complemento #267 de 17/11/2026: [roteiro e insumos específicos](../operacao/incidentes-recuperacao.md)
e [ensaio ampliado](evidencias/issue-267/README.md). Nicolas relata backups manuais
no Docker; cobertura/histórico/acessos ainda sem evidência. Canal privado e
registro protegido de exclusões/revogações continuam pendentes. A extensão do
ensaio não resolve infraestrutura, guarda ou operação de backups da matriz.

| Item / tema | Estado atual | Falta validar / quem valida | Risco enquanto pendente | Critério de conclusão / referência |
| --- | --- | --- | --- | --- |
| 4 — números do limitador | Implementado, PROVISÓRIOS, pendentes de validação | PO e operação: cota reservada real de e-mail, custo de hash, carga, falsos positivos, limites por papel e observação | Negação coletiva para anônimos, esgotamento sem envio, carga excessiva ou bloqueio de uso legítimo | Medições sintéticas e operacionais sanitizadas, cota comprovada e configuração aprovada; `backend/app/core/config.py`, `services/auth_abuso_service.py`, `core/protecao_fluxos.py` |
| 8 — proxy/CDN/IP | Implementado sem IP nas chaves; encaminhamento não confiável | Nicolas: topologia, peer real, cabeçalhos aceitos/removidos, flag do servidor, CDN e limites de borda | IP interpretado incorretamente; contornos fora da aplicação | Diagrama e evidência sanitizada de origem/borda e peer, sem alterar produção por esta execução; `docker-compose.yml`, `core/registros_acesso.py`, [registros](acessos-bloco-6.md) |
| 9 — majors | Planejado, sem atualização de glob/minimatch | PO aprova impacto; manutenção verifica pais, Node, exports e padrões | Consumo de CPU/IO em desenvolvimento/CI; mudança de cobertura/lint ao atualizar | Plano aprovado e regressões da cadeia real; [evidências/proposta](evidencias/issue-266/bloco-7/resultados.json) |
| 10 — conta mínima e vínculo | Implementado: exclusão lógica, e-mail reservado, conteúdo oculto/purga | Responsável por finalidades, com validação jurídica apropriada: base, prazo e data de revisão da guarda; metadados de rejeição e vínculo residual | Guarda excessiva ou descarte incompatível com finalidade; recadastro indisponível | Decisão humana registrada com efeito técnico e revisão dos textos; [retenção](retencao-bloco-5.md), `models/usuario.py`, `services/retencao_service.py` |
| 11 — Marco Civil e logs | Implementado: seis meses corridos em tabela privada | Responsável jurídico: premissa de ausência de fins econômicos/art. 15; operação: logs de cada provedor, retenção, acessos e exportações | Prazo ou escopo inadequado, duplicação externa não inventariada, lacuna em falha de escrita | Premissa revisada e inventário externo confirmado; [acessos](acessos-bloco-6.md), `ACESSO_RETENCAO_MESES`, `registro_acesso_repository.py` |
| 12 — incidentes, controlador e porte | Planejado: procedimento de contenção e comunicação interna | Responsável institucional/jurídico: controlador, qualificação de papéis, porte e prazos legais; operação confirma substituto/canal | Encaminhamento tardio, preservação indevida ou divulgação desnecessária | Papéis aceitos e roteiro exercitado sem dados reais; [manutenção](../operacao/manutencao.md), #267 |
| 13 — fornecedores | Implementado: inventário técnico abaixo; validação externa pendente | Nicolas/operação e responsável jurídico: serviços ativos, região, contratos, subprocessadores e papel jurídico | Transferências/retensões desconhecidas e contratos incompletos | Cada campo externo preenchido com evidência sanitizada e aprovação apropriada; `docs/hospedagem.md`, contexto #261 → #269 |
| 14 — titulares | Implementado: canal DESATIVADO por padrão | Equipe UnDb: escala semanal ou responsável/substituto aceitos, integração e-mail preferencial ou WhatsApp, verificação proporcional, respostas; validação jurídica de prazos | Canal sem capacidade de resposta, exposição de pedido/chave, ativação prematura | Condições de ativação e ensaio completo; sem IA no atendimento; [canal](../canal-titulares.md), #262 → #263 |
| Operação — HTTPS/cookies/origens | Implementado no código; hospedagem pendente de validação | Nicolas: TLS, CORS, origem, cookie Secure/SameSite/HttpOnly e domínio efetivo | Sessão exposta ou acesso legítimo bloqueado | Evidência de navegador/HTTP sanitizada da versão autorizada; `core/auth.py`, `core/origins.py`, #169/#171 |
| Operação — banco e jobs | Implementado: papéis separados no ensaio, purga e pool do limitador | Operação: permissões API/migração, conexões, supervisão e continuidade dos jobs | Purga atrasada; acesso excessivo; esgotamento de conexões | Conferir papéis sem segredos, ciclo e métricas sem pessoas, alerta e retomada; `commands/descartar_moderacao.py`, `core/limite_abuso.py` |
| Backups / restauração | Implementado: ensaio sintético isolado; rotina real planejada | Operação: retenção/local/acesso/cifra, primeiro dado real, arquivo semestral, periodicidade de restauração e registro mínimo de exclusões | Perda de dados ou reexposição de conteúdo excluído após restaurar | Backup/restauração operacionais comprovados e reaplicação de IDs/datas antes de publicar; [ensaio](evidencias/issue-266/bloco-7/resultados.json), #267 |
| Dependências residuais | Implementado: patches source-map-js/zod; audit ainda reporta Next/sharp | Manutenção com acompanhamento de Nicolas: investigar cada advisory/caminho efetivo e propor correção compatível | Risco de disponibilidade ou execução/informação conforme condições de cada aviso; não declarar audit limpo | Análise de aplicabilidade e correções/regressões comprovadas; [inventário e URLs](evidencias/issue-266/bloco-7/resultados.json) |
| CI / release | Evidências locais implementadas; aceite e CI final pendentes de validação | Revisores/PO: verificar SHA do último push e todos os jobs, não reutilizar aprovação de SHA anterior | Entrega revisada diferente da publicada | Checks associados ao SHA final, revisão de riscos e aceite humano; PR #280 e evidências por bloco |
| Textos públicos | Revisão factual implementada; revisão humana pendente | PO/responsável pelo tratamento: política/termos integrados da #269, privacidade e limites de retenção | Informação pública incompleta ou diferente da operação hospedada | Validar textos e suas condições operacionais; seção de alterações abaixo; contexto #268/#269 |

## Inventário técnico de fornecedores

Os serviços abaixo são referidos no código/configuração ou no histórico de
`docs/hospedagem.md`; isso não confirma contrato, conta ativa ou região hoje.
Todos os campos jurídicos/externos permanecem pendentes de validação (item 13).

| Fornecedor / serviço | Dados observados e finalidade | Região / armazenamento | Contrato / papel jurídico |
| --- | --- | --- | --- |
| Vercel — frontend | Código/build e metadados HTTP para servir páginas; logs externos a inventariar | Pendente de validação | Pendente de validação |
| Render — API | Requisições de autenticação, avaliações e atendimento; operação da API | Pendente de validação; não presumir disco/worker contínuo | Pendente de validação |
| Neon — PostgreSQL | Conta, hashes, sessões/tokens, catálogo, avaliações/comentários, denúncias, decisões, pedidos e registros privados | Região, backup/retenção e acessos pendentes de validação | Pendente de validação |
| Resend — e-mail | Destinatário e link opaco de confirmação/recuperação, remetente; finalidade transacional | Região, logs e cota efetiva pendentes de validação | Pendente de validação |
| OpenAI — triagem opcional de moderação | Texto após controles de minimização quando flags autorizadas; apoio/fluxo atual da #239 | Região, retenção externa e subprocessadores pendentes de validação | Pendente de validação; não usado no atendimento a titulares |
| Registro.br — domínio/DNS | Metadados administrativos/DNS para domínio; cadastro do titular não inspecionado | Pendente de validação | Pendente de validação |
| GitHub — código e CI | Código/documentos e dados sintéticos de ensaio; não enviar dumps ou registros de usuários | Artefatos, logs e permissões pendentes de validação | Pendente de validação |
| SIGAA/UnB — fonte pública institucional | Consulta/importação de catálogo docente/turmas; sem credenciais ou histórico estudantil | Origem pública; dados importados no PostgreSQL | Relação e enquadramento pendentes de validação |

## Dependências e aceite da #266

Consulta de #261/#262 confirma consolidações administrativas em #269/#263,
respectivamente; isso não comprova resolução material. A decisão B desta sessão
define o destino de avaliações que o histórico da #262 ainda tratava como aberto.
Nenhuma issue foi alterada/comentada. #267 fornece contexto de incidentes e
restauração: o ensaio do Bloco 7 comprova restore/contagens em 25 tabelas, sem
provar jornada executada no banco restaurado, RPO/RTO ou infraestrutura externa.
#169/#170/#171 dão contexto operacional; #272 se relaciona a dependências;
#268/#269 aos textos/inventário; #263 ao canal. Consome-se o insumo específico,
sem exigir fechamento dessas issues e sem transferir registros para elas.

| Critério da #266 | Situação para revisão |
| --- | --- |
| Sessões, origem, erros e logs sanitizados herdados da #279 | Implementado; evidências anteriores e regressões locais preservadas |
| Núcleo e proteção por fluxo | Implementado nos Blocos 1–4; calibração e infraestrutura pendentes de validação |
| Exclusão, retenção e registros privados | Implementado nos Blocos 5–6; operação e fundamentos/prazos humanos pendentes de validação |
| Alertas de dependências | Patches dirigidos implementados; majors planejadas e Next/sharp pendentes de investigação |
| Versão hospedada, proxy/cookies/logs/permissões | Pendente de validação; nenhuma inspeção ou alteração de produção nesta execução |
| Evidências e consolidação | Implementado em documentos/PR; CI do SHA final e aceite do PO pendentes de validação |

## Registro de revisão dos textos públicos

- `frontend/src/app/sobre/page.tsx`: inclusão de informação factual sobre exclusão
  lógica, conteúdo oculto/janela padrão e registros privados por seis meses;
  explicita que operação na hospedagem permanece pendente de validação. Requer
  revisão humana; não substitui política de privacidade ou termos.
- Home revisada: não foram encontradas afirmações de retenção/exclusão/logs a
  corrigir; texto preservado. O limiar de três avaliações não promete anonimato.
- Na revisão inicial desta branch (c02396c), política e termos estavam ausentes.
  A integração posterior de develop/#281 preserva as páginas da #269 e a ciência
  explícita obrigatória no cadastro. A política foi reconciliada com retenção,
  registros e limitador atuais; revisão humana/operação seguem pendentes. Nenhuma
  base legal nova foi criada para resolver os conflitos.
- Guias técnicos de canal, desenvolvimento e hospedagem passam a apontar para
  o comportamento atual; estudos históricos não são reescritos como execução atual.

As referências de código neste documento usam caminhos relativos a `backend/app/`,
salvo quando indicado. O registro central da execução é a PR #280, continuação
autorizada da #279 integrada. A #266 não é declarada concluída.
