# 📋 Engenharia de Requisitos — G7

Especificação de requisitos do sistema de **Avaliação de Professores e Disciplinas da UnB**,
desenvolvido para a disciplina de Métodos de Desenvolvimento de Software (MDS) 2026/2.

> Este documento é a **fonte de verdade** dos requisitos. O `specs.md` é derivado dele.
> Mudanças de requisito são feitas aqui primeiro, e o `specs.md` regenerado em seguida.

**Estado:** requisitos funcionais e escopo do Release 1 validados com o time.
RNF02 validado pelo PO nesta revisão; os demais requisitos não-funcionais permanecem **propostos**.

---

## 1. Objetivo

Dar a qualquer aluno da UnB acesso à informação sobre professores e disciplinas que hoje
circula apenas em redes sociais informais, permitindo decisão de matrícula fundamentada e
comparável, **independentemente de quantas pessoas ele conheça no curso**.

---

## 2. Origem dos requisitos — pesquisa com usuários

Conversas abertas com **20 a 30 alunos da UnB**, de diferentes semestres, conduzidas antes
da definição de escopo.

### 2.1 Situação atual

O aluno tem três caminhos para saber como é um professor: perguntar no grupo geral da
faculdade, falar com um colega que já cursou, ou cursar uma semana e trancar a matrícula.

### 2.2 Problema identificado

A informação existe, mas **está presa numa rede social informal**. Quem tem veterano
conhecido resolve em uma conversa; quem não tem decide sem base ou paga o custo de uma
semana de semestre. O grupo geral, único canal aberto, exclui na prática três perfis:

- aluno de 2º e 3º semestre, que já escolhe matrícula mas ainda não formou rede;
- aluno introvertido, que não se expõe num grupo de centenas de pessoas;
- aluno de **módulo livre**, que cursa em outro departamento e não tem a quem perguntar.

O terceiro é o mais forte: é o caso em que o boca a boca não funciona em nenhuma hipótese.

### 2.3 Hipóteses não validadas

Registradas para não serem tratadas como fato: que didática e taxa de reprovação sejam os
fatores **decisivos** da escolha. Os alunos citaram ambos, mas o peso relativo não foi medido.

---

## 3. Personas

| Persona | Perfil | Dor principal | Papel no produto |
|---|---|---|---|
| **P1 — Aluno sem rede** | 2º/3º semestre, introvertido, ou cursando módulo livre | Decide o semestre inteiro sem informação | Consome |
| **P2 — Veterano que já se queimou** | 5º semestre em diante, com rede formada | A informação que circula é boato, não dado comparável | Alimenta |

A P2 é quem torna o produto viável: sem ela a base nasce vazia e a P1 não é atendida.

---

## 4. Perfis de usuários (atores)

| Perfil | Descrição | Permissões |
|---|---|---|
| **Visitante** | Usuário anônimo, sem cadastro | Consultar professores, disciplinas e resultados agregados |
| **Estudante** | Usuário cadastrado e autenticado | Tudo do visitante + registrar avaliação |
| **Moderador** | Membro da equipe com privilégio de curadoria | Tudo do estudante + fila de moderação (**Release 2**) |

---

## ⚙️ 5. Requisitos Funcionais (RF)

### Módulo 1 — Identificação e acesso

- **[RF01] Cadastro enxuto:** o sistema deve permitir cadastro solicitando apenas nome,
  e-mail com domínio `@aluno.unb.br` e senha. A conta é criada antes da confirmação do
  endereço, mas somente pode registrar avaliações depois da confirmação por link, conforme
  RF14. Não devem ser solicitados matrícula, CPF ou histórico acadêmico.
- **[RF02] Sessão autenticada:** o sistema deve autenticar o usuário e manter, no servidor,
  uma sessão identificada no navegador por cookie seguro. A sessão deve expirar após sete
  dias consecutivos de inatividade e ser invalidada no logout.
- **[RF03] Avaliação única com substituição:** o sistema deve manter apenas uma avaliação
  por usuário, professor e disciplina. Um novo envio válido para a mesma combinação
  substitui a avaliação anterior, sem criar registro adicional.
- **[RF04] Consulta sem cadastro:** o sistema deve permitir consulta livre a todos os
  resultados agregados sem exigir autenticação.

### Módulo 2 — Busca e navegação

- **[RF05] Busca por professor:** o sistema deve permitir pesquisar professor por nome,
  incluindo nome parcial.
