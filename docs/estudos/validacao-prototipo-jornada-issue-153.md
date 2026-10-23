# [R2][UX] Preparação da validação da jornada com alunos

**Estado:** roteiro proposto e inspeção documental/técnica para a [issue #153](https://github.com/unb-mds/2026-02-UnDb/issues/153), vinculada ao [épico #144](https://github.com/unb-mds/2026-02-UnDb/issues/144). **Validação com alunos não realizada nos registros consultados; redução de obstáculos não demonstrada.** Revisão documental em 14/10/2026.

**Atualização em 22/10/2026:** este documento preserva a preparação histórica de 14/10. O [relatório de resultados do reteste](resultados-reteste-jornada-issue-153.md) registra o retorno recebido depois, compara obstáculos e atualiza a avaliação dos critérios da #153. As afirmações de ausência de resultados abaixo descrevem o estado histórico da preparação.

## 1. Objetivo e limites da entrega

**Atualização de preparação em 22/10/2026:** os relatos da #148 motivaram uma [adaptação do protótipo e um roteiro para a próxima rodada](ajustes-prototipo-jornada-issue-153.md). Esse material complementa o roteiro histórico abaixo e ainda não apresenta resultados de teste do protótipo com alunos.

A issue #153 pede verificar, com alunos, se o protótipo reduz os obstáculos identificados no diagnóstico anterior antes de implementar as telas. Este documento prepara tarefas, coleta e comparação, registra capacidades verificáveis da implementação anterior e encaminha questões de produto ao PO.

O roteiro e a existência de mensagens na interface não demonstram compreensão pelos estudantes. Não foram apresentados registros de sessões, participantes recrutados ou resultados antes/depois. Esses dados não são substituídos por testes automatizados, inspeção de código ou dados demonstrativos do protótipo.

As regras vigentes são as de [requisitos](../requisitos.md), especialmente RF04–RF15, RNF02 e seções 6, 8 e 11. Conforme `project-governance`, propostas de UX e questões de produto permanecem separadas de decisões aprovadas.

## 2. Fontes e versões dos artefatos

| Artefato | Versão e localização verificáveis | Uso e limite nesta entrega |
|---|---|---|
| Diagnóstico da issue #148 | [Observação da jornada, commit `838e443`](https://github.com/unb-mds/2026-02-UnDb/blob/838e4435122136a008df630b89606ad10aeab077/docs/estudos/observacao-jornada-busca-comparacao.md), entregue na [PR #176](https://github.com/unb-mds/2026-02-UnDb/pull/176) | Seção 5: sete obstáculos preliminares. O próprio documento mantém a coleta com alunos e a frequência observada pendentes. Seus relatos e prioridades não são tratados aqui como pesquisa empírica concluída. |
| Interface anterior inspecionada na PR #178 | [Frontend, commit `e320ee7`](https://github.com/unb-mds/2026-02-UnDb/tree/e320ee710d2bc6ffe6a5c63633822e848f2aad89/frontend/src/app) | Inspeção estática das rotas reais de busca, consulta, comparação e avaliação oriundas da R1. Não é uma sessão de uso nem comprovação do comportamento da release implantada. |
| Protótipo da R2, issue #152 | [Relatório, capturas e reprodução, commit `d5bd200`](https://github.com/unb-mds/2026-02-UnDb/blob/d5bd2008d8a0daf125d74bd7cc87f94a98e1a2d0/docs/estudos/verificacao-prototipo-jornada-issue-152.md), entregue na [PR #179](https://github.com/unb-mds/2026-02-UnDb/pull/179) | Protótipo navegável identificado em `/prototipo`, com dados demonstrativos e prévia sem envio. Disponível para preparar a avaliação; não foi avaliado com alunos nesta entrega. |

O protótipo da R2 já possui artefato identificado; a descrição anterior de que estava apenas em elaboração foi substituída pelas referências acima. Para reproduzi-lo, utilizar a versão indicada e as instruções do relatório da #152: em `frontend/`, `npm ci`, `npm run dev` e acesso a `http://localhost:3000/prototipo`. Ele não exige backend.

A seção 4 descreve exclusivamente a interface real no commit `e320ee7`. A seção 5 confronta essa inspeção com o diagnóstico preliminar; não constitui comparação de resultados de alunos entre R1 e R2. A versão efetivamente apresentada aos participantes deverá constar no registro de cada sessão.

O diagnóstico da #148 também contém descrições normativas imprecisas: Dificuldade é **opinião**, não fato, e o mínimo de três avaliações decorre de **RNF02**, não de RF08/RF09. Esta entrega utiliza os requisitos como fonte para essas regras; não modifica o diagnóstico de outra issue.

## 3. Roteiro proposto para avaliação

### 3.1 Perfis de recrutamento

P1 e P2 são personas de referência da seção 3 dos requisitos, **não participantes já recrutados ou observados**:

- **P1 — Aluno sem rede:** estudante de 2º/3º semestre, introvertido ou cursando módulo livre, que consulta informações para decidir matrícula.
- **P2 — Veterano que já se queimou:** estudante de 5º semestre em diante, com repertório para consultar e contribuir com avaliações.

Antes da sessão, obter consentimento e atribuir um código anônimo, como `ALUNO-01`. Não publicar nome, matrícula, CPF, e-mail real ou outros dados que identifiquem o participante. Registrar somente o perfil necessário à análise.

### 3.2 Tarefas e preparação dos cenários

As instruções abaixo são propostas para aplicação moderada. No protótipo `d5bd200`, Ana e Algoritmos são exemplos fictícios da interface, não alunos, professores ou avaliações reais. Preparar os mesmos objetivos na interface anterior com dados controlados e registrar diferenças de ambiente e conteúdo.

| ID | Objetivo | Instrução ao participante | Preparação do facilitador |
|---|---|---|---|
| **T1** | Buscar professor por nome parcial | “Você ouviu falar da professora Ana e quer consultar as informações sobre ela. Mostre como faria.” | Garantir um resultado correspondente; registrar o termo usado e o percurso. |
| **T2** | Buscar disciplina por nome/código, inclusive de outro departamento | “Você pretende cursar Algoritmos e quer consultar as opções de professores. Mostre como faria.” | Repetir com o código e uma disciplina de outro departamento, sem indicar onde clicar. Não presumir oferta no próximo semestre. |
| **T3** | Interpretar resultados e estados especiais | “Explique o que estas informações permitem concluir sobre este professor nesta disciplina.” | Apresentar casos com zero avaliações, duas avaliações e dados suficientes com conflito em Chamada/Material. Registrar cada caso separadamente, sem antecipar sua explicação. |
| **T4** | Comparar professores da mesma disciplina | “Qual destas opções você escolheria com as informações disponíveis? Por quê?” | Registrar entendimento da recomendação, contagem e neutralidade; repetir em tela compacta e registrar a largura. |
| **T5** | Localizar e preencher avaliação | “Você cursou a matéria e quer compartilhar sua experiência. Mostre como procederia.” | No protótipo, concluir apenas a prévia; no sistema real, usar ambiente e contas de teste. Registrar a interpretação do acesso autenticado e do e-mail confirmado. |

### 3.3 Registro a preencher em cada sessão real

Nenhuma linha de resultado foi preenchida. O facilitador deverá registrar:

| Campo | Informação necessária |
|---|---|
| Sessão | Data, facilitador e código anônimo do participante; perfil P1/P2 quando aplicável. |
| Artefato | Interface anterior ou protótipo; commit, rota/URL, dados preparados e estado apresentado. |
| Ambiente | Dispositivo, largura de tela, navegador e limitações de acesso/rede. |
| Tarefa e caso | T1–T5; em T3, distinguir vazio, insuficiente e conflitante. |
| Resultado | Concluída com autonomia, concluída com ajuda/dificuldade ou não concluída; registrar intervenção. |
| Observação | Hesitação, desvio, erro, interpretação expressa e tempo, se medido; separar descrição de inferência. |
| Fala | Citação real, quando houver consentimento e sem identificação pessoal. |
| Evidência | Referência ao registro anonimizado, trecho ou captura autorizada que sustenta a observação. |
| Comparação | Obstáculo do diagnóstico, ocorrência em cada versão e limitações de comparabilidade. |

### 3.4 Aspectos a observar, sem novos critérios de aceite

Não foi localizada aprovação dos percentuais de 80%, 100% ou 75% apresentados na versão anterior. Eles foram retirados; este roteiro não institui metas quantitativas nem redefine os critérios da issue.

Observar e registrar:

1. Conclusão de T1/T2 e acesso à leitura dos resultados em T3, com ou sem intervenção.
2. Compreensão de que zero avaliações não significa avaliação negativa e de que RNF02 oculta critérios abaixo de três avaliações.
3. Interpretação de “Conflitante” como empate nas respostas factuais de Chamada ou disponibilidade de Material, conforme seção 11 dos requisitos.
4. Ausência de direção boa/ruim em Dificuldade e Chamada. **Dificuldade é opinião agregada por moda; Chamada é fato agregado por maioria.** Neutralidade visual não altera essa natureza.
5. Compreensão de que consultar/comparar é público e registrar avaliação exige conta autenticada com e-mail confirmado, nos termos de RF04/RF14.

### 3.5 Limitações e comparação futura

O tamanho da amostra, recrutamento, responsáveis e datas das sessões ainda precisam ser registrados pela equipe. A issue sugere Sprint 6; isso não comprova agendamento ou execução de pesquisa.

O protótipo utiliza exemplos fixos e não realiza consulta à API, autenticação ou envio real. Suas fixtures permitem explorar estados visuais, mas não comprovam integração, oferta atual de turmas ou sucesso de envio. Alterações de dados, largura de tela e intervenção do facilitador devem ser registradas para não atribuir ao design diferenças causadas pelo ambiente.

Para avaliar redução de obstáculos, registrar as mesmas tarefas e casos nas versões identificadas, indicando ordem de apresentação e possível aprendizado pela repetição. Consolidar ocorrências com denominador e limitações; não transformar ausência de observação em comprovação de melhora.

## 4. Inspeção técnica da interface anterior

As evidências abaixo são de código no commit `e320ee7`, sem sessões com estudantes e sem execução de navegação nesta revisão.

| Parte da jornada | Capacidade verificada no código | Hipótese ou limite a observar com alunos |
|---|---|---|
| Entrada e busca | [Home](https://github.com/unb-mds/2026-02-UnDb/blob/e320ee710d2bc6ffe6a5c63633822e848f2aad89/frontend/src/app/page.tsx) oferece dois cards, “Buscar professor” e “Buscar disciplina”, com rotas distintas. | A escolha inicial pode gerar hesitação; sua ocorrência não foi medida nesta entrega. |
| Consulta e acesso à avaliação | [Consulta agregada](https://github.com/unb-mds/2026-02-UnDb/blob/e320ee710d2bc6ffe6a5c63633822e848f2aad89/frontend/src/app/professores/%5Bid%5D/disciplinas/%5BdisciplinaId%5D/page.tsx) permite chegar ao formulário. O [formulário](https://github.com/unb-mds/2026-02-UnDb/blob/e320ee710d2bc6ffe6a5c63633822e848f2aad89/frontend/src/app/professores/%5Bid%5D/disciplinas/%5BdisciplinaId%5D/avaliar/avaliacao-form.tsx) informa conta/e-mail confirmado e consulta a sessão no envio; em 401, oferece login em nova aba. | Verificar se o estudante distingue consulta pública e envio autenticado e se o retorno da nova aba causa perda de contexto. |
| Vazio e insuficiência | A consulta agregada informa ausência de avaliações, contagem e mínimo de três. “Faltam X” aparece somente quando há uma ou duas avaliações. Os critérios não são renderizados quando `dadosSuficientes` é falso. | A presença do aviso não comprova que o estudante entende o limiar ou evita leitura negativa. RNF02 define um mínimo inicial, sem garantia empírica de anonimato. |
| Conflito | A consulta agregada renderiza “Conflitante” para Chamada e disponibilidade de Material. | Verificar a compreensão do empate factual; não confundir com opinião sobre qualidade de material. |
| Comparação | A [tela de disciplina](https://github.com/unb-mds/2026-02-UnDb/blob/e320ee710d2bc6ffe6a5c63633822e848f2aad89/frontend/src/app/disciplinas/%5Bid%5D/page.tsx) usa grade de uma coluna abaixo do breakpoint `sm` e duas acima, com contagem e avisos. O [serviço](https://github.com/unb-mds/2026-02-UnDb/blob/e320ee710d2bc6ffe6a5c63633822e848f2aad89/backend/app/services/avaliacao_service.py) ordena por recomendação decrescente, depois quantidade e nome; resultados insuficientes ficam no final. | O layout e a ordenação estão no código; legibilidade e compreensão não foram verificadas com participantes. |
| Critérios neutros | O formulário contém “Dificuldade e Chamada são informações neutras, sem indicação de bom ou ruim” e cinco selects nas escalas da R1. | Verificar a interpretação das escalas e da neutralidade, sem classificar Dificuldade como fato. |

## 5. Confronto preliminar com o diagnóstico da #148

Os identificadores abaixo preservam a ordem dos sete obstáculos da seção 5 do diagnóstico no commit `838e443`. A coluna de implementação refere-se ao commit `e320ee7`, **não ao protótipo R2**. Em todos os casos, a redução do obstáculo permanece **não avaliada com alunos**.

| Obstáculo da #148 | Implementação anterior verificável | Hipótese para avaliação / proposta de UX |
|---|---|---|
| **1. Ambiguidade na busca inicial** (RF05–RF07) | Dois caminhos separados na home. | Observar escolha inicial e desvios; avaliar proposta de busca unificada, sem presumir menos cliques ou maior sucesso. |
| **2. Interpretação do estado vazio** (RF10) | Mensagem de ausência de avaliações; sem valores dos critérios quando insuficientes. | Verificar se a ausência é distinguida de avaliação negativa; considerar convite para avaliar. |
| **3. Incompreensão do limiar** (RNF02; RF09) | Detalhe informa mínimo e avaliações faltantes; comparação mostra contagem e aviso mais curto. | Verificar interpretação de uma/duas avaliações e considerar harmonização das mensagens. |
| **4. Dificuldade no estado conflitante** (RF11) | Rótulo factual presente; sem legenda explicativa no detalhe. | Avaliar explicação de empate entre respostas, sem inventar novos resultados ou fórmula. |
| **5. Comparação em telas compactas** (RF12–RF13) | Grade passa a uma coluna em tela pequena. | Observar leitura e alternância entre cartões; considerar apresentação compacta. Não há melhora de legibilidade demonstrada. |
| **6. Percepção da barreira de autenticação** (RF04, RF14) | Consulta sem exigência de sessão nas telas inspecionadas; aviso de conta/e-mail no formulário. | Verificar se o participante entende os diferentes acessos antes do envio. |
| **7. Neutralidade dos critérios** (seções 6 e 8; RF14–RF15) | Legenda de neutralidade em consulta/formulário. | Avaliar se o estudante atribui mérito automaticamente a Dificuldade/Chamada, preservando a diferença entre opinião e fato. |

Após as sessões reais, complementar cada linha com versão anterior, versão do protótipo, referências às observações, ocorrências e limitações. Até então, nenhum obstáculo é classificado como “melhora comprovada”, “melhora parcial” ou “ausência de melhora”.

## 6. Encaminhamentos ao PO e à equipe

### 6.1 Propostas de UX para discussão

Busca unificada, harmonização dos avisos de insuficiência, explicação de conflito e comparação compacta são sugestões a confrontar com os resultados das sessões. Não são defeitos obrigatórios nem autorizações de implementação.

A preservação de rascunho após autenticação é uma proposta adicional. Seu mecanismo, duração e tratamento de dados precisam ser definidos antes de implementar; este documento não escolhe armazenamento nem presume perda de respostas já observada.

### 6.2 Questões de produto e decisões posteriores

1. **Ordenação (RF13, seções 8 e 11):** o percentual de recomendação é a chave aprovada; quantidade decrescente e nome são desempates. Ordenar por didática ou ponderar notas/volume alteraria a regra vigente. Qualquer proposta depende de decisão explícita do PO e atualização da fonte de requisitos.
2. **Oferta e semestre (RF12, RF16–RF17):** a [consulta de professores por disciplina](https://github.com/unb-mds/2026-02-UnDb/blob/e320ee710d2bc6ffe6a5c63633822e848f2aad89/backend/app/repositories/professor_repository.py) filtra `Turma.disciplina_id` e `Turma.ativa`, **sem filtro por `Turma.semestre`**. Logo, a comparação pode incluir turmas ativas de semestres diferentes; não há restrição ao semestre vigente nessa consulta. Perguntas ao PO: deve existir restrição explícita por semestre? Devem aparecer professores com histórico avaliado, mas sem qualquer turma ativa na disciplina? Ambas permanecem pendentes; nenhuma filtragem é alterada nesta entrega.
3. **Comentários na R2 (RF20–RF22):** a R1 inspecionada mantém avaliação estruturada sem texto livre. A [fonte de requisitos atualizada pela #154, commit `5360ff4`](https://github.com/unb-mds/2026-02-UnDb/blob/5360ff4/docs/requisitos.md) já define comentário opcional vinculado à avaliação e moderação humana prévia, além das regras de denúncia e revisão. As perguntas anteriores sobre obrigatoriedade e moderação não permanecem abertas. Esse detalhamento documental não comprova implementação no protótipo da #152; cenários de comentários devem seguir a fonte aprovada quando houver artefato correspondente para avaliação.

## 7. Critérios da issue #153 e pendências

Os três critérios da issue são preservados, sem substituir pesquisa por preparação documental:

- [ ] **Registrar tarefas, observações e limitações da avaliação.** Roteiro e campos de coleta preparados; faltam registros reais de participantes, execução e observações do protótipo identificado.
- [ ] **Comparar os principais obstáculos com o diagnóstico anterior.** Confronto documental/técnico preparado; faltam dados antes/depois que permitam avaliar redução dos obstáculos.
- [x] **Encaminhar mudanças que impliquem regra de produto ao PO.** Questões registradas na seção 6.2; respostas e decisões não são presumidas. O registro não comprova discussão ou aprovação pelo PO.

A equipe deverá registrar participantes e sessões consentidas, preencher a matriz da seção 3.3, comparar os resultados e suas limitações, e então reavaliar os critérios. **Esta entrega não conclui a validação com alunos nem autoriza fechar a #153.**

## 8. Referências

- [Issue #153 — Validar protótipo da jornada com alunos](https://github.com/unb-mds/2026-02-UnDb/issues/153)
- [Issue #148 — Observar a jornada com alunos](https://github.com/unb-mds/2026-02-UnDb/issues/148) e [PR #176 — diagnóstico preliminar](https://github.com/unb-mds/2026-02-UnDb/pull/176)
- [Issue #152 — Prototipar telas principais](https://github.com/unb-mds/2026-02-UnDb/issues/152) e [PR #179 — protótipo navegável](https://github.com/unb-mds/2026-02-UnDb/pull/179)
- [Épico #144 — Melhorar a jornada do aluno](https://github.com/unb-mds/2026-02-UnDb/issues/144)
- [Requisitos](../requisitos.md) — fonte de verdade das regras utilizadas
- [Visão do produto](../visao.md)
