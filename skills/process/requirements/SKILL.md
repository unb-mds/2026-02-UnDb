---
name: requirements
description: Estrutura, registra e mantém requisitos funcionais e não-funcionais rastreáveis até uma fonte autorizada, e mantém sincronizados os documentos derivados deles. Use ao escrever, alterar, numerar, revisar ou desambiguar requisitos, ao verificar se uma implementação tem requisito que a sustente, e ao propagar mudança de requisito para artefatos derivados.
metadata:
  project-version: "0.1.0"
  project-status: "proposed"
  project-category: "process"
  project-scope: "requirements-engineering"
  agent-agnostic: "true"
---

# Requirements

## 1. Objective

Garantir que todo requisito do projeto tenha identificador estável, origem verificável e
estado explícito, e que os documentos derivados dos requisitos permaneçam consistentes com
eles — sem que suposição, preferência técnica ou conveniência de implementação se tornem
requisito.

Esta skill é a fonte canônica de requisitos e critérios de aceite do projeto. Outras skills
consomem essas definições; não as redefinem.

## 2. Scope

Esta skill é responsável por:

- estruturar requisitos funcionais (`RF`) e não-funcionais (`RNF`) com identificador estável;
- relacionar cada requisito à sua fonte autorizada;
- distinguir fato observado, hipótese não validada, proposta e decisão vigente;
- identificar e eliminar ambiguidade em requisito já aceito;
- registrar restrições de produto que atravessam múltiplos requisitos;
- manter a matriz de rastreabilidade por release;
- manter documentos derivados sincronizados com a fonte de verdade;
- verificar se uma implementação, issue ou teste possui requisito que a sustente;
- registrar decisões pendentes que bloqueiam requisitos.

Esta skill **não** conduz pesquisa com usuário, não decide produto, não escolhe tecnologia,
não define arquitetura, não escreve ADR e não aprova requisito.

## 3. When to use

Use esta skill quando a tarefa envolver:

- escrever, alterar ou numerar um requisito;
- desambiguar um requisito antes de implementação;
- verificar se uma issue, teste ou mudança de código tem requisito que a sustente;
- propagar alteração de requisito para documentos derivados;
- registrar um requisito que emergiu durante outra atividade;
- avaliar se uma funcionalidade solicitada está dentro do escopo aprovado.

## 4. When not to use

Não use esta skill para:

- conduzir ou simular pesquisa com usuário;
- criar persona sem dado de origem;
- decidir escopo, prioridade ou release — isso pertence ao Product Owner;
- tomar ou registrar decisão arquitetural — pertence a `architecture`;
- escolher tecnologia — pertence à responsabilidade de tecnologia;
- implementar — pertence a `implementation`;
- criar ou executar testes — pertence a `testing`;
- aprovar requisito — ver seção 10.

Quando uma dessas responsabilidades surgir, faça o handoff em vez de absorvê-la.

## 5. Expected inputs

Use, conforme disponíveis:

1. saída de pesquisa com usuário, com indicação de método e amostra;
2. personas derivadas dessa pesquisa;
3. decisões de produto já tomadas pelo Product Owner;
4. requisitos existentes e seus identificadores;
5. restrições de produto já registradas;
6. decisões arquiteturais e tecnológicas vigentes, quando limitarem o requisito;
7. issues, código e testes existentes, como evidência do estado atual;
8. limites de escopo e aprovação definidos pela governança do projeto.

Código existente, issue existente ou teste existente **não são fonte de requisito**. São
evidência do que foi construído, não do que deveria ter sido.

## 6. Pre-conditions

Antes de escrever ou alterar um requisito:

1. identifique a fonte que o autoriza;
2. verifique se já existe requisito cobrindo a mesma necessidade;
3. verifique se a necessidade pertence de fato a requisito, e não a arquitetura,
   tecnologia ou detalhe de implementação;
4. identifique decisões pendentes que impeçam formulação não ambígua;
5. identifique quais documentos derivados serão afetados.

**Se não houver fonte autorizada, pare.** Um requisito sem origem não deve ser escrito, ainda
que pareça óbvio, útil ou tecnicamente necessário. Registre a lacuna e indique qual pesquisa,
decisão de produto ou informação é necessária para preenchê-la.

A pesquisa com usuário e a modelagem de personas são atividades humanas. Esta skill consome
seu resultado; não o produz nem o substitui.

## 7. Procedure

1. **Delimite a necessidade.** Determine o que precisa ser verdadeiro no sistema, do ponto
   de vista de quem usa, sem descrever como será construído.
2. **Localize a fonte.** Relacione a necessidade a pesquisa, decisão de produto, restrição
   externa ou requisito já aprovado. Registre a fonte.
3. **Classifique a informação.** Separe explicitamente fato observado, hipótese não validada,
   proposta e decisão vigente. Não promova uma categoria a outra.
4. **Verifique duplicação e conflito.** Compare com os requisitos existentes. Se houver
   sobreposição, prefira alterar o requisito existente a criar outro. Se houver conflito,
   exponha os dois em vez de escolher.
5. **Escreva de forma verificável.** Cada requisito deve permitir determinar sem discussão se
   foi atendido. Evite "rápido", "amigável", "seguro", "intuitivo" sem critério associado.
   Um requisito que não pode ser verificado ainda não é requisito.
6. **Atribua identificador estável.** `RF` para funcional, `RNF` para não-funcional,
   numeração sequencial. Identificador atribuído **nunca é reaproveitado**, mesmo que o
   requisito seja removido — a rastreabilidade histórica depende disso.
7. **Separe restrição de requisito.** Regra que atravessa vários requisitos e limita como
   qualquer um deles pode ser atendido pertence à seção de restrições, não a um `RF` isolado.
