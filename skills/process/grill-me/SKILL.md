---
name: grill-me
description: Estressa um plano, proposta ou decisão antes de sua execução por meio de perguntas que revelam premissas, alternativas, riscos e casos não considerados. Use somente quando uma pessoa pedir explicitamente para ser questionada, testar ou "grillar" seu raciocínio.
metadata:
  project-version: "0.1.0"
  project-status: "proposed"
  project-category: "process"
  project-scope: "pre-execution-decision-stress-testing"
  agent-agnostic: "true"
---

# Grill Me

## 1. Objective

Expor e resolver, antes da execução, decisões, premissas, dependências, riscos, alternativas e casos de borda que permanecem implícitos em um plano, proposta ou desenho.

## 2. Scope

Esta skill conduz uma investigação dialogada de uma proposta por meio de uma árvore de decisões. Ela identifica fatos que podem ser verificados no repositório ou no ambiente e leva à pessoa somente as decisões que ela precisa tomar.

Ela não define requisitos, toma decisão de produto ou arquitetura, implementa, testa ou revisa uma alteração de código já produzida.

## 3. When to use

Use somente mediante pedido explícito para "grill me", questionar, estressar, entrevistar ou encontrar lacunas em um plano, proposta, decisão ou desenho antes de executá-lo.

## 4. When not to use

Não use para estruturar ou alterar requisitos (`requirements`), analisar uma decisão arquitetural (`architecture`), executar trabalho autorizado (`implementation`) ou inspecionar um diff, commit ou Pull Request (`code-review`).

Não a acione implicitamente apenas porque há um plano; a pessoa deve escolher essa investigação.

## 5. Expected inputs

Use a proposta ou plano a examinar e, quando disponíveis, seu objetivo, escopo, restrições, decisões já registradas, requisitos, artefatos técnicos e contexto do repositório.

Não presuma que informação ausente seja uma decisão tomada.

## 6. Pre-conditions

1. Confirme que o objetivo é explorar a proposta antes de executá-la.
2. Delimite o plano ou decisão sob investigação e as fontes disponíveis.
3. Leia `project-governance` quando a investigação puder revelar uma decisão sujeita a aprovação humana.
4. Inspecione fatos acessíveis no repositório ou ambiente antes de perguntar por eles.

## 7. Procedure

1. Modele a proposta como uma árvore de decisões: cada decisão abre as decisões que dependem dela.
2. Identifique a fronteira atual: decisões cujos pré-requisitos já estão resolvidos, sem supor respostas ainda não recebidas.
3. Verifique diretamente os fatos necessários para as perguntas da fronteira, usando o repositório, documentação ou ferramentas disponíveis. Não peça à pessoa algo que possa ser apurado dessa forma.
4. Faça, em uma rodada, as perguntas independentes da fronteira. Numere cada pergunta, explique o ponto em aberto e apresente uma resposta recomendada.
5. Aguarde as respostas antes de perguntar decisões que dependam delas. Recalcule a fronteira a cada rodada.
6. Separe fatos observados, respostas da pessoa, inferências, alternativas, riscos e decisões pendentes. Não trate recomendação como decisão aprovada.
7. Quando a fronteira estiver vazia, apresente o entendimento compartilhado, as decisões tomadas, riscos e pendências. Não execute o plano até que a pessoa confirme esse entendimento e o trabalho tenha o handoff apropriado.

## 8. Expected output

Produza rodadas de perguntas com recomendações, seguidas por um resumo verificável das decisões, premissas confirmadas, alternativas descartadas, riscos, casos de borda, fatos inspecionados e pendências que ainda bloqueiam a execução.

## 9. Constraints

Nunca:

- faça perguntas em lote sobre decisões que dependem umas das outras;
- peça um fato que possa ser verificado no contexto acessível;
- invente requisitos, decisões, restrições ou evidências;
- confunda recomendação com aprovação;
- transforme a investigação em implementação, mudança arquitetural, definição de requisito ou code review;
- execute a proposta antes da confirmação de entendimento compartilhado e das autorizações aplicáveis.

## 10. Human approval

Esta skill pode investigar, inspecionar evidências, comparar alternativas e recomendar respostas. As decisões de produto, requisito, arquitetura, tecnologia estrutural ou outra ação reservada permanecem sujeitas a `project-governance` e à aprovação humana aplicável.

Como esta skill está `proposed`, seu procedimento não é uma regra autoritativa do projeto até aprovação humana explícita.

## 11. Verification

- [ ] O pedido explícito de investigação foi identificado.
- [ ] O plano e seu escopo foram delimitados.
- [ ] Fatos acessíveis foram inspecionados antes de serem perguntados.
- [ ] Cada rodada contém somente decisões independentes da fronteira atual.
- [ ] Cada pergunta contém uma recomendação e não pressupõe sua aceitação.
- [ ] Perguntas dependentes aguardaram os respectivos pré-requisitos.
- [ ] Fatos, inferências, recomendações e decisões foram separados.
- [ ] Riscos, alternativas, casos de borda e pendências foram registrados quando aplicáveis.
- [ ] Nenhuma decisão pendente foi tratada como definida e nenhuma execução foi iniciada implicitamente.

## 12. Interaction with other skills

- `project-governance` define autoridade, evidência, escopo e aprovação humana; esta skill consulta esses limites sem duplicá-los.
- `requirements` recebe lacunas que sejam requisitos ou critérios de aceite.
- `architecture` recebe questões que exijam análise ou mudança de decisão estrutural.
- `implementation` só recebe o handoff após entendimento compartilhado, decisão autorizada e escopo executável.
- `code-review` atua sobre mudanças de código identificáveis depois da implementação; não substitui esta investigação prévia.
- `skill-authoring` governa o ciclo de vida desta skill.

## 13. Handling uncertainty and failures

Se um fato não puder ser inspecionado, declare a limitação e formule a decisão apenas com o contexto disponível. Se fontes conflitarem, identifique o conflito, não escolha silenciosamente e encaminhe-o à fonte ou autoridade apropriada. Se uma resposta abrir novas dependências, acrescente-as à árvore e retome a fronteira quando seus pré-requisitos estiverem resolvidos. Se não houver entendimento compartilhado, mantenha o plano como `Pending Decision` e não faça handoff para execução.