- **[RF06] Busca por disciplina:** o sistema deve permitir pesquisar disciplina por nome ou
  por código.
- **[RF07] Busca entre departamentos:** a busca não deve filtrar por curso ou departamento
  do usuário. Uma disciplina de outro departamento deve ser encontrável e consultável
  normalmente (caso de uso módulo livre).

### Módulo 3 — Consulta de avaliações

- **[RF08] Exibição agregada:** o sistema deve exibir os cinco critérios de avaliação já
  consolidados para um professor em uma disciplina, e não a lista de avaliações individuais.
- **[RF09] Transparência estatística:** toda exibição de resultado agregado deve informar
  quantas avaliações o sustentam.
- **[RF10] Estado vazio explícito:** quando não houver avaliações, o sistema deve comunicar
  a ausência de dados de forma que não possa ser confundida com avaliação negativa.
- **[RF11] Estado conflitante:** para os critérios de natureza factual, quando não houver
  maioria clara entre as respostas, o sistema deve exibir estado "conflitante".

### Módulo 4 — Comparação

- **[RF12] Comparação entre professores:** o sistema deve exibir lado a lado os professores
  que oferecem a mesma disciplina, com seus critérios agregados.
- **[RF13] Ordenação:** a comparação deve ser ordenável pelo percentual de recomendação.

### Módulo 5 — Registro de avaliação

- **[RF14] Registro estruturado:** o sistema deve permitir que um estudante autenticado e
  com e-mail confirmado registre avaliação de um professor em uma disciplina através dos
  cinco critérios da seção 6, sem campo de texto livre.
- **[RF15] Agregação por natureza do critério:** o sistema deve agregar cada critério
  conforme sua natureza, sem misturar regras de fato e de opinião (seção 6).

### Módulo 6 — Dados institucionais

- **[RF16] Importação de professores e disciplinas:** o sistema deve obter dados de
  professores, disciplinas e turmas a partir de páginas públicas do SIGAA.
- **[RF17] Cobertura de todas as unidades com turmas de graduação:** a importação deve
  consultar todas as opções de unidade da página pública de turmas do SIGAA e importar
  as que oferecem turmas de graduação, inclusive departamentos, institutos, faculdades
  e campi. Não se limita aos cursos de interesse imediato do time. Pré-requisito do RF07.
- **[RF19] Log de execução:** cada execução de importação deve registrar sucesso ou falha.

### Módulo 7 — Release 2

- **[RF18] Rotina de atualização:** o sistema deve atualizar os dados importados
  periodicamente.
- **[RF20] Comentários em texto livre:** permitir comentário textual sobre a disciplina.
- **[RF21] Denúncia de conteúdo:** permitir sinalizar avaliação abusiva.
- **[RF22] Fila de moderação:** interface para aprovar ou remover conteúdo denunciado.

---

## 6. Critérios de avaliação — Release 1

| Critério | Formato | Natureza | Agregação |
|---|---|---|---|
| Didática | Nota de 1 a 5 | Opinião | Média |
| Dificuldade | Fácil / Médio / Difícil | Opinião | Moda |
| Chamada | Sim / Não | Fato | Maioria, com estado "conflitante" |
| Material | Não disponibiliza / Ruim / Médio / Bom | Fato + opinião | Maioria para disponibilidade + moda para qualidade |
| Recomenda a matéria | Sim / Não | Opinião | Percentual |

**Escala de didática.** Escolhido 1 a 5. Três níveis concentrariam quase todos os professores
no meio; mais de cinco produzem distinções que o avaliador não sustenta de forma estável.
É também a escala mais familiar ao usuário, o que reduz atrito num produto que depende de
volume de avaliações.

**Métrica de recomendação.** É a métrica-resumo. É a única que permite ordenar, já que os
cinco critérios usam escalas incompatíveis entre si. Também valida as demais: didática baixa
com alto percentual de recomendação indica fator não capturado — insumo para o Release 2.

---

## 🛡️ 7. Requisitos Não-Funcionais (RNF)

> **RNF02 validado pelo PO nesta revisão.** Os demais RNFs continuam propostos.

- **[RNF01] Privacidade do avaliador:** a avaliação não deve ser exibida publicamente de
  forma vinculada à identidade nominal de quem avaliou. O sistema não deve armazenar
  matrícula, CPF ou histórico acadêmico.
