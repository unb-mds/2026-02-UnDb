# Issue #240 — decisões e evidências

Estado: **Proposed**. Base inspecionada: `origin/develop`, commit
`edd4a7beb22fbde74df34fa22f44f35e57ddf642`, em 14/11/2026.
Inspeção estática, somente leitura; nenhum ataque ou ensaio em produção.
Criar skills não corrige vulnerabilidades nem comprova segurança do ambiente.

## Decisão anterior à criação

Comparação de descrição, escopo e gatilhos das quatro skills existentes:

| Tema | Decisão | Justificativa e fronteira |
|---|---|---|
| Revisão de segurança | CREATE `security-review` | Recorre por mudança de exposição, integração ou operação, mesmo sem diff. Possui análise de ameaças e matriz de evidência próprias. Estender `code-review` ampliaria seu gatilho, atualmente limitado a mudanças identificáveis. |
| Resposta a incidentes | CREATE `incident-response` | Sinal de incidente exige triagem, contenção, comunicação e recuperação; não é implementação nem revisão de mudança. Nenhuma das quatro skills possui esse ciclo operacional. |
| Correções | NO-SKILL adicional | `implementation` já executa mudanças autorizadas; esta entrega só encaminha tarefas. |
| Testes de segurança | NO-SKILL adicional | `testing` já planeja/executa verificações autorizadas; cenários aqui são exercícios de mesa, não outra estratégia de testes. |
| Revisão de diff | NO-SKILL adicional | `code-review` mantém findings e avaliação de alterações; recebe os resultados de segurança pertinentes. |
| Mudança estrutural | NO-SKILL adicional | `architecture` já analisa propostas sistêmicas; controles novos não são aprovados por estas skills. |
| IA e operação hospedada | NO-SKILL adicional | #239 e #171 possuem as entregas específicas; as duas propostas só verificam riscos e encaminham evidências. |

Nenhuma EXTEND selecionada: os dois ciclos têm gatilhos e saídas próprios;
as responsabilidades já cobertas permanecem nas fontes existentes.
Não foram modificadas skills `defined`, adapters ou fronteiras de governança.

## Código observado e limites da evidência

Caminhos abaixo são relativos à raiz, com símbolo/trecho para localização na base.
São fatos de código/documentação, não resultados de execução.

| Fonte e trecho | O que foi observado | O que não comprova |
|---|---|---|
| `backend/app/core/auth.py`, `obter_moderador`; `routers/moderacao.py`, `Moderador`; `services/moderacao_service.py`, `autorizar` | Dependência exige conta confirmada e papel de moderador; serviço também verifica papel/confirmação. | Ausência de toda falha de autorização ou configuração correta de papéis em produção. |
| `backend/app/services/moderacao_service.py`, erros de impedimento por autoria/denúncia | Há impedimentos de decisão para moderador envolvido. | Revisão integral de todos os caminhos de dados privados. |
| `backend/app/core/auth.py`, `definir_cookie_sessao` | HttpOnly, SameSite=lax, Secure condicionado a `not DEBUG`. | Cookies seguros no deploy ou cobertura suficiente contra CSRF. |
| `backend/app/services/auth_service.py`, `SESSION_TTL`, `validar_e_renovar_sessao`; `core/security.py`, `gerar_hash_token` | Prazo de sete dias, verificação de expiração, renovação e busca por hash do token. | Teste de revogação ou jornada pública nesta inspeção. |
| `backend/app/main.py`, `add_middleware`; `core/config.py`, `CORS_ORIGINS` | Origens configuráveis, credenciais permitidas, métodos/headers amplos. | CORS efetivo do ambiente; CORS não substitui análise CSRF. |
| `backend/app/schemas/auth.py`, Fields/validadores | Limites de tamanho em e-mail/senha e validação de entradas. | Proteção integral contra abuso ou injeção. |
| `backend/app/repositories/avaliacao_repository.py`, consultas `select(...).where(...)`; `frontend/src/components/item-comentario.tsx`, `{comentario.texto}` | Consultas ORM e texto em expressão JSX nos trechos lidos. | Ausência global de SQL injection/XSS; demais destinos precisam de análise contextual. |
| `backend/app/core/config.py`, `SECRET_KEY`, `DATABASE_URL`, `RESEND_API_KEY` | Configuração externa; valores reais não foram consultados. | Ausência de segredos em logs, histórico ou infraestrutura. |
| `backend/app/services/denuncia_service.py`, `LIMIAR_SUSPENSAO`, `registrar`; `repositories/denuncia_repository.py`, `contar_contas` | Duplicata de conta rejeitada; contagem distinta para suspensão; limiar existente 50, também documentado em requisitos. | Resistência a contas coordenadas; denúncias não são julgamento de procedência. |
| `backend/app/commands/descartar_moderacao.py`, `--continuo`; `docs/hospedagem.md`, “Tarefas fora do servidor HTTP” | Comando periódico existente; guia distingue execução local de operação hospedada ainda sem evidência. | Worker contínuo instalado no ambiente público. |
| `docs/requisitos.md`, “Estados, transições e retenção de RF20–RF22” | Denúncias encerradas não são conservadas; textos removidos/retirados têm uma semana interna; textos rejeitados/substituídos não são conservados conforme transição. | Permissão para criar arquivo de evidências com cópias de conteúdo privado. |
| `docs/hospedagem.md`, “Backup e restauração — roteiro ainda não executado” | Roteiro isolado documentado, sem evidência de dump/restauração nesta fonte. | Backup periódico ou recuperação validada. |
| `docs/hospedagem.md`, tabela `MIGRATION_DATABASE_URL` e seção de papel limitado; `core/config.py`, fallback para `DATABASE_URL` | Separação de conexões prevista; fallback existe. | Uso efetivo do papel limitado no deploy. |

