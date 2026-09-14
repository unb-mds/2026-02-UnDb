---
name: database-design
description: Projeta, revisa e valida modelos de dados relacionais a partir de requisitos autorizados. Use antes ou durante mudanças de schema para verificar entidades, relacionamentos, integridade, normalização e índices, sem substituir requisitos, arquitetura ou implementação.
metadata:
  project-version: "0.1.0"
  project-status: "proposed"
  project-category: "technology"
  project-scope: "relational-data-modeling"
  agent-agnostic: "true"
---

# Database Design

## 1. Objective

Projetar, revisar e validar o modelo conceitual e lógico relacional do G7 a partir de requisitos autorizados, para que o schema preserve integridade e represente o domínio antes ou durante sua implementação.

## 2. Scope

Esta skill identifica entidades, atributos, relacionamentos, cardinalidades, chaves, dependências funcionais, constraints, normalização, redundâncias, riscos de inconsistência e índices justificados por consultas conhecidas. Ela compara o modelo conceitual com os mapeamentos SQLAlchemy e o banco quando estiverem disponíveis. Não define requisitos, escolhe tecnologia estrutural, implementa migrations, altera o schema aprovado nem resolve regras de negócio não definidas.

## 3. When to use

Use ao criar, revisar ou validar um modelo relacional; antes de uma migration; ao detectar duplicidade, dados órfãos, inconsistência ou divergência entre documentação, modelo, SQLAlchemy e banco; ou ao avaliar uma mudança autorizada que afete persistência.

## 4. When not to use

- Use `requirements` para definir ou esclarecer comportamento e critérios de aceite.
- Use `architecture` para decisões estruturais de maior nível ou para mudança que exija decisão arquitetural.
- Use `implementation` para codificar um modelo já autorizado, incluindo repository, service, models e migration.
- Uma futura `postgresql` deve tratar recursos e boas práticas específicos do PostgreSQL; esta skill não a substitui.

## 5. Expected inputs

Use somente o que estiver disponível e autorizado: requisitos, critérios de aceite, Issues ou decisões aprovadas; documentação de domínio e arquitetura; consultas, filtros, ordenações e fluxos de escrita conhecidos; modelo, migrations, schema e mapeamentos SQLAlchemy; restrições de stack e governança.

No estado observado do G7, PostgreSQL, SQLAlchemy síncrono, Alembic e psycopg2 são a stack presente no backend. Não a substitua nem a promova como decisão normativa sem fonte autorizada; registre qualquer conflito documental.

## 6. Pre-conditions

1. Identifique fontes e estados: `Defined`, `Proposed`, `Pending Decision` ou `Not Currently Applicable`.
2. Delimite a questão e inspecione schema/modelos relevantes.
3. Separe requisitos, fatos observados, inferências e propostas.
4. Se uma regra necessária não estiver definida, mantenha-a como `Pending Decision`.

## 7. Procedure

1. Parta dos requisitos autorizados e registre cada fonte; não derive regra de produto de nomes de colunas ou código existente.
2. Identifique entidades, atributos e relacionamentos. Declare cardinalidade e participação; represente N:N por tabela associativa quando necessário.
3. Determine PKs, chaves candidatas, FKs e dependências funcionais relevantes. Defina tipos no nível lógico sem converter conveniência do ORM em regra de domínio.
4. Traduza regras estruturais para `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL`, `CHECK`, `DEFAULT` e constraints compostas quando o banco puder garanti-las. Defina ações de referência somente quando autorizadas.
5. Normalize primeiro: avalie 1FN, 2FN, 3FN, dependências, redundância e anomalias. Desnormalize somente com razão concreta e verificável, consulta/medição que a justifique, risco explícito e estratégia de manutenção. Leia [normalização](references/normalization.md).
6. Derive índices de consultas, joins, filtros e ordenações conhecidos; não crie índice por hábito ou hipótese. Leia [índices](references/indexing.md).
7. Verifique a rastreabilidade requisito → modelo → SQLAlchemy → migration → banco. Relate divergências sem escolher a fonte correta.
8. Faça handoff: ambiguidade para `requirements`; decisão estrutural para `architecture`; mudança autorizada para `implementation`; particularidade PostgreSQL para futura `postgresql`.

Leia [workflow de modelagem](references/modeling-workflow.md) para roteiro e saída e [constraints](references/constraints.md) quando uma regra de integridade estiver em discussão.

## 8. Expected output

Produza: requisitos usados; entidades, atributos, relacionamentos e cardinalidades; chaves e constraints; análise de normalização, redundância e riscos; índices justificados; conflitos e decisões pendentes; impacto em SQLAlchemy e migration; testes de integridade; e comparação entre modelo conceitual, documentação, código e schema quando acessíveis.

## 9. Constraints

Nunca invente requisito, cardinalidade, política de exclusão, tipo, default ou regra de negócio; altere unilateralmente modelo aprovado, arquitetura, banco, ORM ou SGBD; trate código, migration, Issue, PR ou documentação isoladamente como especificação automática; transforme proposta em `Defined`; recomende desnormalização prematura por “performance”; ou deixe integridade importante exclusivamente no código quando o banco puder garanti-la.

## 10. Human approval

O agente pode analisar, comparar e preparar proposta marcada como `Proposed`. Nova regra de domínio, mudança material de modelo, desnormalização, política de referência, mudança de stack ou resolução de conflito permanece `Pending Decision` até aprovação humana. Só após autorização `implementation` pode alterar SQLAlchemy, migrations ou banco.

## 11. Verification

- [ ] Cada entidade, atributo e relacionamento tem fonte ou está pendente.
- [ ] Cardinalidades, chaves e dependências funcionais foram verificadas.
- [ ] Regras importantes têm garantia estrutural quando possível.
- [ ] 1FN, 2FN, 3FN, redundância e anomalias foram consideradas.
- [ ] Índices correspondem a consultas conhecidas ou constraints, não a suposição.
- [ ] Modelo, SQLAlchemy, migration, banco e documentação foram comparados quando acessíveis.
- [ ] Conflitos e pendências não foram resolvidos silenciosamente.
- [ ] Há testes de integridade necessários para mudança autorizada.

## 12. Interaction with other skills

`project-governance` define autoridade e estados; `skill-authoring` governa esta skill. `requirements` fornece regras e critérios autorizados; `architecture` recebe decisões estruturais maiores; `implementation` executa o modelo autorizado; `testing` verifica a implementação. Esta skill não substitui futura `postgresql`, responsável por dialeto, recursos e operação específicos.

## 13. Handling uncertainty and failures

Se faltar fonte, consulta ou regra, registre a lacuna e continue somente o que for sustentado. Se requisito, documentação, código, modelo, Issue ou PR divergirem, cite fontes e conflito; não eleja uma como correta. Marque a resolução como `Pending Decision` e encaminhe-a. Se banco, migration ou modelos não forem acessíveis, limite a validação ao artefato inspecionado.

## 14. Example: Avaliação

Para o requisito autorizado de unicidade por `(usuario_id, professor_id, disciplina_id)` e reenvio válido que substitui o anterior, proponha `UNIQUE (usuario_id, professor_id, disciplina_id)` e FKs para as três entidades. A constraint evita duplicação sob concorrência, mas não implementa substituição: repository/service devem localizar e atualizar a linha existente (ou usar upsert autorizado); a migration deve criar a constraint e tratar duplicatas existentes; testes devem cobrir inserção, reenvio, violação de unicidade e integridade referencial. Não deduza outros campos ou regras de avaliação.