- **[RNF02] Proteção contra identificação indireta:** quando um professor tiver poucas
  avaliações em uma disciplina, o resultado agregado pode permitir inferir quem avaliou.
  O sistema só deve exibir critérios agregados a partir de três avaliações por professor
  e disciplina. Abaixo disso, deve informar a quantidade e a insuficiência de dados, sem
  exibir valores dos critérios. O mínimo é uma escolha inicial de produto, não garantia
  empírica de anonimato, e pode ser revisto pelo PO.
- **[RNF03] Segurança de credenciais:** senhas devem ser armazenadas com hash forte;
  comunicação via HTTPS; consultas protegidas contra SQL Injection.
- **[RNF04] Reprodutibilidade em containers:** a aplicação deve subir via `docker compose up`
  sem comandos manuais no sistema do desenvolvedor.
- **[RNF05] Versionamento de schema:** toda alteração do esquema do banco deve ser feita
  por migração versionada e commitada. DDL manual não é permitido.
- **[RNF06] Arquitetura em camadas:** o backend deve separar routers/schemas, lógica de
  negócio, persistência e modelos, sem lógica de negócio dentro do router.
- **[RNF07] Resiliência da importação:** falha em uma fonte ou departamento não deve
  interromper a importação dos demais, e deve ser registrada (RF19).
- **[RNF08] Responsividade:** a interface deve ser utilizável em smartphone, já que a
  consulta acontece tipicamente durante o período de matrícula, fora do computador.

---

## 8. Restrições de produto

Restrições que valem para todo o sistema e não pertencem a um RF isolado.

- **Ordenação:** usar exclusivamente o percentual de recomendação. Não criar índice composto
  ponderando os cinco critérios — não existe fonte que justifique pesos entre eles.
- **Apresentação neutra:** Dificuldade e Chamada **não possuem direção boa ou ruim** e não
  devem receber codificação de valor (vermelho/verde, ícone de alerta, posição em ranking).
  "Difícil" é sinal de matéria séria para parte dos alunos; chamada é desejada por uns e
  evitada por outros. São critérios informativos.
- **Sem campo livre no Release 1:** nenhum campo de texto aberto, para que não exista
  conteúdo a moderar antes da infraestrutura de moderação existir.

---

## 🗺️ 9. Matriz de rastreabilidade por release

| Requisito | Descrição | Release | Estado |
|---|---|---|---|
| RF01–RF04 | Identificação, sessão, substituição sem duplicata, consulta anônima | R1 | Planejado — modelo de acesso validado; envio de e-mail ainda depende das decisões da seção 11 |
| RF05–RF07 | Busca por professor, disciplina e entre departamentos | R1 | Planejado |
| RF08–RF11 | Consulta agregada, transparência, estado vazio e conflitante | R1 | Planejado |
| RF12–RF13 | Comparação e ordenação | R1 | Planejado |
| RF14–RF15 | Registro de avaliação e regras de agregação | R1 | Planejado |
| RF16–RF17, RF19 | Importação manual do SIGAA, cobertura de graduação e log | R1 | Validado localmente; operação inicial manual |
| RF18 | Atualização periódica dos dados importados | R2 | Planejado; agendamento local ainda não configurado |
| RF20–RF22 | Comentários, denúncia e moderação | R2 | Planejado |
| RNF02 | Mínimo de três avaliações para exibição detalhada | R1 | Validado pelo PO; implementação planejada |
| RNF01, RNF03–RNF08 | Privacidade, segurança, containers, camadas, resiliência | R1 e R2 | **Proposto** |

---

## 10. Métricas de sucesso

| Métrica | Definição |
|---|---|
| **Cobertura** | % de professores com pelo menos N avaliações |
| **Adoção** | Avaliações registradas por semestre |
| **Alcance** | Consultas realizadas por semestre |
| **Amplitude** | % de consultas a disciplinas fora do curso do próprio aluno |

Cobertura é a mais crítica: plataforma de avaliação sem massa de dados não responde nada.
O valor de N será definido após o primeiro semestre de uso. Amplitude mede especificamente
se o caso de módulo livre (RF07) está sendo atendido.

---

## 11. Decisões de acesso e pendências

### Identificação, cadastro e sessão — validada para a Release 1

O grupo validou em reunião presencial de 09/09/2026, nas mesas do UAC, o seguinte modelo:

