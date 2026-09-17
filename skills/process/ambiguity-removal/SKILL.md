---
name: ambiguity-removal
description: Identifica, classifica e torna explícitas ambiguidades em requisitos, especificações, documentação, issues, decisões, contratos, propostas e critérios de aceite antes que interpretações divergentes gerem execução ou registro incorreto. Use ao auditar um artefato por leituras plausíveis, termos vagos, lacunas, conflitos ou inconsistências.
metadata:
  project-version: "0.1.0"
  project-status: "proposed"
  project-category: "process"
  project-scope: "cross-artifact-ambiguity-analysis"
  agent-agnostic: "true"
---

# Ambiguity Removal

## 1. Objective

Encontrar interpretações plausíveis diferentes para um artefato do projeto antes que uma pessoa ou agente precise escolher uma delas. A skill torna a divergência observável, rastreável e encaminhável sem resolver a ambiguidade silenciosamente.

## 2. Scope

Audite requisitos, especificações, documentação, issues, decisões, contratos, propostas, critérios de aceite e interfaces entre componentes. Procure termos vagos ou não definidos, quantificadores vagos, atores ou referências ausentes, caminhos e casos de borda omitidos, conflitos, incompletude, critérios não verificáveis e terminologia inconsistente entre artefatos.

Esta skill identifica e relata ambiguidade. Ela não aprova requisitos, escolhe a interpretação, decide produto ou arquitetura, modela banco, implementa, testa ou revisa código como atividade principal.

## 3. When to use

Use antes de planejamento ou implementação, quando um artefato precisa ser auditado quanto a interpretações divergentes, coerência com outras fontes ou capacidade de verificação. Use também quando uma inconsistência for descoberta durante outra atividade, encaminhando-a à autoridade correspondente.

## 4. When not to use

Não use para:

- definir ou reestruturar requisitos (`requirements`);
- conduzir uma entrevista de decisões ou estressar uma proposta (`grill-me`);
- decidir ou revisar arquitetura (`architecture`);
- decidir modelo relacional ou detalhes PostgreSQL (`database-design`, `postgresql`);
- implementar uma decisão (`implementation`);
- revisar código já implementado (`code-review`).

Uma ambiguidade encontrada pode ser encaminhada a essas skills, mas não deve ser absorvida por elas silenciosamente.

## 5. Expected inputs

Receba o artefato a auditar, sua localização e, quando disponíveis, fontes relacionadas, glossário, decisões, requisitos, contratos, issues, código e documentação derivados. Se o texto ou o contexto não estiver acessível, registre essa limitação; não invente findings.

## 6. Pre-conditions

1. Delimite o artefato, versão ou conjunto de fontes que será auditado.
2. Identifique a finalidade e o estado de cada fonte: `Defined`, `Proposed`, `Pending Decision` ou `Not Currently Applicable`.
3. Localize a hierarquia de autoridade aplicável; no G7, `docs/requisitos.md` é fonte de verdade e `specs.md` é derivado.
4. Leia glossários, decisões e artefatos relacionados antes de classificar um termo como não definido ou uma afirmação como conflitante.
5. Separe fatos observados, inferências, propostas e decisões aprovadas.

## 7. Procedure

1. Leia o artefato inteiro uma vez e delimite o escopo efetivamente auditado.
2. Faça uma passagem por cada classe: termo vago ou quantificador sem limite; termo não definido; ator ausente; referência ambígua; comportamento, caminho alternativo ou edge case não especificado; requisito incompleto; conflito entre fontes; e critério de aceite não verificável.
3. Compare termos, regras, identificadores, estados e contratos entre as fontes relacionadas. Código, issue ou implementação existente são evidências do estado, não decisões aprovadas automaticamente.
4. Para cada ambiguidade real, produza um finding com o formato da seção 8. Só registre finding quando houver pelo menos duas leituras plausíveis ou quando houver conflito/lacuna que impeça uma verificação ou decisão única.
5. Cite o trecho exato e sua localização. Explique as leituras plausíveis, as evidências que sustentam cada uma e a fonte potencialmente mais autoritativa quando essa precedência puder ser demonstrada.
6. Descreva o impacto e recomende a próxima ação: esclarecer o texto, obter evidência, atualizar a fonte de verdade, encaminhar a decisão ou revisar o contrato. Uma recomendação não é uma decisão aprovada.
7. Marque `Pending Decision` quando a resolução exigir escolha humana, especialmente em produto, requisito, arquitetura, tecnologia, escopo, política ou conflito sem precedência definida.
8. Apresente findings, não-findinges e limitações separadamente. Não reescreva nem corrija o artefato durante a auditoria, salvo autorização explícita para uma tarefa de edição posterior.

