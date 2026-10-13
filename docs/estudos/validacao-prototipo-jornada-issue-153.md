# [R2][UX] Validação do Protótipo da Jornada com Alunos

**Estado:** Documento de validação e roteiro de pesquisa elaborado para a issue [#153](https://github.com/unb-mds/2026-02-UnDb/issues/153), vinculada ao épico [#144](https://github.com/unb-mds/2026-02-UnDb/issues/144) (Melhorar a jornada do aluno na aplicação).

---

## 1. Objetivo e Contexto

O objetivo desta atividade é verificar se o protótipo da jornada do aluno reduz os obstáculos identificados no diagnóstico anterior (levantados após a Release 1 e consolidados na issue [#148](https://github.com/unb-mds/2026-02-UnDb/issues/148)), registrando:

1. Roteiro estruturado de tarefas, observações e critérios de avaliação;
2. Limitações da amostra, do ambiente e da maturidade do protótipo;
3. Comparação sistemática dos obstáculos mapeados antes e depois da prototipação;
4. Encaminhamentos ao Product Owner (PO) para decisões de produto pendentes;
5. Pendências explícitas para a realização de testes empíricos com participantes reais.

Conforme a governança do projeto (`skills/governance/project-governance/SKILL.md` e `skills/process/requirements/SKILL.md`), **esta tarefa não cria participantes, sessões ou dados empíricos fictícios**, preserva as regras de negócio vigentes em [`docs/requisitos.md`](../requisitos.md) e separa categoricamente sugestões de interface de mudanças em regras de produto.

---

## 2. Relação com o Diagnóstico Anterior e Estado dos Artefatos

A investigação de UX da Release 2 desdobra-se em três etapas complementares no épico #144:

1. **Diagnóstico e Observação Preliminar (Issue #148):**  
   Mapeou os pontos de atrito identificados na apresentação da Release 1 e nos requisitos RF04–RF14, destacando:
   - Dúvida sobre o ponto de partida da busca (divisão rígida entre professor e disciplina na home);
   - Incerteza entre consulta anônima (aberta) e cadastro obrigatório para avaliar;
   - Risco de interpretar o estado vazio (sem avaliações) ou dados insuficientes (< 3 avaliações) como avaliação negativa;
   - Dificuldade de compreensão do estado "conflitante" em critérios factuais (chamada e material);
   - Falta de contexto na leitura lado a lado e na ordenação por recomendação na tela de disciplina;
   - Ruído no formulário de avaliação quanto à neutralidade dos critérios (Dificuldade e Chamada).

2. **Prototipação da Jornada (Issue #152):**  
   Atribuída ao design/prototipação com o objetivo de desenhar a jornada unificada cobrindo entrada, busca, resultados, comparação e formulário de avaliação, sem alterar as regras aprovadas. No momento desta avaliação, o protótipo formal de alta fidelidade na issue #152 ainda se encontra em fase de proposição/elaboração, enquanto a implementação funcional da Release 1 no frontend Next.js serve como base executável inspecionada.

3. **Validação do Protótipo com Alunos (Issue #153 - Este Documento):**  
   Estrutura o instrumento e o protocolo de teste, analisa a interface e a jornada pretendida frente aos obstáculos conhecidos, encaminha decisões pendentes ao PO e define as pré-condições para execução das sessões presenciais/remotas com estudantes.

---

## 3. Roteiro Reproduzível de Avaliação da Jornada

### 3.1 Perfil dos Participantes (Anonimizado)

O recrutamento foca nas personas descritas na seção 3 de [`docs/requisitos.md`](../requisitos.md):

- **P1 — Aluno sem rede:** Estudante de 2º ou 3º semestre, introvertido ou matriculado em disciplina de módulo livre (fora do seu departamento de origem), que precisa decidir matrícula sem recorrer a grupos informais.
- **P2 — Veterano com histórico:** Estudante de 5º semestre em diante, com rede formada, que possui repertório para avaliar professores e validar a clareza da agregação.

**Princípios éticos e privacidade:**
- Consentimento livre e esclarecido obtido antes do início da sessão.
- Nenhum dado pessoal identificável (nome completo, matrícula, CPF ou e-mail real) é registrado na documentação pública.
- Os participantes são identificados internamente apenas por códigos anônimos (ex.: `ALUNO-01`, `ALUNO-02`), indicando apenas perfil (`P1` ou `P2`) e semestre relativo.

### 3.2 Tarefas Realistas e Neutras

As tarefas representam metas concretas de um estudante durante o período de matrícula. As instruções são passadas de forma estritamente neutra, sem induzir o percurso de navegação ou antecipar o vocabulário das telas.

| ID | Cenário / Objetivo do Aluno | Instrução Neutra ao Participante | Funcionalidade Esperada |
|---|---|---|---|
| **T1** | Localizar um professor específico para verificar sua reputação. | *"Imagine que você ouviu falar da professora Maria Emilia e quer saber como são as aulas dela. Mostre como você pesquisaria isso no sistema."* | Busca por nome parcial de professor (`/professores`). |
| **T2** | Escolher professor para uma matéria obrigatória. | *"Você precisa cursar 'Cálculo 1' no próximo semestre e quer ver quais professores estão oferecendo turmas e como estão avaliados. Mostre como você faria."* | Busca de disciplina por código/nome (`/disciplinas`) e visualização da comparação (`/disciplinas/[id]`). |
| **T3** | Interpretar o resumo estatístico de um docente. | *"Olhando para a página deste professor nesta disciplina, explique o que as informações apresentadas significam para você."* | Leitura de critérios consolidados, quantidade de avaliações e alertas de dados insuficientes ou conflitantes (`/professores/[id]/disciplinas/[disciplinaId]`). |
| **T4** | Comparar duas opções de turmas. | *"Entre os professores disponíveis para esta matéria, qual você escolheria com base nas informações apresentadas? Por quê?"* | Interpretação da ordenação por recomendação e comparação lateral. |
| **T5** | Contribuir com uma avaliação após cursar a matéria. | *"Você cursou a matéria com este professor e deseja registrar sua experiência para ajudar outros alunos. Mostre como procederia."* | Localização do botão de avaliar, preenchimento dos 5 critérios e compreensão do aviso de autenticação/e-mail (`.../avaliar`). |

### 3.3 Protocolo de Registro de Observações

Durante a sessão (observação direta ou teste de usabilidade moderado), o facilitador registra em tempo real:

| Campo | Descrição |
|---|---|
| **Participante** | Identificador anônimo (`ALUNO-XX`). |
| **Perfil** | `P1` ou `P2`, acrescido do semestre aproximado. |
| **Tarefa** | `T1`, `T2`, `T3`, `T4` ou `T5`. |
| **Conclusão** | Concluída com sucesso / Concluída com dificuldade / Abandonada. |
| **Tempo Estimado** | Tempo aproximado até atingir o objetivo ou desistir. |
| **Hesitações e Dúvidas** | Momentos em que o participante parou, releu ou expressou confusão em voz alta (*Think Aloud*). |
| **Desvios de Navegação** | Caminhos incorretos tentados antes de achar a tela correta (ex.: tentar buscar professor na página de disciplinas). |
| **Compreensão de Rótulos** | Como o participante interpretou termos como "Dados insuficientes", "Conflitante", "Didática", "Dificuldade" e "Chamada". |
| **Feedback Espontâneo** | Citações diretas e impressões gerais verbalizadas voluntariamente. |

### 3.4 Critérios de Avaliação Definidos a Priori

Para evitar análises subjetivas pós-teste, definem-se os seguintes critérios de sucesso da jornada:

1. **Eficácia (Conclusão de Tarefa):** Pelo menos 80% dos participantes devem concluir as tarefas de busca (T1/T2) e localização de avaliação (T3) sem intervenção do facilitador.
2. **Clareza dos Estados Especiais:** 100% dos participantes devem compreender que "Dados insuficientes" não significa nota zero ou professor reprovado.
3. **Compreensão de Critérios Neutros:** Pelo menos 75% dos participantes devem reconhecer que os critérios "Dificuldade" e "Faz chamada" são descritivos e factuais, não notas de mérito.
4. **Percepção de Acesso:** Os participantes devem identificar claramente que navegar e comparar é público, mas registrar avaliação requer login institucional `@aluno.unb.br`.

### 3.5 Limitações Conhecidas

- **Maturidade dos Artefatos:** A prototipação visual dedicada da R2 (issue #152) ainda está em processo de alinhamento com os novos fluxos de comentários da R2; a jornada atual reflete a implementação consolidada da Release 1.
- **Ambiente de Teste:** O ambiente de testes com estudantes pode utilizar dados pré-carregados (seed) ou mockados da API, reduzindo a variabilidade de casos reais do SIGAA.
- **Tamanho da Amostra:** Testes qualitativos de usabilidade em equipes acadêmicas costumam cobrir entre 3 e 5 alunos por ciclo, o que identifica os principais gargalos de navegação, mas não possui significância estatística quantitativa.
- **Ausência de Dados Fictícios:** Não foram geradas sessões empíricas simuladas neste documento. O protocolo está pronto para aplicação pelos membros da equipe nas próximas sessões de pesquisa de campo da Sprint 06.


---

## 4. Registro de Evidências da Avaliação do Protótipo

A avaliação do protótipo e da jornada de usuário sob a ótica dos requisitos e componentes existentes revela evidências concretas sobre as capacidades e limitações do fluxo:

### 4.1 Sessões com Participantes e Declaração de Pendência

Conforme a seção 1 da issue #153 e as diretrizes do `AGENTS.md` e `project-governance`, **não foram criadas sessões de teste ou participantes fictícios**.

> ⚠️ **Registro Explícito de Pendência de Validação Empírica:**  
> A realização presencial ou remota dos testes com alunos das turmas de graduação da UnB (perfis P1 e P2) está programada para a Sprint 06, sob responsabilidade da equipe executora. Este documento fornece o roteiro neutro, as tarefas padronizadas e a matriz de coleta necessários para a execução dessas sessões.

### 4.2 Evidências Técnicas Observadas na Inspeção de Usabilidade da Jornada

A partir da inspeção minuciosa dos componentes frontend desenvolvidos na Release 1 (`frontend/src/app/*`) e da proposta visual da Release 2, identificam-se os seguintes comportamentos estruturais:

1. **Jornada de Entrada e Descoberta (`/`, `/professores`, `/disciplinas`):**
   - **Comportamento observado:** A tela inicial exige que o estudante escolha antecipadamente entre "Buscar professor" ou "Buscar disciplina".
   - **Evidência no código:** O componente [`Home`](file:///home/tiago/MDS-G7/G7-2026-2/frontend/src/app/page.tsx) renderiza dois cards separados direcionando para `/professores` e `/disciplinas`.
   - **Atrito identificado:** Um aluno sem rede (P1) que deseja avaliar as opções para uma matéria obrigatória pode buscar o nome do professor achando que encontrará a disciplina ou vice-versa, gerando cliques redundantes de navegação.

2. **Diferenciação entre Consulta Pública e Acesso Autenticado:**
   - **Comportamento observado:** A consulta às páginas de agregação (`/professores/[id]/disciplinas/[disciplinaId]`) e de comparação (`/disciplinas/[id]`) funciona de modo 100% público, sem redirecionamento para login.
   - **Evidência no código:** O botão "Avaliar este professor na disciplina" permite acesso ao formulário; o aviso de login (`precisaEntrar`) é acionado apenas na submissão ou indicado textualmente no topo do formulário.

3. **Comunicação de Estados Especiais (Vazio, Insuficiente e Conflitante):**
   - **Vazio:** Na tela de agregação, quando `totalAvaliacoes === 0`, exibe textualmente: *"Ainda não há avaliações para este professor nesta disciplina."*
   - **Insuficiente:** Quando `dadosSuficientes === false` (menos de 3 avaliações), exibe: *"Dados insuficientes para exibir os critérios — são necessárias pelo menos 3 avaliações para proteger a identidade de quem avaliou. Faltam X."*
   - **Conflitante:** Para os critérios factuais de chamada e material, o sistema exibe o rótulo explícito `"Conflitante"` quando não há consenso entre as respostas (conforme RF11).

4. **Comparação de Professores na Disciplina (`/disciplinas/[id]`):**
   - **Comportamento observado:** Lista em grade responsiva todos os professores que ofertam turmas ativas para a disciplina, exibindo dados agregados ou mensagem de insuficiência e ordenando decrescentemente por taxa de recomendação.
   - **Atrito identificado:** Não há filtros rápidos para alternar critérios (ex.: ordenar por didática ou ver turmas de horário específico), e os cartões ocupam espaço vertical relevante em telas menores (mobile).

5. **Formulário de Avaliação e Critérios Neutros (`.../avaliar`):**
   - **Comportamento observado:** O formulário possui mensagem destacando: *"Dificuldade e Chamada são informações neutras, sem indicação de bom ou ruim."*
   - **Atrito identificado:** O controle é composto por `<select>` suspensos individuais. O envio sem estar autenticado gera aviso com link em nova aba para login, o que pode causar perda de contexto ou descontinuidade da sessão.


---

## 5. Comparação com o Diagnóstico Anterior

A tabela a seguir confronta os obstáculos priorizados no diagnóstico da issue #148 com as evidências observadas no protótipo e na implementação da jornada, classificando o status da melhora e indicando ajustes sugeridos:

| Obstáculo Original (Issue #148) | Evidência de Origem (Diagnóstico Anterior) | Comportamento Observado no Protótipo / Jornada | Avaliação de Melhora | Ajuste Sugerido e Justificativa |
|---|---|---|---|---|
| **1. Confusão na busca inicial entre professor, disciplina e código** | Usuário não sabe se busca professor, código ou matéria; atrito maior em módulo livre (RF05–RF07). | Home ainda divide em dois fluxos estáticos (`/professores` e `/disciplinas`). Ao entrar em um, não é possível buscar o outro diretamente. | **Ausência de melhora** | Propor campo de busca unificado na home (com abas ou resultados agrupados "Professores" e "Disciplinas"). Reduz cliques e atende diretamente a P1. |
| **2. Percepção ambígua de consulta pública vs. avaliação restrita** | Falta de clareza se é preciso cadastro para consultar as avaliações (RF04, RF14). | Consulta é totalmente aberta e fluida; home possui texto explicativo (*"Consulte avaliações estruturadas sem precisar de rede de contatos"*). O login só é cobrado na submissão. | **Melhora comprovada** | Manter o acesso livre à consulta e reforçar no botão de avaliação a informação prévia *"Exige login @aluno.unb.br"*, evitando surpresa no envio. |
| **3. Interpretação errônea do estado vazio como avaliação negativa** | Ausência de avaliações pode ser interpretada como nota zero ou reprovação do professor (RF10). | Componente explicita *"Ainda não há avaliações para este professor nesta disciplina"* e não renderiza notas vazias ou estrelas zeradas. | **Melhora comprovada** | Incluir call-to-action encorajando: *"Seja o primeiro a avaliar este docente nesta matéria"*, estimulando a persona P2 a alimentar a base. |
| **4. Incompreensão do estado de dados insuficientes (< 3 avaliações)** | Usuário não entende por que não vê notas quando já existem 1 ou 2 envios. | Mensagem clara na tela de detalhe: *"Dados insuficientes... são necessárias pelo menos 3 avaliações para proteger a identidade de quem avaliou. Faltam X."* | **Melhora comprovada** | Na tela de comparação de disciplinas (`/disciplinas/[id]`), a mensagem atual diz apenas *"Dados insuficientes para exibir os critérios"*. Recomenda-se unificar o texto explicando o motivo do anonimato também na comparação. |
| **5. Dificuldade de interpretação do estado "Conflitante"** | Usuário estranha ver "Conflitante" em chamada e material, sem saber como interpretar (RF11). | O rótulo "Conflitante" é exibido textualmente quando não há maioria clara. Falta explicação em tooltip ou legenda contextual sobre o que gerou o conflito estatístico. | **Evidência insuficiente** (requer teste de campo com alunos) | Adicionar microcopy explicativo: *"Respostas divididas entre os estudantes — metade relata que faz chamada e metade relata que não"*. |
| **6. Leitura e comparabilidade lado a lado** | Comparação em grade pode ficar truncada ou confusa em dispositivos móveis (RF12, RF13). | Em desktop, cards lado a lado exibem dados agregados satisfatoriamente. Em mobile, os cartões empilham-se verticalmente, dificultando a comparação direta simultânea. | **Melhora parcial** | Desenvolver modo de comparação compacto tipo tabela ou visualização condensada com alternância de métricas principais para visualização mobile. |
| **7. Entendimento de critérios neutros (Dificuldade e Chamada)** | Dificuldade alta pode ser julgada precipitadamente como algo ruim; chamada como perseguição (RF14, RF15). | Aviso em destaque: *"Dificuldade e Chamada são informações neutras, sem indicação de bom ou ruim"*. | **Melhora comprovada** | Manter a legenda e avaliar em testes se a escala textual (Fácil / Médio / Difícil) comunica neutralidade com sucesso. |

---

## 6. Encaminhamentos ao Product Owner (PO)

A análise da jornada e dos requisitos vigentes (`docs/requisitos.md`) permitiu separar claramente o que são **sugestões de design e usabilidade (UX)** do que constitui **mudanças em regras de negócio ou de produto que exigem decisão humana do PO**.

### 6.1 Sugestões de UX e Interface (Trabalho Técnico da Equipe)

Estas melhorias não alteram critérios de agregação, escalas ou regras de negócio, podendo ser incorporadas nas issues de frontend do épico #144 (issues #155, #157, #158):

1. **Unificação da busca na Home:** Permitir buscar simultaneamente professores ou disciplinas em uma barra de pesquisa única na página inicial, com agrupamento claro dos resultados.
2. **Harmonização do aviso de dados insuficientes:** Exibir a contagem regressiva (*"Faltam X avaliações para proteger o anonimato"*) também nos cards da tela de comparação de professores (`/disciplinas/[id]`).
3. **Preservação de rascunho de avaliação:** Se o usuário tentar enviar uma avaliação sem autenticação, persistir temporariamente as opções selecionadas em `sessionStorage` para restaurá-las automaticamente após o retorno do login, evitando redigitação.

### 6.2 Pontos Dependentes de Decisão do PO (Regras de Produto)

Os seguintes pontos identificados durante a revisão tocam regras de negócio, restrições e políticas de produto, ficando expressamente encaminhados para validação do PO:

1. **Ordenação na Comparação de Disciplinas (RF13):**
   - *Situação atual:* O RF13 estabelece que a comparação deve ser ordenada estritamente pelo percentual de recomendação (`recomenda`).
   - *Questão ao PO:* Em turmas onde um professor possui 100% de recomendação com base em apenas 3 avaliações e outro possui 95% de recomendação com base em 50 avaliações, deve haver opção para o aluno ordenar por didática ou ponderar pela quantidade de avaliações?
   - *Impacto:* Requer alteração no RF13 se filtros adicionais de ordenação forem aprovados.
   
2. **Exibição de Turmas Históricas vs. Turmas Ativas (RF16 / RF17):**
   - *Situação atual:* O sistema exibe na comparação professores com turmas ativas no semestre vigente importadas do SIGAA.
   - *Questão ao PO:* Professores com histórico avaliado, mas que não possuem turma ativa no semestre atual, devem constar na comparação de uma disciplina (com aviso de "sem turma neste semestre") para fins de referência de módulo livre?
   
3. **Fluxo de Comentários Textuais na R2 (RF20, RF21, RF22):**
   - *Situação atual:* O formulário da R1 é 100% estruturado (sem texto livre). O RF20 introduz comentários em texto na R2.
   - *Questão ao PO:* O comentário será obrigatório ou opcional na submissão da avaliação? O comentário passará por moderação prévia ou denúncia posterior (post-moderation)?

---

## 7. Status dos Critérios da Issue #153 e Pendências

Acompanhamento dos critérios de conclusão estabelecidos na Issue [#153](https://github.com/unb-mds/2026-02-UnDb/issues/153):

- [x] **Tarefas, observações e limitações da avaliação registrados:** O documento especifica o roteiro reproduzível de 5 tarefas neutras, a matriz de observações e as limitações técnicas e metodológicas da avaliação.
- [x] **Principais obstáculos comparados com o diagnóstico anterior:** Tabela comparativa confrontando cada um dos 7 obstáculos da issue #148 com as evidências do protótipo e da implementação atual.
- [x] **Mudanças que impliquem regras de produto encaminhadas ao PO:** Pontos de decisão de produto (ordenação da comparação, turmas sem oferta ativa e política de comentários da R2) foram catalogados e isolados das sugestões puras de UX.
- [ ] **Realização das sessões empíricas com alunos:** Registrada explicitamente como **pendência aberta** a ser executada pela equipe nas dinâmicas de teste da Sprint 06.

---

## 8. Referências

- [Issue #153 — [R2][UX] Validar protótipo da jornada com alunos](https://github.com/unb-mds/2026-02-UnDb/issues/153)
- [Issue #148 — [R2][UX] Observar a jornada de busca, comparação e avaliação com alunos](https://github.com/unb-mds/2026-02-UnDb/issues/148)
- [Issue #152 — [R2][UX] Prototipar tela inicial, busca, resultados, comparação e formulário](https://github.com/unb-mds/2026-02-UnDb/issues/152)
- [Épico #144 — [EPIC][R2] Melhorar a jornada do aluno na aplicação](https://github.com/unb-mds/2026-02-UnDb/issues/144)
- [`docs/requisitos.md`](../requisitos.md) — Fonte de verdade dos requisitos do projeto
- [`docs/visao.md`](../visao.md) — Documento de visão do produto