- a consulta de avaliações é pública e não exige conta;
- o registro de avaliações exige conta com e-mail confirmado;
- o cadastro solicita somente nome, e-mail `@aluno.unb.br` e senha;
- a posse do endereço é confirmada por link enviado ao e-mail cadastrado;
- somente quem mantém acesso ao domínio aceito pode concluir o cadastro; ex-alunos sem esse
  acesso e outros vínculos institucionais não são contemplados na Release 1;
- a sessão é mantida no servidor e identificada por valor aleatório em cookie `HttpOnly`,
  `SameSite=Lax` e `Secure` em produção;
- a sessão expira após sete dias consecutivos de inatividade; atividade válida renova esse
  prazo, e o logout invalida a sessão no servidor e remove o cookie do navegador;
- matrícula, CPF e histórico acadêmico não são coletados.

A reunião foi convocada no grupo de WhatsApp da equipe. Participaram Nicolas, Vinicius,
Gabriel, Tiago e Warlley; Yasmin não participou. A decisão vale para a Release 1 e será
reavaliada na validação geral da release, permitindo correções para a Release 2.

### Regras de produto — aprovadas pelo PO em 13/09/2026

Nicolas aprovou explicitamente, na conversa de revisão do repositório:

- Material: maioria para disponibilidade e moda para qualidade; não converter categorias em média numérica.
- Novo envio válido substitui a avaliação anterior para o mesmo usuário/professor/disciplina (RF03).
- Ordenação exclusivamente pelo percentual de recomendação.
- Mínimo inicial de três avaliações por professor/disciplina antes de exibir critérios (RNF02).

Na mesma conversa, Nicolas aprovou também os detalhes abaixo para #40/#51:

- Didática: média com uma casa decimal; recomendação: percentual inteiro. Em ambos,
  arredondamento de metades para cima (half-up).
- Dificuldade: moda; empate escolhe Difícil > Médio > Fácil.
- Chamada e disponibilidade de material: maioria simples; empate exato gera "conflitante".
- Qualidade de material: moda entre respostas que disponibilizam material; empate escolhe
  Bom > Médio > Ruim. Só é exibida se a disponibilidade agregada tiver maioria de "sim".
- Comparação por recomendação decrescente; empate usa quantidade de avaliações decrescente
  e, depois, nome em ordem alfabética. Resultados insuficientes ficam no final, sem percentual artificial.

Essas decisões não validam os demais RNFs nem alteram as pendências de execução e envio de e-mail.

### Contrato de cadastro — aprovado para a Issue #48 em 19/09/2026

- senha entre 8 e 128 caracteres, armazenada com Argon2id;
- confirmação por token opaco aleatório, de uso único, com validade de 24 horas; somente o
  hash do token é persistido;
- cadastro repetido retorna resposta genérica `202`, sem revelar se o e-mail já existe e
  sem alterar a conta existente;
- Resend é o provedor de produção, atrás de uma interface interna; na Release 1, o fluxo é
  exercitado exclusivamente pelo adaptador local sem envio externo;
- o formulário e a API aceitam somente nome, e-mail `@aluno.unb.br` e senha;
- a página de confirmação recebe o token e solicita a mutação por `POST` à API.

O domínio remetente do Resend é uma dependência operacional para envio a usuários reais,
planejada para a Release 2, e não uma mudança no domínio institucional aceito no cadastro.

### Demais decisões pendentes

O modelo de execução do banco foi definido durante a revisão do PR #55, em 11/09/2026:
SQLAlchemy síncrono, Alembic, PostgreSQL e driver `psycopg2`.

