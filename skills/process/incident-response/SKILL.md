---
name: incident-response
description: Orienta triagem, contenção reversível proposta, recuperação e comunicação de incidentes. Use diante de indício de abuso, exposição de dados ou ataque técnico; preserva crítica acadêmica legítima, evidências mínimas e aprovação operacional.
metadata:
  project-version: "0.1.0"
  project-status: "proposed"
  project-category: "process"
  project-scope: "security"
  agent-agnostic: "true"
---

# Incident Response

## 1. Objective

Organizar uma resposta rastreável a sinais de incidente, reduzindo exposição sem ampliar retenção nem confundir crítica legítima com ataque. Workflow proposed, aguardando aprovação.

## 2. Scope

Da recepção do sinal à revisão posterior: triagem, coordenação, proposta de contenção reversível, recuperação e comunicação. Não concede acesso operacional nem autorização de executar intervenções.

## 3. When to use

Indício de acesso indevido, vazamento, segredo em log, abuso coordenado, indisponibilidade ou ataque técnico. Um sinal ainda não confirmado exige triagem, não declaração automática de incidente.

## 4. When not to use

Crítica acadêmica negativa legítima segue a política de comentários; denúncia ordinária segue a fila humana existente. Revisão preventiva pertence a `security-review`; correções e testes a suas skills.

## 5. Expected inputs

Sinal sanitizado, horário/fuso, versão afetada, impacto observado, fonte de evidência mínima, contratos de retenção, procedimentos de recuperação e autorizações disponíveis. [Registro inicial e pendências](../../engineering/security-review/references/issue-240.md) não substitui verificação atual.

## 6. Pre-conditions

Verificar responsável e substituto, canal privado, autoridade de contenção/recuperação e acesso restrito à evidência. Se inexistentes: **decisão pendente**; preparar triagem sanitizada e proposta, sem escolher pessoas/canais nem intervir no ambiente.

## 7. Procedure

1. **Receber e coordenar.** Registrar sinal, horário, fonte e impacto sem texto integral, autor, e-mail, token ou cookie. Responsável e canal precisam de fonte explícita; sem definição, escalar a decisão humana por meio já autorizado, sem publicar evidência sensível.
2. **Triar.** Separar fato observado, hipótese e lacuna. Classificar abuso (ex.: coordenação de denúncias), exposição de dados ou ataque técnico/indisponibilidade; categorias podem coexistir. Avaliar alcance e impacto sem inventar limiares ou SLAs. Crítica negativa sem violação da política não é incidente; quantidade de denúncias não prova culpa. Preservar a revisão humana e impedimentos de moderação.
3. **Preservar o mínimo.** Manter linha do tempo, versão, categoria, contagem agregada e referência restrita à fonte quando compatível com a retenção vigente. Não exportar logs/comentários integrais, copiar autores ou manter identificadores que permitam reidentificação. Não suspender descarte nem arquivar denúncias encerradas. Se a fonte expirar, registrar a limitação, não criar retenção paralela. Se encontrar segredo, informar só local/tipo em meio apropriado.
4. **Propor contenção reversível.** Descrever objetivo, escopo, efeito colateral, autorização necessária, estado anterior sem segredos e caminho de reversão. Exemplos condicionais: desligar apoio de IA por mecanismo existente autorizado ou reverter versão pelo procedimento vigente. Validar se o mecanismo realmente existe. Não remover conteúdo por ser crítica, alterar permissões/limiares, apagar dados, desligar serviços ou rotacionar credenciais sem autorização específica. Ações destrutivas não são autorizadas por esta skill. Rotação/revogação de credencial, quando necessária, exige plano próprio e autoridade explícita; nunca anexar o valor.
5. **Recuperar.** Usar procedimento existente de atualização/diagnóstico/reversão em `docs/hospedagem.md`; rollback de aplicação não reverte migrações. Antes de restauração, conferir autorização, origem/destino isolado, integridade e prazos de descarte. Não restaurar texto que deveria estar descartado nem dados expirados em cópias. Backup documentado não é recuperação comprovada. Registrar verificações autorizadas de sessão, autorização, jornadas e descarte; encaminhar execução a operadores e `testing`.
6. **Comunicar.** Preparar informe para revisão humana: o que se sabe, impacto, incertezas, ação autorizada realizada (se houver evidência) e próxima atualização a definir. Destinatários, canal, responsável e cadência são decisão pendente quando não definidos. Comunicação pública não contém evidências privadas, autores ou segredos; não prometer recuperação sem comprovação. Não enviar mensagens por conta própria.
7. **Revisar depois.** Registrar causa confirmada ou hipótese, linha do tempo sanitizada, eficácia/efeitos da contenção, evidência de recuperação e tarefas preventivas. Relacionar #171 para operação e #239 para IA. Encerramento operacional e aceite dependem do responsável autorizado; aprovação da documentação não encerra incidente.

## 8. Expected output

Registro sanitizado com sinal, classificação, fatos/hipóteses, impacto, referência mínima, responsável/canal definidos ou pendentes; plano de contenção e reversão, recuperação e critérios de verificação; rascunho de comunicação, revisão posterior e handoffs. Distinguir plano de ação realmente executada.

## 9. Constraints

Sem exploração, ataques, ações destrutivas ou testes em terceiros/sistemas reais. Não ampliar retenção, acessar autores sem necessidade/autorização ou expor segredos. Sem coleta SIGAA, históricos, IRA ou mudança de produto/arquitetura/permissões. Respeitar RF20–RF22, inclusive anonimato público e descarte.

## 10. Human approval

Aplicar [project-governance](../../governance/project-governance/SKILL.md). Pode preparar análise e planos; intervenção, comunicação externa e recuperação exigem autorização específica e responsável definido. Aprovação desta skill não é autorização permanente de operar. Promoção a defined exige aprovação humana explícita.

## 11. Verification

- [ ] Classificação diferencia crítica legítima, abuso, exposição e ataque técnico.
- [ ] Canal/responsável têm fonte ou estão como decisão pendente.
- [ ] Evidência mínima respeita privacidade e descarte vigente, inclusive em backups.
- [ ] Contenção tem escopo, autorização e reversão; recuperação tem evidência ou limitação.
- [ ] Comunicação e encerramento não foram tratados como aprovados por inferência.
- [ ] Percorrer os [cinco cenários sintéticos](../../engineering/security-review/references/scenarios.md) sem executar ataques.

## 12. Interaction with other skills

`project-governance` delimita autoridade e `skill-authoring` a autoria. `security-review` analisa riscos e prevenção; `testing` verifica recuperação autorizada; `implementation` recebe correções próprias; `code-review` revisa seus diffs e `architecture` recebe decisões estruturais. Reutilizar operação de #171, sem novo roteiro de backup concorrente.

## 13. Handling uncertainty and failures

Sem canal, responsável, mecanismo de reversão ou autorização, interromper só a intervenção dependente e registrar **decisão pendente**. Continuar análise sanitizada. Se recuperação falhar, não declarar serviço recuperado, não repetir ação destrutiva e encaminhar decisão ao responsável autorizado. Conflitos de retenção não autorizam cópias preventivas.