8. **Registre o estado.** Cada requisito e cada requisito não-funcional carrega estado:
   validado, proposto, bloqueado ou fora de escopo. Requisito não validado deve estar
   marcado como tal, inclusive quando parecer consensual.
9. **Atualize a rastreabilidade.** Mantenha a relação entre requisito, release e estado.
10. **Propague para os derivados.** Alteração de requisito exige revisão dos documentos
    derivados. Ver seção 8.
11. **Registre as pendências.** Decisão ausente que impeça formulação não ambígua deve ser
    registrada como pendente, com indicação do que ela bloqueia e de quem decide.

## 8. Expected output

A atividade produz, conforme aplicável:

- requisitos com identificador, texto verificável, origem e estado;
- restrições de produto, quando a regra atravessar requisitos;
- matriz de rastreabilidade atualizada;
- lista de decisões pendentes com o que cada uma bloqueia;
- documentos derivados atualizados ou a indicação explícita de que precisam ser;
- registro do que não pôde ser escrito por ausência de fonte.

### Hierarquia de documentos

O projeto mantém um documento de requisitos como **fonte de verdade** e documentos
**derivados** dele, orientados a públicos ou usos específicos.

Regras:

- mudança de requisito ocorre primeiro na fonte de verdade;
- o derivado é regenerado a partir dela, nunca editado isoladamente;
- todo derivado declara, no próprio arquivo, qual é sua fonte;
- se derivado e fonte divergirem, a fonte prevalece e o derivado é corrigido;
- um derivado **não pode conter decisão que a fonte não contenha**. Se durante a derivação
  surgir uma lacuna, ela é resolvida na fonte e depois propagada.

## 9. Constraints

Nunca:

- invente requisito, critério de aceite ou necessidade de usuário;
- crie ou complete persona sem dado de pesquisa;
- transforme código, issue ou teste existente em requisito por já existir;
- transforme hipótese não validada em fato;
- transforme proposta em requisito aprovado;
- escreva requisito não verificável;
- reaproveite identificador de requisito removido;
- resolva ambiguidade escolhendo silenciosamente uma interpretação;
- registre decisão arquitetural ou tecnológica como requisito;
- descreva solução técnica dentro do texto do requisito;
- altere escopo, prioridade ou release;
- edite documento derivado sem alterar a fonte;
- declare validado um requisito que não passou por validação.

## 10. Human approval

Esta skill pode redigir, estruturar, numerar, desambiguar, comparar, detectar conflito e
propor requisitos. **Não pode aprová-los.**

Siga `project-governance` para as fronteiras universais. Em particular, alterar requisito já
aprovado, tomar decisão de produto, remover funcionalidade e modificar escopo exigem
aprovação humana explícita.

Requisito redigido por um agente permanece **proposto** até validação humana. Ausência de
objeção, continuidade da conversa ou o fato de o texto já estar escrito não constituem
aprovação.

## 11. Verification

Antes de concluir:

- [ ] cada requisito possui identificador estável e único;
- [ ] cada requisito é verificável sem discussão de interpretação;
- [ ] cada requisito possui fonte identificada, ou a ausência está registrada;
- [ ] hipóteses não validadas estão marcadas como tal;
- [ ] requisitos não validados não estão apresentados como validados;
- [ ] nenhum requisito descreve solução técnica;
- [ ] restrições transversais não foram embutidas em requisito isolado;
- [ ] nenhum identificador foi reaproveitado;
- [ ] conflitos foram expostos, não resolvidos por escolha própria;
- [ ] a matriz de rastreabilidade reflete o estado atual;
- [ ] documentos derivados foram atualizados ou marcados como desatualizados;
- [ ] decisões pendentes estão explícitas, com o que bloqueiam.

## 12. Interaction with other skills

- **`project-governance`**: fonte das regras de autoridade, evidência, escopo e aprovação.
  Esta skill as aplica sem duplicá-las.
- **`architecture`**: consome requisitos; não os define. Requisito diz o que o sistema faz;
  arquitetura diz como. ADR pertence a `architecture`, ainda que cite requisitos.
- **`implementation`**: consome requisitos e critérios de aceite. Necessidade de novo
  requisito descoberta durante implementação retorna para cá.
- **`testing`**: usa requisitos como fonte do comportamento esperado. Teste existente não é
  requisito.
- **`code-review`**: avalia mudanças contra requisitos autorizados. Divergência entre código
  e requisito retorna para cá quando o requisito estiver ambíguo.
- **`technology-guidelines`**: escolha de tecnologia não é requisito. Um requisito pode
  restringir tecnologia, mas não a seleciona.
- **Skills de processo e GitHub**: governam issues, branches e Pull Requests. Esta skill
  fornece o requisito que uma issue referencia; não define o fluxo operacional.
- **`skill-authoring`**: governa mudanças estruturais nesta skill.

## 13. Handling uncertainty and failures

Quando faltar informação:

1. identifique exatamente qual dado, decisão ou fonte está ausente;
2. determine se a lacuna bloqueia todo o requisito ou apenas parte;
3. escreva somente a parte sustentada por fonte;
4. registre o restante como pendente, indicando quem decide;
5. não preencha a lacuna com valor padrão, inferência ou prática comum de mercado.

Quando um requisito for ambíguo:

1. liste as interpretações possíveis;
2. indique a consequência de cada uma na implementação;
3. não escolha por conveniência;
4. encaminhe a decisão a quem tem autoridade sobre ela.

Quando fontes conflitarem, identifique ambas e o ponto de conflito, aplique precedência
apenas se estiver oficialmente definida, e interrompa somente a parte afetada.

Quando um requisito for removido, registre o motivo e preserve o identificador como retirado.
Não renumere os demais.