| Decisão | Bloqueia | Responsável |
|---|---|---|
| Estratégia de execução/deploy do frontend Next.js (servidor vs export estático) | Configuração definitiva de execução (#36); não bloqueia o scaffold local #29 | Time |
| Valor de N da métrica de cobertura | Apenas a métrica; mínimo de exibição já definido separadamente | PO |
| Execução e operação da coleta em todas as unidades | RF17–RF19; escopo de graduação definido abaixo | Time |

### Escopo de cobertura definido na validação da Release 1

Em 24/09/2026, ficou definido que RF17 abrange todas as opções da página pública de
turmas do SIGAA que tenham ofertas no nível `GRADUAÇÃO`, inclusive institutos,
faculdades e campi. A enumeração deve considerar também opções sem ofertas no período,
para distinguir ausência de turmas de uma unidade não consultada. Outros níveis de
ensino ficaram fora desta decisão. A evidência de execução está em
[`estudos/validacao-release-1-sigaa-2026-09-24.md`](estudos/validacao-release-1-sigaa-2026-09-24.md).

Na preparação da Release 1, o PO definiu que a importação inicial pode ser executada
manualmente no ambiente local, inclusive na apresentação. A atualização periódica do
banco (RF18) passa para a Release 2. O comando de importação e seu registro de sucesso
ou falha (RF19) permanecem na Release 1; não é necessário instalar um agendamento
para lançar a versão 1.0.0.

### Nota — verificação de que o aluno cursou

O escopo original previa impedir avaliação de disciplina não cursada. O histórico de
matrícula por aluno não está disponível em página pública do SIGAA. Confirmada essa
limitação, a garantia do Release 1 passa a ser: identificação do avaliador (RF01–RF02) e
bloqueio de duplicata (RF03). Isso impede spam, mas não impede que alguém avalie professor
que nunca teve. **A limitação é assumida explicitamente**, não contornada por solução
não verificável.

### Nota — viabilidade do scraping

A [POC da #23](estudos/sigaa-poc.md), executada em 13/09/2026, demonstrou coleta HTTP de
108 ofertas do CIC em 2026.2, preservando sessão e controles JSF. Isso comprova o caso
demonstrado, não cobertura total, persistência ou atualização periódica. A integração
persistida é tratada na #25; cobertura e atualização periódica continuam nas #26/#27.

### Decisões da integração institucional — aprovadas em 17/09/2026

Para concluir a Issue #25, o time aprovou o seguinte contrato:

- toda oferta válida do SIGAA é representável, inclusive sem docente ou com múltiplos
  docentes;
- professor possui UUID interno e SIAPE quando a fonte o disponibilizar; sem identificador
  externo, cada ocorrência recebe identidade provisória, explicitamente não confirmada, e
  homônimos nunca são unidos automaticamente;
- turma e professor têm relação muitos-para-muitos. A identidade da turma é composta por
  fonte, unidade, período, componente e código textual da turma; docentes não fazem parte
  dessa identidade;
- unidade preserva o identificador público do SIGAA, o código interno e o nome exibido;
- disciplina preserva UUID interno, identificador público do componente e código acadêmico;
  conflitos entre essas identidades exigem reconciliação explícita;
- reimportação sincroniza o retrato da unidade/período: cria, atualiza e marca como inativas
  as turmas ausentes. Ausências só podem inativar registros quando a coleta completa foi
  validada; uma coleta parcial ou com erro nunca remove nem inativa dados anteriores;
- cada unidade é uma transação independente e cada oferta usa savepoint, de modo que uma
  falha não impeça as demais ofertas ou unidades;
- `sucesso=true` significa execução integral, sem erro nem divergência. O resultado
  estruturado é responsabilidade da #25; agendamento, histórico durável e monitoramento são
  responsabilidade da #26; cobertura de todas as unidades é responsabilidade da #27;
- a API nunca dispara coleta. A #25 entrega leitura institucional mínima; as Issues #44 e
  #45 permanecem responsáveis pela experiência de busca no frontend.

Consultas por nome são parciais, sem distinção de maiúsculas/minúsculas ou acentos. Busca
válida sem correspondência retorna lista vazia; recurso individual inexistente retorna 404;
homônimos são sempre apresentados separadamente.

---

## 12. Fora do escopo do Release 1

| Item | Motivo |
|---|---|
| Avaliação de personalidade do professor | Subjetivo demais e com risco de ataque pessoal |
| Comentários em texto livre e moderação | Release 2 |
| Atualização periódica automática dos dados do SIGAA (RF18) | Release 2; a Release 1 usa importação manual |
| Calouro como usuário primário | É matriculado automaticamente, sem escolha; torna-se usuário no 2º semestre |
| Verificação de que o aluno cursou a disciplina | Dado indisponível publicamente (ver seção 11) |

---

## 13. Rastreabilidade

- **[Documento de visão](visao.md):** síntese derivada do problema, público, valor, escopo,
  métricas e riscos do produto
- **[Board de requisitos (Figma)](https://www.figma.com/board/qs0bvgeJXyfCxYFEDSX9VH/G7---Requisitos--Avalia%C3%A7%C3%A3o-de-Professores-UnB-):**
  pesquisa, personas, Double Diamond, priorização, story map e fluxos de usuário
- **Epic:** `[EPIC] Avaliações (Core do Produto)` (#14)
- **Sub-issues:** #38 a #43 e derivadas do story map
- **Governança:** `skills/governance/project-governance/` define quais decisões exigem
  aprovação humana explícita
