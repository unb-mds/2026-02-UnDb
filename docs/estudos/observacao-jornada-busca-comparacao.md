# Observação da jornada de busca, comparação e avaliação com alunos

## 1. Contexto e objetivo

Este documento registra o **protocolo de observação, o diagnóstico preliminar e o mapeamento de hipóteses** da jornada de uso do UnDb após a Release 1.0.0, com foco nas etapas de busca, consulta, comparação e avaliação.

O objetivo da [Issue #148](https://github.com/unb-mds/2026-02-UnDb/issues/148) é identificar pontos concretos de confusão na navegação do produto relatados após a Release 1, estruturar as tarefas e telas investigadas, priorizar os obstáculos e relacioná-los aos requisitos aprovados (`docs/requisitos.md`), estabelecendo a base para as intervenções de interface do épico [#144](https://github.com/unb-mds/2026-02-UnDb/issues/144) e para a validação empírica com alunos na Sprint 06 ([Issue #153](https://github.com/unb-mds/2026-02-UnDb/issues/153)).

Em estrito cumprimento às diretrizes de governança do projeto (`skills/governance/project-governance/SKILL.md` e `AGENTS.md`):
- **Não são inventados resultados, participantes ou métricas presumidas.**
- As hipóteses preliminares e o diagnóstico derivado do feedback da apresentação da Release 1 são mantidos explicitamente separados de resultados empíricos coletados em campo.
- Os critérios que dependem da execução física das sessões com estudantes permanecem registrados como pendências abertas.

---

## 2. Fonte de dados e diagnóstico da Release 1

### 2.1 Apresentação presencial da Release 1 (24/09/2026)

A fonte inicial que motivou a abertura do épico #144 e da issue #148 foi o feedback recebido durante a demonstração presencial da Release 1.0.0, realizada em 24/09/2026 com docentes e discentes da disciplina de Métodos de Desenvolvimento de Software.

Durante a interação com o produto demonstrado localmente, foram apontados os seguintes pontos críticos de hesitação e atrito:

1. **Ambiguidade na entrada da busca:** A tela inicial exigia que o aluno escolhesse antecipadamente se desejava buscar professor ou disciplina, gerando confusão em casos onde o estudante só lembrava parte do nome ou o código da matéria (ex.: módulo livre).
2. **Separação entre consulta pública e avaliação autenticada:** Usuários questionaram se era necessário efetuar login para apenas consultar e comparar professores, revelando falta de clareza visual de que a navegação é totalmente pública e anônima.
3. **Interpretação do estado vazio (zero avaliações):** A ausência de avaliações em um professor/disciplina gerou a impressão de avaliação negativa ou nota zero, por falta de mensagem contextual encorajadora.
4. **Compreensão dos estados insuficiente e conflitante:**
   - O limiar de 3 avaliações (RF08) para proteção da identidade do avaliador não era compreendido imediatamente, deixando dúvidas sobre por que notas parciais não apareciam.
   - O rótulo "Conflitante" em critérios factuais (chamada e material) gerava estranheza sem uma explicação textual de apoio.
5. **Legibilidade da comparação lado a lado:** A visualização comparativa de múltiplos docentes em telas menores (smartphones) empilhava os cartões, prejudicando a leitura comparativa simultânea.
6. **Percepção de critérios neutros:** O critério "Dificuldade" e o critério "Faz chamada" foram por vezes interpretados precipitadamente como aspectos negativos, quando na verdade são indicadores factuais neutros (RF14, RF15).

### 2.2 Base normativa de requisitos

Os pontos de atenção foram confrontados com os requisitos funcionais vigentes em [`docs/requisitos.md`](../requisitos.md):
- **RF01 e RF02:** Acesso e autenticação com e-mail institucional `@aluno.unb.br`.
- **RF04:** Consulta pública sem exigência de login.
- **RF05 a RF07:** Mecanismos de busca por professor, disciplina e código.
- **RF08 e RF09:** Agregação de critérios com mínimo de 3 avaliações para exibição pública.
- **RF10 e RF11:** Tratamento explícito de estados especiais (sem avaliações, dados insuficientes e conflitante).
- **RF12 e RF13:** Comparação entre professores da mesma disciplina e ordenação por índice de recomendação.
- **RF14 e RF15:** Formulário estruturado de avaliação e apresentação neutra de critérios.

---

## 3. Escopo da observação

### 3.1 Tarefas investigadas

O protocolo cobre 6 tarefas principais que compõem o fluxo essencial do estudante:

| ID | Tarefa | Objetivo do Usuário | Tela / Componente |
|---|---|---|---|
| **T1** | Buscar professor | Localizar um docente por nome ou parte do nome | `/professores` |
| **T2** | Buscar disciplina | Localizar matéria por código (ex.: MAT0025) ou nome (ex.: Cálculo 1) | `/disciplinas` |
| **T3** | Consulta pública | Acessar informações agregadas e confirmar que não exige login | `/`, `/professores/[id]`, `/disciplinas/[id]` |
| **T4** | Comparar professores | Visualizar docentes de uma mesma disciplina e interpretar a recomendação | `/disciplinas/[id]` |
| **T5** | Interpretar estados especiais | Identificar se a turma está sem avaliação, com dados insuficientes (< 3) ou com divergência de relatos | `/professores/[id]/disciplinas/[disciplinaId]` |
| **T6** | Avaliar professor | Preencher os 5 critérios estruturados e compreender o fluxo de autenticação | `/professores/[id]/disciplinas/[disciplinaId]/avaliar` |

### 3.2 Perfis de participantes-alvo

Em conformidade com a modelagem de personas de [`docs/requisitos.md`](../requisitos.md):

- **P1 — Aluno sem rede de contatos:** Estudante de 2º ou 3º semestre, introvertido ou cursando disciplina de módulo livre fora de seu instituto. Não possui referências prévias de turmas e depende exclusivamente da clareza da busca e da comparação no site para decidir matrícula.
- **P2 — Aluno veterano:** Estudante de 5º semestre em diante, com repertório acadêmico consolidado. Atua tanto na consulta crítica quanto na alimentação das avaliações estruturadas.

### 3.3 Princípios éticos e privacidade na coleta

- Nenhum dado pessoal identificável (nome completo, matrícula ou e-mail real) será registrado no repositório.
- Participantes de sessões reais serão identificados apenas por códigos internos padronizados: `ALUNO-01`, `ALUNO-02`, etc., acompanhados de perfil (`P1` ou `P2`) e semestre relativo.
- As tarefas devem ser instruídas de forma neutra, sem antecipar termos técnicos da interface.

---

## 4. Protocolo de registro de observações de campo

Para aplicação nas sessões de teste com alunos, o facilitador deve preencher a seguinte matriz estruturada:

| Campo | Descrição e formato esperado |
|---|---|
| **Identificador** | Código anônimo do participante (ex.: `ALUNO-01`). |
| **Perfil** | `P1` ou `P2`, com indicação de semestre aproximado. |
| **Tarefa** | `T1`, `T2`, `T3`, `T4`, `T5` ou `T6`. |
| **Resultado** | Concluída com autonomia / Concluída com hesitação / Não concluída. |
| **Dificuldade observada** | Descrição fática da hesitação, clique incorreto, dúvida verbalizada ou erro. |
| **Tela / Componente** | URL ou elemento visual onde o atrito ocorreu. |
| **Impacto** | **Alto** (bloqueia conclusão), **Médio** (gera confusão mas permite contorno), **Baixo** (estético/microcopy). |
| **Requisito associado** | RF correspondente em `docs/requisitos.md`. |

---

## 5. Diagnóstico preliminar e priorização de obstáculos

As dificuldades identificadas no feedback da Release 1 foram analisadas contra os requisitos e categorizadas pelo seu potencial de impacto na jornada de decisão de matrícula:

| Obstáculo identificado | Hipótese de dificuldade / Comportamento observado | Tela principal | Requisito | Severidade de impacto | Frequência preliminar |
|---|---|---|---|---|---|
| **1. Ambiguidade na busca inicial** | Aluno não sabe de antemão se deve clicar em "Professores" ou "Disciplinas", especialmente em módulo livre | `/` | RF05, RF06, RF07 | **Alta** (bloqueia o ponto de partida) | Frequente no feedback da R1 |
| **2. Interpretação do estado vazio** | Ausência de avaliações é lida erroneamente como professor ruim ou reprovado pela comunidade | `/professores/[id]/disciplinas/[disciplinaId]` | RF10 | **Alta** (distorce a tomada de decisão) | Relatado no feedback da R1 |
| **3. Incompreensão do limiar de anonimato (< 3 avaliações)** | Aluno não entende por que um professor com 1 ou 2 avaliações não exibe médias numéricas | `/professores/[id]/disciplinas/[disciplinaId]` | RF08, RF09 | **Alta** (baixa percepção de confiabilidade) | Relatado no feedback da R1 |
| **4. Dificuldade no estado conflitante** | Usuário estranha ver o rótulo "Conflitante" em chamada/material sem explicação contextual | `/professores/[id]/disciplinas/[disciplinaId]` | RF11 | **Alta** (gera dúvida na escolha) | Observado na demonstração |
| **5. Comparação em telas compactas (mobile)** | Cartões empilhados verticalmente dificultam a confrontação direta de métricas lado a lado | `/disciplinas/[id]` | RF12, RF13 | **Alta** (compromete o uso no smartphone) | Identificado na inspeção de UX |
| **6. Percepção da barreira de autenticação** | Dúvida se a consulta exige login institucional `@aluno.unb.br` | `/`, `/professores`, `/disciplinas` | RF04, RF14 | **Média** (gera atrito desnecessário) | Relatado no feedback da R1 |
| **7. Neutralidade dos critérios factuais** | Dificuldade alta e presença de chamada são confundidas com atributos negativos de mérito | `/avaliar`, `/professores/[id]/...` | RF14, RF15 | **Média** (avaliação enviesada) | Observado na demonstração |

### Justificativa da priorização preliminar:

- **Prioridade Alta:** Obstáculos que impedem a descoberta (busca inicial), transmitem conclusões falsas sobre professores (estado vazio interpretado como nota zero) ou inviabilizam a escolha informada da turma no período de matrícula.
- **Prioridade Média:** Questões que geram fricção ou hesitação no usuário, mas não bloqueiam a conclusão do fluxo principal quando superadas.
- **Prioridade Baixa:** Refinamentos puramente cosméticos e de microcopy secundário sem impacto na navegação.

> ℹ️ **Nota sobre calibração de frequência:** A frequência definitiva de cada obstáculo será consolidada empiricamente na matriz após a realização das sessões de observação com estudantes na Sprint 06.

---

## 6. Rastreabilidade com telas e requisitos de produto

| Tela / Rota do Frontend | Elemento observado | Dificuldade relacionada | Requisitos vigentes |
|---|---|---|---|
| `/` (Início) | Cards separados de Professor e Disciplina | Exige decisão prévia sobre a modalidade de busca | RF05, RF06 |
| `/professores` | Campo de busca textual | Falta de busca unificada e feedback dinâmico de termos parciais | RF05 |
| `/disciplinas` | Campo de busca por código/nome | Código de disciplina requer digitação exata ou padrão específico | RF06, RF07 |
| `/disciplinas/[id]` | Lista comparativa de professores | Visualização lado a lado perde legibilidade em telas compactas; ordenação estrita por % de recomendação | RF12, RF13 |
| `/professores/[id]/disciplinas/[disciplinaId]` | Painel de métricas agregadas | Diferenciação entre "sem avaliações", "dados insuficientes" e "conflitante" | RF08, RF09, RF10, RF11 |
| `/professores/[id]/disciplinas/[disciplinaId]/avaliar` | Formulário estruturado | Clareza da exigência de e-mail institucional e preservação de neutralidade | RF01, RF02, RF14, RF15 |

---

## 7. Status dos critérios da Issue #148 e pendências

Acompanhamento dos critérios de conclusão estabelecidos na [Issue #148](https://github.com/unb-mds/2026-02-UnDb/issues/148):

- [ ] **Registrar tarefas observadas, participantes e dificuldades sem inventar resultados:**
  - *Diagnóstico e protocolo estruturados:* As 6 tarefas essenciais, as 2 personas de referência (P1 e P2), a matriz de coleta padronizada e as dificuldades preliminares mapeadas no feedback da Release 1 estão devidamente registrados neste documento.
  - *Pendência aberta:* A execução física das sessões de campo com alunos reais das turmas da UnB e o preenchimento da matriz com dados empíricos estão programados para a **Sprint 06**, em articulação com o roteiro de testes da [Issue #153](https://github.com/unb-mds/2026-02-UnDb/issues/153). Em respeito às regras de governança, o critério é mantido aberto até a realização efetiva dos testes.

- [ ] **Priorizar os obstáculos pela frequência e impacto observados:**
  - *Diagnóstico e priorização preliminar:* Os 7 obstáculos identificados na Release 1 foram priorizados em Alta e Média severidade com base no seu impacto funcional na jornada crítica de matrícula.
  - *Pendência aberta:* A validação estatística da frequência observada em campo depende da conclusão das sessões com estudantes na Sprint 06. O critério permanece aberto até a consolidação desses dados.

- [ ] **Relacionar achados às telas e aos requisitos existentes:**
  - *Rastreabilidade documentada:* Cada obstáculo identificado foi explicitamente mapeado às telas do frontend e aos requisitos RF01–RF15 em `docs/requisitos.md`.
  - *Pendência aberta:* A confirmação final da aderência dos requisitos frente às dificuldades reais relatadas pelos estudantes será reavaliada após as sessões empíricas da Sprint 06.

---

## 8. Próximos passos e articulação com a Release 2

1. **Prototipação de soluções UX ([Issue #152](https://github.com/unb-mds/2026-02-UnDb/issues/152)):** Elaboração dos protótipos de alta fidelidade abordando busca unificada, cards comparativos responsivos e microcopy contextual para estados especiais.
2. **Execução das sessões de teste com alunos ([Issue #153](https://github.com/unb-mds/2026-02-UnDb/issues/153)):** Aplicação do protocolo estabelecido neste documento durante a Sprint 06 com discentes voluntários dos perfis P1 e P2.
3. **Implementação de melhorias de interface ([Issues #155, #157 e #158](https://github.com/unb-mds/2026-02-UnDb/issues/144)):** Refinamento da navegação, resultados, comparação e formulário de avaliação no frontend conforme as evidências de validação.

---

## 9. Referências

- [Issue #148 — [R2][UX] Observar a jornada de busca, comparação e avaliação com alunos](https://github.com/unb-mds/2026-02-UnDb/issues/148)
- [Issue #152 — [R2][UX] Prototipar tela inicial, busca, resultados, comparação e formulário](https://github.com/unb-mds/2026-02-UnDb/issues/152)
- [Issue #153 — [R2][UX] Validar protótipo da jornada com alunos](https://github.com/unb-mds/2026-02-UnDb/issues/153)
- [Épico #144 — [EPIC][R2] Melhorar a jornada do aluno na aplicação](https://github.com/unb-mds/2026-02-UnDb/issues/144)
- [`docs/requisitos.md`](../requisitos.md) — Fonte autorizada de requisitos do UnDb
- [`docs/visao.md`](../visao.md) — Documento de visão do produto
