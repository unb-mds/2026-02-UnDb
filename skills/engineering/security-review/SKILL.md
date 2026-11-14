---
name: security-review
description: Analisa ameaças, controles e evidências de segurança técnica e operacional. Use em revisões de exposição, integrações, abuso ou preparação de publicação, mesmo sem diff; produz achados e encaminhamentos sem executar ataques ou correções.
metadata:
  project-version: "0.1.0"
  project-status: "proposed"
  project-category: "engineering"
  project-scope: "security"
  agent-agnostic: "true"
---

# Security Review

## 1. Objective

Identificar riscos recorrentes com evidência, impacto e mitigação proposta, sem confundir instruções com controles implementados. Estado proposed: este workflow aguarda aprovação.

## 2. Scope

Revisão estática de confiança, dados privados, superfícies técnicas, abuso e integrações de IA; começa na delimitação da superfície e termina no relatório e handoffs.

## 3. When to use

Mudança de exposição pública, autenticação, moderação, integração externa ou configuração; preparação de release ou revisão periódica autorizada, inclusive sem diff.

## 4. When not to use

Não substitui revisão de diff, implementação, testes, arquitetura ou resposta a incidente ativo. Encaminhar cada responsabilidade conforme seção 12.

## 5. Expected inputs

Escopo autorizado, versão/commit, requisitos, arquitetura, contratos, configuração sanitizada, issues e evidências existentes. Consultar o [registro inicial](references/issue-240.md) apenas quando pertinente; revalidar fatos antigos.

## 6. Pre-conditions

Identificar ativos, atores e fronteiras de confiança; confirmar acesso somente leitura e fontes autorizadas. Nunca exigir credenciais reais para concluir uma análise documental.

## 7. Procedure

1. Delimitar superfície, versão e limites da inspeção. Mapear navegador, API, banco, operador, moderador e eventual provedor de IA; identificar dados que cruzam cada fronteira.
2. Para cada item abaixo, registrar ameaça, controle observado com arquivo/símbolo ou issue, limite da evidência, impacto e mitigação proposta. Não usar a existência desta checklist como evidência de controle:
   - Autorização e dados privados: permissão por operação/objeto, autoria, impedimentos, separação público/interno, negação segura e menor privilégio de API, banco, migração e operação.
   - Sessões/cookies: geração, hash, expiração, renovação, logout e flags; analisar CSRF em operações mutáveis e origens/CORS com credenciais. Não presumir que SameSite ou CORS isoladamente resolvem CSRF; conferir configuração publicada só com evidência autorizada.
   - XSS/injeção: validação de entrada, consultas parametrizadas e destinos de texto/HTML/URLs; comentários e justificativas de IA não devem virar HTML ou comandos confiáveis.
   - Segredos: configuração, logs, artefatos, histórico e acesso. Se encontrar segredo/dado pessoal, registrar somente local e tipo, sem copiar valor nem ampliar divulgação.
   - Dependências: versões e lockfiles, fontes primárias de advisories, aplicabilidade e mitigação. Ferramenta ou consulta indisponível implica “não verificado”, nunca ausência de vulnerabilidade.
   - Abuso: cadastro/login, tentativa automatizada, avaliação repetida e denúncias coordenadas; distinguir limites existentes de propostas. Não alterar escalas, agregação ou limiares aprovados.
   - IA (#239): comentário é dado não confiável, não muda política nem aciona ferramentas; verificar saída estruturada, tratamento da justificativa, minimização inclusive de dados pessoais no texto, retenção externa e limites de tamanho, tempo, tentativas, chamadas e custos. Valores sem aprovação são decisão pendente. Falha/saída inválida fica na fila humana; IA não publica/remove/rejeita autonomamente.
   - Operação (#171): permissões efetivas, descarte contínuo, backups, ensaio isolado de restauração e reversão; roteiro ou CI não comprovam execução em produção.
3. Classificar cada resultado: **confirmado** (comportamento ou lacuna diretamente sustentada), **hipótese** (condições ainda não verificadas) ou **melhoria** (proposta adicional). Não chamar vulnerabilidade de confirmada sem evidência suficiente.
4. Priorizar qualitativamente pelo impacto e exposição demonstrados, explicando incerteza; sem inventar score, SLA ou limiar. Relacionar às issues existentes antes de propor tarefa própria.
5. Se houver sinal de incidente, encaminhar a `incident-response` sem explorar. Entregar relatório sanitizado e decisões pendentes; não corrigir produto nesta atividade.

## 8. Expected output

Matriz `classe | ameaça | evidência/versão | impacto | mitigação proposta | encaminhamento`; cobertura e itens não verificados; lista priorizada de lacunas e decisões pendentes. Separar “o código faz” de “a skill orienta”.

## 9. Constraints

Somente leitura: sem ataques, exploração de terceiros, coleta de credenciais SIGAA, históricos ou ponderação por IRA. Não mudar produto, permissões, arquitetura ou retenção. Evidência mínima sem autores/segredos; seguir retenção vigente, sem cópias integrais adicionais.

## 10. Human approval

Aplicar [project-governance](../../governance/project-governance/SKILL.md). Análise e propostas podem prosseguir no escopo autorizado; adoção da skill e alterações derivadas dependem de aprovação pertinente. Não promover a defined. Provedor, envio real à IA e custos seguem #239.

## 11. Verification

- [ ] Todos os domínios da seção 7 possuem evidência ou limitação explícita.
- [ ] Achados, hipóteses e melhorias estão separados; impacto e encaminhamento são rastreáveis.
- [ ] Nenhum controle foi inferido da mera instrução, nenhum segredo/autor foi copiado.
- [ ] Lacunas de #171/#239 foram relacionadas sem duplicar entregas.
- [ ] [Cenários sintéticos](references/scenarios.md) foram percorridos como exercício de mesa, sem alegar teste real.

## 12. Interaction with other skills

`skill-authoring` governa autoria; `project-governance`, autoridade. `code-review` recebe findings relativos a diffs; `testing`, verificações autorizadas; `implementation`, correções em tarefas próprias; `architecture`, mudanças estruturais. `incident-response` recebe sinais ativos. Não repetir seus workflows.

## 13. Handling uncertainty and failures

Registrar informação ausente como não verificada e decisão material como **decisão pendente**; continuar itens independentes. Referência externa não consultada fica “a verificar”. Se acesso exigir expor dados ou explorar sistema, parar essa parte e solicitar encaminhamento humano seguro.