## Lacunas priorizadas — proposta de ordem, sem SLA

Nenhuma vulnerabilidade explorável foi confirmada por esta inspeção limitada.
“Confirmada” abaixo qualifica a lacuna documental, não um incidente.

| Ordem | Classe / evidência | Impacto potencial | Encaminhamento e evidência necessária |
|---|---|---|---|
| 1 | Lacuna confirmada de comprovação operacional: #171, atualização de 12/11, e guia de hospedagem | Exposição de sessão/dados ou perda de privacidade por descarte inoperante | Manter em #171: evidência sanitizada de HTTPS/CORS/cookies/variáveis, papel limitado, jornada completa e worker contínuo; não duplicar implantação. |
| 2 | Lacuna confirmada de recuperação no roteiro de hospedagem; #171 ainda distingue documentação de recuperação comprovada | Perda de dados/indisponibilidade prolongada | Evidenciar ensaio isolado e rollback em #171, articulando entrega existente da #170, já encerrada; tarefa própria se exceder o escopo operacional. Não reabrir #170 implicitamente. |
| 3 | Hipótese a investigar: busca por `rate.limit`, `slowapi`, `limiter`, `csrf` em `backend/app` e `frontend/src` sem correspondências | Abuso de cadastro/login/avaliação/denúncia e ações entre sites | Tarefa própria de análise de abuso e CSRF, incluindo infraestrutura não inspecionada. Ausência de termos não comprova ausência de controle. Limites e mudanças dependem de decisão. |
| 4 | Evolução condicionada: #239 aberta, não comprovação de controle de IA implantado | Manipulação, vazamento de texto ou custo indevido | #239: contrato de saída, minimização, provedor/retenção, tamanho/tempo/tentativas/chamadas/custos e fallback humano antes de ativar. |
| 5 | Melhoria de evidência: trechos de autorização, ORM, JSX e configuração acima têm alcance limitado | Dados privados expostos, XSS/injeção ou segredo em log | Tarefas próprias para revisão completa de fluxos sensíveis e destinos de logs; nunca publicar valores. Dependências: inventário e advisories aplicáveis por versão em tarefa própria; nenhum CVE foi afirmado ou scanner executado. |

## Decisões pendentes (Pending Decision)

- Responsável operacional por incidente, substituto e autoridade para conter/recuperar: **decisão pendente**. Assignees das issues não são automaticamente esses papéis.
- Canal privado de relato, escalonamento, armazenamento restrito e canal de comunicação pública: **decisão pendente**. Não usar issue pública para evidência sensível.
- Ferramentas aprovadas para diagnóstico, dependências, evidências e sanitização: **decisão pendente**.
- Critérios de gravidade, prazos/SLAs, cadência de comunicação e encerramento operacional: **decisão pendente**; sem valores presumidos.
- Política de backup, responsáveis, acesso, retenção compatível, objetivos de recuperação e evidência de restauração: **decisão pendente**, coordenar #171.
- Provedor/modelo/retenção de IA, custos e limites de chamadas, metas de validação e autorização de envio: **decisão pendente** em #239.
- Controles novos de abuso/CSRF, alterações de produto/arquitetura e permissões: **decisão pendente**, tarefas próprias e respectivas aprovações.
- Apresentação e aprovação das propostas pelo PO: **decisão pendente**. PR para revisão não comprova apresentação realizada ou aceite; usar Refs #240.

## Referências primárias consultadas em 14/11/2026

- [Issue #240](https://github.com/unb-mds/2026-02-UnDb/issues/240): escopo e aceite.
- [Issue #239](https://github.com/unb-mds/2026-02-UnDb/issues/239): IA assistiva, sem decisão autônoma.
- [Issue #171](https://github.com/unb-mds/2026-02-UnDb/issues/171): evidências operacionais restantes.
- `docs/requisitos.md`, RF20–RF22; `docs/arquitetura.md`, sessões e limites RF20–RF22: contratos e contexto, sem substituir inspeção de código.
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html): menor privilégio e verificação de permissões por requisição.
- [OWASP LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html): separação de instruções/dados e validação de saída.
- [NIST SP 800-61 Rev. 3, abril de 2025](https://csrc.nist.gov/pubs/sp/800/61/r3/final): resposta integrada à gestão de riscos, detecção, resposta e recuperação. Não define responsáveis, ferramentas ou SLA do UnDb.
