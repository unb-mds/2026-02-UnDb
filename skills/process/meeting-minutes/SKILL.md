---
name: meeting-minutes
description: Registra atas de reuniões do projeto com fatos, decisões, pendências e encaminhamentos rastreáveis. Use ao criar, revisar ou atualizar uma ata sem inventar presença, consenso, aprovação ou mudança de escopo.
metadata:
  project-version: "1.0.0"
  project-status: "defined"
  project-category: "process"
  project-scope: "meeting-records"
  agent-agnostic: "true"
---

# Meeting Minutes

## 1. Objective

Produzir atas concisas e verificáveis para preservar o contexto de reuniões recorrentes do G7, distinguindo o que foi informado, confirmado, decidido, proposto ou deixado pendente.

## 2. Scope

Esta skill registra metadados da reunião, pauta, síntese, decisões, pendências, responsáveis, prazos, vínculos com Issues e próximos passos quando essas informações estiverem disponíveis. Ela pode revisar uma ata existente contra suas fontes, mas não conduz a reunião, define o processo Scrum, cria requisitos, toma decisões de produto ou altera o estado de Issues e Pull Requests.

## 3. When to use

Use ao criar ou revisar atas de planejamento, acompanhamento, review, retrospectiva, alinhamento técnico ou outra reunião do projeto; ao transformar notas fornecidas pela equipe em registro rastreável; ou ao consolidar decisões e ações confirmadas durante uma reunião.

## 4. When not to use

- Use a responsabilidade de Scrum aplicável para definir ou conduzir cerimônias e alterar o processo.
- Use `requirements` para criar ou modificar requisitos.
- Use `architecture` para analisar ou preparar decisões arquiteturais.
- Use `project-governance` para determinar autoridade e aprovação.
- Use o processo de GitHub aplicável para alterar Issues, Pull Requests, milestones ou responsáveis.

Uma ata registra o que ocorreu; ela não substitui a fonte responsável por executar ou aprovar cada encaminhamento.

## 5. Expected inputs

Use somente informações disponíveis: data, horário, local ou formato, participantes, pauta, notas, decisões, divergências, ações, responsáveis, prazos e referências do projeto. Issues, documentos e mensagens podem servir como evidência do estado atual, mas não provam por si sós que um tema foi discutido ou aprovado na reunião.

## 6. Pre-conditions

1. Identifique a reunião e o período a registrar.
2. Separe informações fornecidas sobre a reunião de contexto consultado posteriormente.
3. Confirme quais decisões e responsáveis foram explicitamente registrados.
4. Marque dados ausentes ou conflitantes sem preenchê-los por suposição.

## 7. Procedure

1. Registre data, horário, objetivo e, quando informados, participantes, local e duração.
2. Resuma a pauta e os pontos discutidos de forma factual, sem atribuir fala ou concordância sem evidência.
3. Diferencie decisão confirmada, proposta, decisão pendente e simples informação. Preserve os estados `Defined`, `Proposed`, `Pending Decision` e `Not Currently Applicable` quando relevantes.
4. Para cada encaminhamento confirmado, registre ação, responsável, prazo e dependência quando disponíveis. Não invente valores para completar a tabela ou lista.
5. Vincule requisitos, documentos, Issues ou Pull Requests somente quando a relação estiver sustentada. Não use `Closes` ou equivalente se a reunião não autorizou e concluiu formalmente o item.
6. Registre divergências, bloqueios e itens não discutidos que limitem a interpretação da ata.
7. Revise a ata para garantir que ela não transforme silêncio, presença, sugestão ou contexto externo em consenso ou aprovação.

## 8. Expected output

A ata deve ser proporcional à reunião e normalmente conter:

- identificação e objetivo;
- pauta ou contexto;
- síntese dos pontos confirmados;
- decisões e respectivos estados;
- pendências e encaminhamentos;
- responsáveis, prazos e dependências conhecidos;
- referências e limitações relevantes.

Use Markdown quando o repositório não definir outro formato. Preserve a organização existente quando atualizar uma ata.

## 9. Constraints

Nunca invente participante, presença, horário, duração, local, fala, voto, consenso, decisão, responsável, prazo ou vínculo. Não apresente contexto obtido depois da reunião como se tivesse sido discutido nela. Não altere requisito, arquitetura, processo, Issue, PR ou milestone como consequência implícita da ata. Não trate a redação pronta como aceite dos participantes.

## 10. Human approval

O agente pode preparar e revisar a ata dentro das informações fornecidas. Ações reservadas por `project-governance`, como decisões de produto, mudanças de requisito, arquitetura, modelo de dados, processo Scrum ou merge, continuam exigindo aprovação humana explícita. A ata só registra uma aprovação quando a evidência disponível identifica de forma suficiente a decisão e sua autoridade.

A promoção desta skill de `proposed` para `defined` também depende de aprovação humana conforme o processo de `skill-authoring`.

## 11. Verification

- [ ] Data, horário e objetivo têm fonte ou estão marcados como não registrados.
- [ ] Participantes e presença não foram inferidos.
- [ ] Contexto posterior está separado do conteúdo confirmado da reunião.
- [ ] Decisões, propostas e pendências estão diferenciadas.
- [ ] Cada ação possui apenas responsáveis, prazos e dependências confirmados.
- [ ] Referências não encerram nem aprovam trabalho indevidamente.
- [ ] Limitações, divergências e aprovações necessárias permanecem explícitas.

## 12. Interaction with other skills

`project-governance` define autoridade, estados e fronteiras de aprovação; `skill-authoring` governa o ciclo desta skill. `requirements` e `architecture` recebem mudanças que surgirem da reunião em seus respectivos domínios. Skills de implementação, testing e code review recebem ações técnicas autorizadas. O processo de Scrum ou GitHub aplicável governa cerimônias e alterações operacionais; esta skill limita-se ao registro.

## 13. Handling uncertainty and failures

Se faltar informação, registre "não informado" ou omita o campo quando isso não prejudicar a interpretação. Se fontes divergirem, descreva o conflito e não escolha silenciosamente. Se houver evidência de que uma alternativa foi efetivamente proposta, mas não aprovada, registre-a como `Proposed`. Se o tema exigir uma decisão e não houver evidência suficiente de decisão ou proposta concreta, registre-o como `Pending Decision`. Quando as fontes não permitirem confirmar o tema ou encaminhamento, marque a informação como não verificada ou omita-a. Se as notas forem insuficientes para uma ata confiável, produza apenas o registro sustentado e solicite confirmação humana para os pontos materiais restantes.