## 8. Expected output

Use um relatório com este formato consistente:

```markdown
## Ambiguity Report

Verdict: BLOCK | CONCERNS | CLEAN

| ID | Localização | Tipo | Estado |
|---|---|---|---|
| AMB-001 | <arquivo/seção/linha> | <classe> | Pending Decision |

### Findings

#### AMB-001
- **Localização:** <fonte e posição>
- **Trecho:** <citação literal>
- **Tipo de ambiguidade:** <classe>
- **Problema:** <por que há mais de uma leitura ou por que a verificação é impossível>
- **Interpretações possíveis:** <A>; <B>; <outras, se houver>
- **Evidências:** <fontes observadas para cada leitura>
- **Fonte potencialmente autoritativa:** <fonte e razão, ou não determinada>
- **Impacto:** <efeito em requisito, arquitetura, implementação, teste, contrato ou rastreabilidade>
- **Recomendação:** <próxima ação sem escolher silenciosamente>
- **Estado:** Proposed | Pending Decision | Not Currently Applicable
```

Cada ID deve ser único e estável dentro do relatório. `BLOCK` indica que uma interpretação divergente pode produzir resultado materialmente diferente ou que há conflito; `CONCERNS` indica ambiguidade relevante sem bloqueio demonstrado; `CLEAN` só pode ser usado após verificar as classes aplicáveis e registrar limitações inexistentes.

## 9. Constraints

Nunca:

- escolha a interpretação mais conveniente;
- transforme código, issue, proposta, recomendação ou inferência em requisito ou decisão aprovada;
- declare autoridade de uma fonte apenas por sua existência;
- reescreva o texto inventando limites, atores, valores, comportamentos, critérios ou tecnologia;
- trate silêncio como aprovação;
- confunda ausência de finding com prova de correção;
- substitua `requirements`, `grill-me`, `architecture`, `database-design`, `implementation`, `code-review` ou `project-governance`;
- reporte como conflito duas formulações que podem coexistir sem explicar a incompatibilidade;
- peça informação que possa ser obtida pela inspeção autorizada do repositório.

## 10. Human approval

O agente pode auditar, comparar fontes, reunir evidências, propor perguntas e recomendar uma forma de esclarecimento. Não pode aprovar requisito, decisão de produto, arquitetura, tecnologia, escopo ou resolução de conflito. Resoluções que dependam de escolha humana permanecem `Pending Decision` e seguem as fronteiras de `project-governance` e da skill de domínio competente. Esta skill permanece `proposed` até aprovação humana explícita.

## 11. Verification

- [ ] O artefato, versão e escopo auditados estão identificados.
- [ ] As fontes relacionadas e sua autoridade/estado foram verificadas quando acessíveis.
- [ ] Todas as classes de ambiguidade aplicáveis foram percorridas.
- [ ] Cada finding cita localização e trecho literal.
- [ ] Cada finding distingue duas ou mais interpretações plausíveis, conflito ou lacuna verificável.
- [ ] Evidências, autoridade potencial e limitações estão explícitas.
- [ ] Impacto e recomendação estão separados da decisão.
- [ ] Decisões humanas necessárias estão marcadas `Pending Decision`.
- [ ] Nenhuma alteração foi feita implicitamente no artefato auditado.

## 12. Interaction with other skills

- `project-governance` fornece autoridade, estados, evidência e aprovação; esta skill não os redefine.
- `requirements` recebe ambiguidades de requisitos, critérios de aceite e rastreabilidade; continua responsável por estruturá-los e manter a fonte de verdade.
- `grill-me` usa diálogo para explorar uma proposta ou decisão; esta skill primeiro audita o texto e as fontes para mostrar onde a interpretação diverge.
- `architecture` recebe ambiguidades cuja resolução altera uma decisão estrutural.
- `database-design` e `postgresql` recebem ambiguidades de modelo, constraints, queries ou dialeto.
- `implementation` recebe somente trabalho cujo comportamento e decisões estejam autorizados e suficientemente claros.
- `code-review` recebe inconsistências encontradas em código já alterado; esta skill não revisa o diff em seu lugar.
- `skill-authoring` governa o ciclo de vida desta skill.

## 13. Handling uncertainty and failures

Se uma fonte, trecho, glossário ou evidência não puder ser acessado, marque a parte como não verificada e não produza uma conclusão dependente dela. Se fontes conflitarem, cite ambas, preserve seus estados e encaminhe a resolução à autoridade apropriada. Se só uma interpretação for plausível, registre uma lacuna ou sugestão apenas quando houver consequência verificável; não crie um finding de estilo. Se o texto não permitir nenhuma avaliação útil, informe a entrada mínima necessária em vez de fabricar um relatório.
