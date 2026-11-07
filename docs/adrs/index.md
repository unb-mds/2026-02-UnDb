# Registros de decisão técnica (ADRs)

Um ADR registra o problema, as alternativas, a escolha e suas consequências em um
momento do projeto. Ele permite compreender por que uma decisão foi proposta ou
aprovada. Regras gerais de programação e instruções reutilizáveis para agentes
continuam nas [skills canônicas](https://github.com/unb-mds/2026-02-UnDb/tree/develop/skills);
requisitos de produto continuam em [Requisitos](../requisitos.md).

Este guia e o [template versionado](template.md) atendem à
[issue #188](https://github.com/unb-mds/2026-02-UnDb/issues/188). Eles organizam o
registro documental sem criar novos gates de aprovação ou alterar a governança.

## Catálogo e histórico preservado

Os ADRs 01–08 permanecem em [Arquitetura](../arquitetura.md#7-decisoes-arquiteturais-adrs),
com seus identificadores, títulos, conteúdo e âncoras originais. Não é necessário
migrar ou completar retroativamente esses registros para usar o novo template.

| ADR | Registro | Estado e evidência já documentados |
|---|---|---|
| 01 | [SQLAlchemy + Alembic](../arquitetura.md#adr-01-sqlalchemy-alembic-como-orm-e-ferramenta-de-migracao) | Aprovado na revisão do [PR #55](https://github.com/unb-mds/2026-02-UnDb/pull/55), em 11/09/2026 |
| 02 | [Next.js e Tailwind CSS](../arquitetura.md#adr-02-nextjs-e-tailwind-css-no-frontend) | Aprovado por Nicolas e Vinicius em 13/09/2026; referência: [#28](https://github.com/unb-mds/2026-02-UnDb/issues/28) |
| 03 | [E-mail institucional confirmado](../arquitetura.md#adr-03-identificacao-por-e-mail-institucional-confirmado) | Validado pelo grupo para a Release 1 em 09/09/2026; complemento aprovado em 19/09/2026, conforme o próprio registro |
| 04 | [Critérios de fato e opinião](../arquitetura.md#adr-04-separacao-entre-criterios-de-fato-e-de-opiniao-no-modelo) | Proposta arquitetural, conforme o resumo de Arquitetura; sem promoção pela aprovação de requisitos |
| 05 | [Ordenação por recomendação](../arquitetura.md#adr-05-ordenacao-exclusivamente-pelo-percentual-de-recomendacao) | Proposta arquitetural, conforme o resumo de Arquitetura |
| 06 | [Ausência de verificação de matrícula](../arquitetura.md#adr-06-ausencia-de-verificacao-de-matricula-assumida-explicitamente) | Proposta arquitetural, conforme o resumo de Arquitetura |
| 07 | [Identidade e sincronização do SIGAA](../arquitetura.md#adr-07-identidade-institucional-e-sincronizacao-do-sigaa) | Seção individual registra aprovação em 17/09/2026 para a [#25](https://github.com/unb-mds/2026-02-UnDb/issues/25); ver divergência abaixo |
| 08 | [Execução e containerização do frontend](../arquitetura.md#adr-08-execucao-e-containerizacao-do-frontend) | Seção individual registra aprovação em 19/09/2026 para a [#36](https://github.com/unb-mds/2026-02-UnDb/issues/36); ver divergência abaixo |
| 09 | [Estratégia de qualidade](09-estrategia-qualidade.md) | `Proposed`: registro preparado na #188; distingue escopo solicitado, configuração observada e decisões pendentes |

!!! warning "Divergência documental preexistente — Pending Decision"

    O resumo inicial de Arquitetura enumera apenas os ADRs 01–03 como aprovados e
    chama os demais de propostas; as seções dos ADRs 07 e 08 registram aprovações
    posteriores. Este catálogo expõe ambos os registros sem resolver o conflito por
    suposição. A reconciliação do resumo depende de confirmação humana das fontes;
    nenhum estado original foi alterado nesta padronização.

## Criar um registro

1. Localize a issue, os requisitos e as decisões que sustentam o trabalho. Verifique
   se já existe um ADR sobre o mesmo problema e qual é seu estado.
2. Copie o [template](template.md) para `docs/adrs/NN-descricao.md`, usando o próximo
   número livre do catálogo. Não reutilize nem renumere identificadores antigos.
3. Preencha contexto, alternativas, decisão **proposta**, justificativa, consequências,
   data de preparação e fontes. Use `Proposed` enquanto não houver aprovação
   explícita. Datas e referências desconhecidas ficam como não registradas.
4. Acrescente o registro a este catálogo e ao `nav` de `mkdocs.yml`. Relacione a issue
   e os ADRs afetados, mantendo as referências anteriores acessíveis.

## Revisar e registrar aprovação

- Confira o vínculo entre contexto, alternativas e justificativa. Separe configuração
  observada, escopo autorizado, implementação futura e decisão pendente.
- Use o vocabulário canônico: `Defined` (aprovado e autoritativo), `Proposed`
  (preparado, ainda não autoritativo), `Pending Decision` (exige decisão humana) e
  `Not Currently Applicable` (conhecido, desnecessário no momento). A fonte é
  [skill-authoring](https://github.com/unb-mds/2026-02-UnDb/blob/develop/skills/governance/skill-authoring/SKILL.md).
  Preserve também as qualificações históricas, como aprovação apenas para uma release.
- Registre responsável, data, alcance e referência verificável da aprovação humana
  antes de marcar uma decisão como `Defined`. Preparar o arquivo, implementar código
  ou aprovar requisitos relacionados não aprova automaticamente um ADR.
- Siga os [limites de aprovação humana](https://github.com/unb-mds/2026-02-UnDb/blob/develop/skills/governance/project-governance/references/HUMAN_APPROVAL_BOUNDARIES.md).
  O mecanismo operacional exato de registro da aprovação no GitHub continua
  `Pending Decision`; este guia não o substitui por um rito novo.
- Antes da entrega, execute, na raiz, `python -m pip install -r requirements-docs.txt`
  e `python -m mkdocs build --strict --site-dir site`. Confira links e âncoras e
  registre comandos, base, resultados e limitações. O fluxo de contribuição permanece
  no [CONTRIBUTING.md](https://github.com/unb-mds/2026-02-UnDb/blob/develop/CONTRIBUTING.md).

## Atualizar ou substituir sem apagar o histórico

Correções editoriais e novas evidências podem ser acrescentadas ao mesmo ADR,
preservando o sentido da decisão e registrando a alteração relevante no histórico.
Se a escolha técnica mudar, prepare outro ADR com contexto e alternativas atuais e
referencie o anterior em **Substitui**. Enquanto a nova decisão estiver proposta, a
anterior conserva seu alcance e estado; não marque a substituição como efetiva.

Após a aprovação explícita da substituição, acrescente no registro anterior a ligação
**Substituído por**, com data e evidência, e atualize o catálogo. Preserve o texto,
a aprovação original e o identificador anterior. A relação de substituição documenta
a evolução; não elimina a evidência histórica nem dispensa aprovação de arquitetura.
