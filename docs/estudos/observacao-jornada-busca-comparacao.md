# Observação da jornada de busca, comparação e avaliação com alunos

## 1. Contexto e objetivo

Este documento registra o **protocolo de observação, o diagnóstico preliminar e a consolidação de dois relatos de uso** da jornada do UnDb após a Release 1.0.0, com foco nas etapas de busca, consulta, comparação e avaliação. O diagnóstico da apresentação da Release 1 permanece histórico nas seções 2–6; a evidência recebida de Nicolas e a avaliação dos critérios da #148 estão na seção 7.

O objetivo da [Issue #148](https://github.com/unb-mds/2026-02-UnDb/issues/148) é identificar pontos concretos de confusão na navegação do produto relatados após a Release 1, estruturar as tarefas e telas investigadas, priorizar os obstáculos e relacioná-los aos requisitos aprovados (`docs/requisitos.md`), estabelecendo a base para as intervenções de interface do épico [#144](https://github.com/unb-mds/2026-02-UnDb/issues/144) e para a validação empírica com alunos na Sprint 06 ([Issue #153](https://github.com/unb-mds/2026-02-UnDb/issues/153)).

Em estrito cumprimento às diretrizes de governança do projeto (`skills/governance/project-governance/SKILL.md` e `AGENTS.md`):
- **Não são inventados resultados, participantes ou métricas presumidas.**
- As hipóteses preliminares e o diagnóstico derivado do feedback da apresentação da Release 1 são mantidos explicitamente separados de resultados empíricos coletados em campo.
- A entrega inicial era parcial. Com os relatos de `ALUNO-01` e `ALUNO-02`, a observação exploratória e sua consolidação estão documentadas para revisão e aceite da [Issue #148](https://github.com/unb-mds/2026-02-UnDb/issues/148). Isso não representa validação do protótipo, implementação das melhorias ou conclusão da #153.

---

## 2. Fonte de dados e diagnóstico da Release 1

### 2.1 Apresentação presencial da Release 1 (24/09/2026)

A motivação inicial para a abertura do [Épico #144](https://github.com/unb-mds/2026-02-UnDb/issues/144) e da [Issue #148](https://github.com/unb-mds/2026-02-UnDb/issues/148) decorre dos apontamentos colhidos durante a demonstração presencial da Release 1.0.0, realizada em 24/09/2026 com docentes e discentes da disciplina de Métodos de Desenvolvimento de Software (contextualizada operacionalmente em [`docs/releases/1.0.0.md`](../releases/1.0.0.md#operacao-local-da-demonstracao)).

> ⚠️ **Limitação metodológica e rastreabilidade da fonte:**
> Os apontamentos a seguir originaram-se de manifestações orais e observações informais registradas pela equipe durante a dinâmica de apresentação local da versão 1.0.0. Eles **não constituem registros de sessões formais de teste de usabilidade** com matriz preenchida por participante. Por essa razão, conforme `skills/governance/project-governance/SKILL.md`, essas impressões são catalogadas estritamente como **hipóteses e diagnóstico preliminar**, que orientam a investigação, mas não substituem os registros de observação empírica de campo exigidos para a conclusão integral da Issue #148.

Durante a interação com o produto demonstrado localmente, foram apontados os seguintes pontos críticos de hesitação e atrito:

1. **Ambiguidade na entrada da busca:** A tela inicial exigia que o aluno escolhesse antecipadamente se desejava buscar professor ou disciplina, gerando confusão em casos onde o estudante só lembrava parte do nome ou o código da matéria (ex.: módulo livre).
2. **Separação entre consulta pública e avaliação autenticada:** Usuários questionaram se era necessário efetuar login para apenas consultar e comparar professores, revelando falta de clareza visual de que a navegação é totalmente pública e anônima (RF04).
3. **Interpretação do estado vazio (zero avaliações):** A ausência de avaliações em um professor/disciplina gerou a impressão de avaliação negativa ou nota zero, por falta de mensagem contextual encorajadora (RF10).
4. **Compreensão dos estados insuficiente e conflitante:**
   - O limiar de 3 avaliações para proteção contra identificação indireta (RNF02), aliado à regra de exibição agregada (RF08) e transparência estatística da contagem (RF09), não era compreendido imediatamente, deixando dúvidas sobre por que notas parciais não apareciam.
   - O rótulo "Conflitante" em critérios factuais (chamada e material) gerava estranheza sem uma explicação textual de apoio (RF11).
5. **Legibilidade da comparação lado a lado:** A visualização comparativa de múltiplos docentes em telas menores (smartphones) empilhava os cartões, prejudicando a leitura comparativa simultânea (RF12, RF13).
6. **Percepção de critérios neutros:** O critério "Dificuldade" e o critério "Faz chamada" foram por vezes interpretados precipitadamente como aspectos negativos. Ambos devem ter apresentação neutra, preservando suas naturezas: Dificuldade é opinião e Chamada é fato (RF14, RF15).

### 2.2 Base normativa de requisitos

Os pontos de atenção foram confrontados com os requisitos aprovados e vigentes em [`docs/requisitos.md`](../requisitos.md):
- **RF01 e RF02:** Acesso e autenticação com e-mail institucional `@aluno.unb.br`.
- **RF04:** Consulta pública sem exigência de login.
- **RF05 a RF07:** Mecanismos de busca por professor, disciplina e código.
- **RF08:** Exibição agregada dos cinco critérios já consolidados para um professor em uma disciplina, e não a lista de avaliações individuais.
- **RF09:** Transparência estatística, exigindo informar a quantidade de avaliações que sustentam todo resultado agregado.
- **RNF02:** Proteção contra identificação indireta, que define a regra de produto de só exibir critérios agregados a partir de três avaliações por professor e disciplina, informando quantidade e insuficiência de dados abaixo desse patamar.
- **RF10 e RF11:** Tratamento explícito de estados especiais (sem avaliações e estado conflitante).
- **RF12 e RF13:** Comparação entre professores da mesma disciplina e ordenação por índice de recomendação.
- **RF14 e RF15:** Formulário estruturado de avaliação e agregação por natureza do critério (apresentação neutra).

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
| **3. Incompreensão do limiar de anonimato (< 3 avaliações)** | Aluno não entende por que um professor com 1 ou 2 avaliações não exibe médias numéricas | `/professores/[id]/disciplinas/[disciplinaId]` | RNF02, RF08, RF09 | **Alta** (baixa percepção de confiabilidade) | Relatado no feedback da R1 |
| **4. Dificuldade no estado conflitante** | Usuário estranha ver o rótulo "Conflitante" em chamada/material sem explicação contextual | `/professores/[id]/disciplinas/[disciplinaId]` | RF11 | **Alta** (gera dúvida na escolha) | Observado na demonstração |
| **5. Comparação em telas compactas (mobile)** | Cartões empilhados verticalmente dificultam a confrontação direta de métricas lado a lado | `/disciplinas/[id]` | RF12, RF13 | **Alta** (compromete o uso no smartphone) | Identificado na inspeção de UX |
| **6. Percepção da barreira de autenticação** | Dúvida se a consulta exige login institucional `@aluno.unb.br` | `/`, `/professores`, `/disciplinas` | RF04, RF14 | **Média** (gera atrito desnecessário) | Relatado no feedback da R1 |
| **7. Neutralidade de Dificuldade e Chamada** | Dificuldade alta e presença de chamada são confundidas com atributos negativos de mérito | `/avaliar`, `/professores/[id]/...` | RF14, RF15 | **Média** (avaliação enviesada) | Observado na demonstração |

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

## 7. Consolidação dos relatos e critérios da Issue #148

### 7.1 Evidências recebidas

Nicolas encaminhou dois relatos humanos de uso, organizados nos registros abaixo. São relatos indiretos, sem acompanhamento da sessão pelo agente, gravações ou medições. `ALUNO-02` foi identificado como aluno da UnB externo à equipe; `ALUNO-01` foi descrito como aluno externo, sem confirmação do vínculo institucional. Não se presume correspondência com as personas P1/P2.

| Participante | Atividades e resultados informados | Registro |
|---|---|---|
| ALUNO-01 | Abriu a página inicial, pesquisou professor e relatou dificuldades nos resultados, no retorno à busca, no acesso e no caminho para avaliar. Sucesso de login/envio não confirmado. | [Relato completo, OBS-01 a OBS-10](relato-usabilidade-aluno-01-issue-148.md). |
| ALUNO-02 | Acompanhou o processo, citou confusão na busca e dificuldade para chegar à avaliação; conseguiu usar após alguns cliques, sem confirmação do último passo ou envio. | [Relato completo e comparação, A02-01 a A02-04](relato-usabilidade-aluno-02-issue-148.md). |

Não foram informados data das sessões, versão testada, navegador, duração ou contagem de cliques. Como o segundo colega acompanhou o processo, não se presume que as observações sejam independentes. Não há confirmação de uso de `/prototipo`.

### 7.2 Priorização por recorrência nos relatos e impacto descrito

“Nos dois relatos” significa que o tema foi mencionado por ambos, não uma taxa de falha ou uma frequência de eventos por tarefa. A priorização é uma recomendação para planejamento, sem generalização estatística nem mudança automática de requisito.

| Ordem proposta | Obstáculo ou sugestão | Recorrência disponível | Impacto descrito e encaminhamento |
|---|---|---|---|
| 1 | Clareza da busca e da relação professor/disciplina | Nos dois relatos: OBS-01/02 e A02-01/03; causas específicas podem ser diferentes. | Dificulta identificar o destino correto e entender a organização. Investigar resultados e destacar contexto em #155/#157. |
| 2 | Encontrar o caminho de avaliação | Nos dois relatos: OBS-06 e A02-02. | Exige exploração e cliques adicionais percebidos; ALUNO-02 relatou uso possível depois disso. Rever a ação de avaliar e a continuidade em #155/#158. |
| 3 | Perda da pesquisa ao retornar | Somente ALUNO-01: OBS-03. | Obriga a refazer uma etapa já realizada. Preservar contexto da busca na #155. |
| 4 | Compreensão do login, rótulos, unidade e números | Somente ALUNO-01: OBS-04/05/07/10. | Dificulta interpretar informações e preencher o formulário. Identificar os elementos e revisar hierarquia/textos em #155/#157/#158. |
| 5 | Mostrar/ocultar senha | Sugestão de ALUNO-01: OBS-08. | Apoio à digitação; não houve falha de autenticação atribuída à ausência do controle. Avaliar alcance na #158. |
| Avaliar separadamente | Ordenações adicionais, sala/localização e foto do SIGAA | Sugestões em OBS-04/09 e A02-04. | Viabilidade e efeito não demonstrados. Definir escopo, fonte e decisão do PO antes de implementar. Não bloquear os ajustes de navegação por essas possibilidades. |

### 7.3 Rastreabilidade para execução

| Trabalho candidato | Achados | Telas a conferir | Regras a preservar |
|---|---|---|---|
| #155 — Navegação, busca e resultados | OBS-01 a OBS-06; A02-01 a A02-03 | Busca e página do professor, busca de disciplinas, login e links de retorno. | RF04–RF07/RF14; não unir homônimos por nome (ADR 07); explicitar o alcance de alterações de login/cadastro. |
| #157 — Apresentação e comparação | OBS-01/02/04/09/10; A02-03 | Resultados, disciplinas do professor e comparação da mesma disciplina. | RF06–RF13/RNF02; código continua pesquisável; ordenação da comparação continua por recomendação. |
| #158 — Formulário e percurso de avaliação | OBS-02/05/06/07/08; A02-02/03 | Consulta e formulário de professor/disciplina e continuidade após autenticação. | RF01/RF02/RF04/RF14/RF15; preservar escalas, booleanos, neutralidade e confirmação de e-mail. |

Os relatos detalham as propostas e verificações necessárias. A página do professor de referência já lista “Disciplinas lecionadas”; investigar sua visibilidade e o percurso antes de tratá-la como funcionalidade ausente. Fotos, novas ordenações e localização permanecem propostas, não novas obrigações das issues.

### 7.4 Avaliação dos critérios

Acompanhamento dos critérios existentes na [Issue #148](https://github.com/unb-mds/2026-02-UnDb/issues/148), no escopo de observação exploratória documentada:

- [x] **Registrar tarefas observadas, participantes e dificuldades sem inventar resultados:** os dois registros identificam participantes por códigos, atividades, dificuldades, resultados informados e dados ausentes, sem presumir envio de avaliação ou sessões independentes.
- [x] **Priorizar os obstáculos pela frequência e impacto observados:** a seção 7.2 registra recorrência nos dois relatos e impacto descrito para orientar a prioridade, sem inventar medições nem exigir significância estatística não prevista no critério.
- [x] **Relacionar achados às telas e aos requisitos existentes:** a seção 7.3 e as matrizes dos relatos relacionam dificuldades às telas candidatas, regras vigentes e issues de implementação.

Os critérios estão documentados para revisão e aceite da #148. A marcação descreve a avaliação técnica deste material; o fechamento no GitHub segue o aceite humano e o fluxo da PR #181. A identificação do número desconhecido, a reprodução dos resultados com nomes repetidos e a confirmação da versão continuam limitações de reprodução, explicitadas nos relatos.

O teste do protótipo, a comparação entre versões e a demonstração de redução dos obstáculos continuam na #153. Não são considerados realizados por esta entrega. A implementação e a revalidação das melhorias permanecem nas issues posteriores.

---

## 8. Próximos passos e articulação com a Release 2

1. **Protótipo disponível ([Issue #152](https://github.com/unb-mds/2026-02-UnDb/issues/152)):** a proposta em `/prototipo` já existe e usa dados demonstrativos. Os relatos acima não comprovam seu teste.
2. **Validação do protótipo ([Issue #153](https://github.com/unb-mds/2026-02-UnDb/issues/153)):** executar tarefas correspondentes aos obstáculos registrados, identificar a versão e registrar resultados, ajuda recebida e limitações de comparação.
3. **Implementação de melhorias de interface ([Issues #155, #157 e #158](https://github.com/unb-mds/2026-02-UnDb/issues/144)):** após a validação, aplicar os ajustes priorizados às rotas reais e verificar o percurso completo. Mudanças de produto continuam sujeitas a decisão explícita do PO.

---

## 9. Referências

- [Issue #148 — [R2][UX] Observar a jornada de busca, comparação e avaliação com alunos](https://github.com/unb-mds/2026-02-UnDb/issues/148)
- [Issue #152 — [R2][UX] Prototipar tela inicial, busca, resultados, comparação e formulário](https://github.com/unb-mds/2026-02-UnDb/issues/152)
- [Issue #153 — [R2][UX] Validar protótipo da jornada com alunos](https://github.com/unb-mds/2026-02-UnDb/issues/153)
- [Épico #144 — [EPIC][R2] Melhorar a jornada do aluno na aplicação](https://github.com/unb-mds/2026-02-UnDb/issues/144)
- [`docs/requisitos.md`](../requisitos.md) — Fonte autorizada de requisitos do UnDb
- [`docs/visao.md`](../visao.md) — Documento de visão do produto
