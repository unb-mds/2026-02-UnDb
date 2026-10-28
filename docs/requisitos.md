# 📋 Engenharia de Requisitos — G7

Especificação de requisitos do sistema de **Avaliação de Professores e Disciplinas da UnB**,
desenvolvido para a disciplina de Métodos de Desenvolvimento de Software (MDS) 2026/2.

> Este documento é a **fonte de verdade** dos requisitos. O `specs.md` é derivado dele.
> Mudanças de requisito são feitas aqui primeiro, e o `specs.md` regenerado em seguida.

**Estado:** requisitos funcionais e escopo do Release 1 validados com o time.
RNF02 validado pelo PO nesta revisão; os demais requisitos não-funcionais permanecem **propostos**.
RF20–RF22 detalhados a partir das decisões explícitas do solicitante na discussão da
Issue #154; origem, estado e evolução pendente estão registrados na seção 11.
Este detalhamento não afirma implementação ou homologação das funcionalidades da R2.

---

## 1. Objetivo

Dar a qualquer aluno da UnB acesso à informação sobre professores e disciplinas que hoje
circula apenas em redes sociais informais, permitindo decisão de matrícula fundamentada e
comparável, **independentemente de quantas pessoas ele conheça no curso**.

---

## 2. Origem dos requisitos — pesquisa com usuários

Nós percebemos a necessidade de tornar esse conhecimento acessível sem depender de contatos pessoais. Essa motivação guiou o desenvolvimento do produto.

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
| **Visitante** | Usuário sem autenticação | Consultar professores, disciplinas e resultados agregados; na R2, ler comentários publicados e denunciá-los |
| **Estudante** | Usuário cadastrado e autenticado | Tudo do visitante; registrar avaliação/comentário exige e-mail confirmado; denunciar não exige confirmação |
| **Moderador** | Membro da equipe designado pelo PO, com conta autenticada e e-mail confirmado | Tudo do estudante + fila e ações de moderação da R2; não pode julgar seu próprio comentário ou denúncia |

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
  cinco critérios da seção 6, sem campo de texto livre na Release 1. Na Release 2,
  RF20 acrescenta comentário opcional, sem alterar as escalas ou a agregação dos critérios.
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
- **[RF20] Comentários em texto livre:** permitir comentário opcional associado à
  avaliação única de estudante, professor e disciplina, com leitura pública sem autoria
  identificável e publicação condicionada à moderação vigente, conforme o detalhamento abaixo.
- **[RF21] Denúncia de conteúdo:** permitir que usuários autenticados, com ou sem e-mail
  confirmado, e visitantes denunciem comentários textuais por motivo obrigatório;
  distinguir as origens e suspender a versão ao atingir o limiar aprovado abaixo.
- **[RF22] Fila de moderação:** permitir que moderadores autorizados decidam sobre
  comentários pendentes, denunciados ou suspensos, preservando os critérios estruturados,
  com impedimentos, comunicação e registros privados conforme o detalhamento abaixo.

### RF20 — Regras de comentário

**Estado:** regras de produto aprovadas na discussão da #154; implementação posterior.
**Origem:** decisões R2-DEC-01 a R2-DEC-05 e R2-DEC-12 a R2-DEC-15, na seção 11.

1. O comentário é opcional e pertence à avaliação única do trio
   `(estudante, professor, disciplina)` de RF03, não a uma conversa avulsa da disciplina.
   Publicar, substituir ou retirar seu texto exige autenticação, e-mail confirmado e autoria
   sobre essa avaliação. Não se concede edição ou retirada de texto alheio a outro estudante.
2. Quando informado, o texto deve conter de **1 a 500 caracteres**, desconsiderando espaços
   no início e no fim. Texto vazio, só com espaços ou acima do limite é inválido. A ausência
   do comentário opcional não impede uma avaliação estruturada válida.
3. A associação ao estudante é interna. A consulta pública não expõe nome, e-mail,
   identificador de conta ou vínculo que identifique o autor. Comentários publicados podem
   ser lidos sem cadastro. Isso não autoriza exibir avaliações individuais nem critérios
   agregados abaixo do mínimo de RNF02; aprovação de texto não altera esse requisito.
4. **Nesta etapa, a moderação é humana antes de publicar qualquer novo texto.** O filtro
   de termos aguarda a lista que será definida pelo solicitante. A IA não substitui a
   aprovação humana nesta entrega documental; sua adoção futura depende da evolução
   registrada na seção 11. Toda substituição de texto passa novamente pela moderação
   vigente no momento; um texto anteriormente aprovado não dispensa a revisão do substituto.
5. O moderador deve rejeitar ofensas pessoais, xingamentos, palavrões, ameaças,
   discriminação, exposição de dados pessoais de estudantes/terceiros e spam. Críticas
   acadêmicas negativas são permitidas; discordância do moderador não justifica rejeição.
6. Os cinco critérios válidos são registrados/substituídos normalmente enquanto o texto
   aguarda revisão ou é rejeitado. As ações sobre texto não removem notas, não alteram
   contagens de avaliações e não mudam as fórmulas de agregação.
7. Ao enviar novo texto, a versão anterior aprovada permanece pública até a aprovação do
   substituto, **desde que não esteja suspensa ou removida**. Suspensão não é contornada
   pelo envio de uma edição. Se o substituto for rejeitado, não substitui a versão anterior
   nem muda seu estado; seu próprio texto é descartado.
8. Reenviar somente os critérios, sem novo comentário, mantém o texto existente. A retirada
   exige ação explícita do autor e preserva os cinco critérios. Ela retira o texto público,
   cancela eventual substituto pendente e encerra denúncias abertas como `conteúdo retirado`,
   sem julgar sua procedência. Um moderador não pode restaurar texto retirado pelo autor.
9. Ao aprovar um substituto, a versão anterior é substituída e seu texto não é conservado.
   Suas denúncias abertas são encerradas como `versão substituída`, sem transferir motivos,
   contagem ou suspensão para o novo texto. Uma versão retirada/removida só pode voltar
   como um novo texto submetido à moderação, não por restauração da versão retirada.
10. O autor acompanha na aplicação o estado do próprio comentário, incluindo a distinção
    entre versão pública e substituto em revisão. Isso não dá acesso a identidades de
    denunciantes ou aos registros privados de moderação.

### RF21 — Regras de denúncia

**Estado:** regras de produto aprovadas na discussão da #154; implementação posterior.
**Origem:** R2-DEC-06 a R2-DEC-08 e R2-DEC-11 a R2-DEC-15, na seção 11.

1. A denúncia tem como alvo uma **versão do comentário textual**; os cinco critérios
   estruturados não são denunciáveis por esse fluxo. Usuários autenticados podem denunciar
   com ou sem confirmação de e-mail. Visitantes sem login também podem denunciar.
2. Cada denúncia exige um motivo da lista fechada correspondente à política de RF20:
   `ofensa pessoal`, `xingamento`, `palavrão`, `ameaça`, `discriminação`,
   `exposição de dados pessoais` ou `spam`. Não há justificativa textual livre.
3. Para autenticados, existe no máximo **uma denúncia em aberto por conta e versão**.
   A repetição não cria nova denúncia aberta nem aumenta a contagem. Visitantes podem
   repetir; suas denúncias são agrupadas por comentário/versão, sem garantia de uma pessoa
   diferente por registro. Não há deduplicação por navegador aprovada nesta etapa.
4. A fila distingue denúncias de contas autenticadas das feitas sem autenticação,
   apresentando separadamente seus registros/contagens para análise humana. A origem
   autenticada não classifica automaticamente uma denúncia como verdadeira, nem a origem
   anônima a classifica como abusiva. Registros de denúncia não são públicos.
5. O limiar inicial é **50 denúncias em aberto de contas autenticadas distintas sobre a
   mesma versão publicada**. Contas sem e-mail confirmado contam. Denúncias anônimas,
   duplicadas e encerradas não contam. Abaixo de 50, a denúncia por si só não suspende o
   texto; a atuação humana continua disponível conforme RF22.
6. Ao atingir o limiar, a versão fica `suspensa`, deixa de ser exibida publicamente e é
   encaminhada à revisão humana. Seu texto permanece disponível internamente para revisão.
   Esse evento não remove os cinco critérios nem representa decisão de procedência.
7. O registro válido retorna confirmação tanto ao autenticado quanto ao visitante. Não há
   painel ou protocolo de acompanhamento posterior da denúncia em tempo real nesta etapa.
   Ao decidir sobre a versão, RF22 encerra as denúncias relacionadas. Retirada e substituição
   seguem os motivos de encerramento específicos de RF20.
8. Na suspensão pelo limiar **ou na remoção humana de um comentário denunciado**, as contas
   com denúncia aberta relacionada recebem agradecimento na aplicação. A mensagem fica
   disponível até a primeira exibição e é apagada depois; não depende de o usuário estar
   conectado no momento da ação. Não revela autor ou outros denunciantes. Visitantes não
   recebem acompanhamento posterior. Retirada pelo autor e rejeição de outro texto não
   disparam agradecimento.

### RF22 — Regras de moderação

**Estado:** regras de produto aprovadas na discussão da #154; implementação posterior.
**Origem:** R2-DEC-04, R2-DEC-09 a R2-DEC-15, na seção 11.

1. O PO designa e remove a permissão de moderador entre membros da equipe com conta
   autenticada e e-mail confirmado. A fila e suas operações são restritas a essa permissão.
   Usuário comum, visitante ou conta sem a permissão não pode moderar.
2. A fila inclui textos novos/substitutos pendentes de aprovação e versões denunciadas ou
   suspensas. O moderador pode aprovar/rejeitar pendentes, manter/remover da exibição pública
   textos denunciados e restaurar/remover da exibição pública textos suspensos. A aprovação
   prévia humana não se limita a conteúdo denunciado.
3. O moderador não pode julgar seu próprio comentário nem um caso com denúncia sua. Outro
   moderador deve decidir; sem outro disponível, o caso permanece pendente e uma suspensão
   existente é preservada. A permissão de curadoria não elimina esse impedimento.
4. Manter/restaurar texto após análise de denúncias improcedentes encerra essas denúncias
   sem alterar os critérios. Remover encerra as denúncias relacionadas e impede a exibição
   do texto. A restauração se aplica à versão suspensa ainda disponível, não a versões
   retiradas pelo autor, substituídas ou já descartadas.
5. Apenas denúncias e decisões de moderação exigem registros de auditoria nesta etapa,
   com referência à versão, data/hora, ator interno quando existir, mudança de estado e
   motivo. Decisões exigem motivo registrado. Não se exige um histórico de auditoria separado
   para toda publicação, edição ou retirada; os estados e vínculos necessários aos fluxos
   ainda devem ser mantidos conforme as regras de retenção.
6. Esses registros são privados. Moderadores podem consultar textos necessários à análise,
   registros e nome/e-mail dos autores e denunciantes autenticados. Visitantes denunciantes
   não têm identidade cadastrada. Acesso interno não autoriza expor identidades ao público,
   ao autor do comentário ou a outros denunciantes.

### Estados, transições e retenção de RF20–RF22

Os nomes abaixo descrevem comportamentos de produto, sem impor enums, tabelas ou endpoints.
Uma versão em revisão pode coexistir com a versão publicada anterior; os estados são
atribuídos a cada versão, não compartilhados automaticamente entre versões.

| Origem | Evento/ator autorizado | Resultado e efeito |
|---|---|---|
| Sem texto / nova versão | Autor envia texto válido | `pendente`; sem publicação do novo texto |
| `pendente` | Moderador aprova | `publicado`; se substituto, encerra denúncias anteriores e descarta texto substituído |
| `pendente` | Moderador rejeita | `rejeitado`; texto rejeitado não é conservado; versão anterior mantém seu estado |
| `publicado` | Denúncia abaixo do limiar | Mantém estado; entra na fila com denúncias separadas por origem |
| `publicado` | 50 contas distintas com denúncia aberta da versão | `suspenso`; texto oculto publicamente e revisão humana |
| `publicado` denunciado | Moderador mantém | `publicado`; denúncias analisadas são encerradas |
| `suspenso` | Moderador restaura | `publicado`; denúncias analisadas são encerradas |
| `publicado` denunciado / `suspenso` | Moderador remove | `removido`; sem exibição pública; critérios preservados |
| Texto existente e eventual substituto pendente | Autor retira | `retirado`; cancela substituto e encerra denúncias sem julgamento |
| Versão anterior | Substituto aprovado | `substituído`; denúncias não passam para a nova versão |

Denúncias têm estado `em aberto` enquanto aguardam decisão sobre a versão. O encerramento
decorre de decisão humana, retirada pelo autor ou substituição aprovada, com o motivo
correspondente. **Encerrar não significa manter um registro arquivado da denúncia:** após
o encerramento ela não é conservada. O registro privado da decisão tem retenção própria.

| Informação | Retenção aprovada |
|---|---|
| Texto pendente, publicado ou suspenso | Disponível enquanto necessário ao estado vigente; suspensão conserva texto para revisão |
| Texto rejeitado | Não conservar após rejeição |
| Texto substituído | Não conservar após aprovação do substituto; manter anterior enquanto substituto ainda está pendente |
| Texto retirado pelo autor ou removido pelo moderador | Uma semana após retirada/remoção, apenas internamente; descartar ao final |
| Denúncia encerrada | Não conservar após encerramento |
| Registro de decisão de moderação | Uma semana após decisão, apenas internamente; descartar ao final |
| Agradecimento | Conservar até primeira exibição na aplicação e apagar depois, conforme esclarecimento da resposta 26 |

Uma semana corresponde a sete dias contados a partir do evento indicado. Descartar texto
inclui não conservar cópias desse texto nos registros de decisão; estes podem manter a
referência da versão e o motivo durante seu próprio prazo. Não há retenção permanente de
conteúdo ou denúncias encerradas aprovada por estas regras.

### Fluxos alternativos e condições de erro

| Situação | Comportamento exigido |
|---|---|
| Autor sem sessão ou sem e-mail confirmado | Não publicar/substituir/retirar texto; consulta pública continua disponível |
| Estudante tenta editar/retirar texto alheio | Negar a operação; não alterar texto ou critérios |
| Texto vazio/só espaços/acima de 500 caracteres | Informar invalidade do texto; não publicar esse texto nem impedir critérios independentemente válidos |
| Ausência de comentário no reenvio | Preservar texto existente, sem confundir ausência com retirada |
| Motivo ausente ou fora da lista de RF21 | Não registrar denúncia inválida; informar que é necessário um motivo permitido |
| Denúncia autenticada duplicada em aberto | Informar existência de denúncia aberta, sem duplicar registro/contagem |
| Conteúdo inexistente ou versão já retirada/substituída/descartada | Não aplicar denúncia/decisão à nova versão ou aos critérios; informar indisponibilidade do alvo |
| Conta sem permissão de moderação ou com impedimento | Negar decisão; manter estado do caso até atuação de outro moderador autorizado |
| Transição incompatível com estado corrente | Não executar a transição; informar estado inválido, sem restaurar texto descartado |
| Fila vazia | Informar ausência de itens pendentes, sem confundir com falha de consulta |

Mensagens e contratos técnicos devem distinguir esses casos; códigos HTTP, rotas e schema
serão definidos nas issues de implementação, não por este detalhamento documental.

### Critérios de aceitação de RF20–RF22

| ID | Cenário verificável | Origem |
|---|---|---|
| AC20-01 | Conta confirmada envia avaliação com texto de 1/500 caracteres; texto aguarda aprovação e os cinco critérios válidos são registrados | R2-DEC-01/02/04 |
| AC20-02 | Texto com 0/501 caracteres após desconsiderar espaços não é publicado; omitir comentário não impede avaliação válida | R2-DEC-01/02 |
| AC20-03 | Visitante lê somente texto publicado, sem nome/e-mail/identificador do autor ou valores individuais dos cinco critérios | R2-DEC-01/03; RF08/RNF02 |
| AC20-04 | Substituto aguarda nova revisão; anterior continua público se não suspenso/removido; rejeição não altera seu estado e descarta o substituto rejeitado | R2-DEC-04/05 |
| AC20-05 | Reenvio apenas de critérios mantém texto; retirada explícita cancela substituto e preserva critérios | R2-DEC-05/12 |
| AC20-06 | Crítica acadêmica negativa não é rejeitada por discordância; as categorias proibidas são avaliadas pela moderação humana vigente | R2-DEC-03/04 |
| AC21-01 | Visitante e conta com e-mail não confirmado denunciam com motivo permitido e recebem confirmação; motivo inválido não gera denúncia | R2-DEC-06/07 |
| AC21-02 | Mesma conta não cria segunda denúncia aberta da versão; relatos de visitantes podem repetir e são separados dos autenticados | R2-DEC-07 |
| AC21-03 | 49 contas distintas não suspendem por limiar; a 50ª suspende; relatos anônimos, duplicados ou encerrados não aumentam esse total | R2-DEC-08 |
| AC21-04 | Denúncia de versão substituída não é transferida; retirada/substituição encerra relatos sem julgá-los procedentes | R2-DEC-12 |
| AC21-05 | Suspensão pelo limiar ou remoção humana oferece agradecimento a denunciantes autenticados relacionados, inclusive no próximo acesso; primeira exibição apaga a mensagem | R2-DEC-11/15 |
| AC22-01 | PO concede/retira permissão; conta sem permissão não decide; moderador impedido não julga caso próprio | R2-DEC-09/10 |
| AC22-02 | Pendentes podem ser aprovados/rejeitados; denunciados mantidos/removidos; suspensos restaurados/removidos; nenhuma ação modifica os cinco critérios | R2-DEC-04/10 |
| AC22-03 | Sem moderador elegível, caso permanece pendente; texto retirado pelo autor não pode ser restaurado | R2-DEC-10/12 |
| AC22-04 | Fila separa origens; registros e identidades internas são inacessíveis publicamente; moderador autorizado consulta nome/e-mail de usuários envolvidos | R2-DEC-07/13 |
| AC22-05 | Decisão registra motivo, ator, versão, data/hora e transição; não arquiva denúncia encerrada nem copia texto rejeitado/substituído | R2-DEC-13/14 |
| AC22-06 | Ao completar sete dias, texto retirado/removido e registro de decisão não são conservados; pendente/suspenso permanece disponível para revisão | R2-DEC-14 |

Esses cenários orientam a verificação futura (#163). Sua presença não afirma que testes
funcionais foram implementados ou executados pela #154.

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
| RF20–RF22 | Comentários, denúncia e moderação | R2 | Regras detalhadas e aprovadas pelo solicitante na #154; implementação/homologação pendentes; filtro e IA não ativados |
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

### Decisões de comentários, denúncia e moderação — Issue #154

**Fonte de aprovação:** respostas humanas explícitas do solicitante aos blocos de perguntas
1–27 na sessão de esclarecimento da [Issue #154](https://github.com/unb-mds/2026-02-UnDb/issues/154),
vinculada à [Epic #145](https://github.com/unb-mds/2026-02-UnDb/issues/145). Os números
de resposta abaixo identificam a origem na conversa; não são comentários já publicados
no GitHub nem decisões atribuídas a outra pessoa nominalmente. As regras estão detalhadas
na seção 5, que permanece sua fonte canônica.

O diagnóstico de origem são AMB-002/003/004 da auditoria #149. Suas sugestões não constituem
aprovação: somente as alternativas expressamente escolhidas e os esclarecimentos do
solicitante foram incorporados. A resposta 7 substitui a exigência inicial de filtro
automático da resposta 4 pelo fluxo exclusivamente humano enquanto a lista não estiver
definida. A resposta 26 esclarece a retenção do agradecimento inicialmente indicada como
`não guarda` na resposta 25: conservar até a primeira exibição e apagar depois.

| Decisão | Estado | Regra aprovada / origem na sessão |
|---|---|---|
| R2-DEC-01 | Aprovada | Comentário opcional da avaliação única estudante/professor/disciplina; vínculo interno e autoria pública anônima (respostas 1–3) |
| R2-DEC-02 | Aprovada | 1–500 caracteres quando preenchido, desconsiderando espaços nas extremidades; critérios válidos independem do texto (8/11) |
| R2-DEC-03 | Aprovada | Leitura pública; política de conteúdo inclui ofensas, xingamentos, palavrões, ameaças, discriminação, dados pessoais e spam; crítica acadêmica negativa permitida (3/12) |
| R2-DEC-04 | Aprovada | Aprovação humana prévia nesta etapa; toda substituição passa pela moderação vigente; filtro aguarda lista e IA é objetivo futuro condicionado (4/7/18 e esclarecimento final após 25) |
| R2-DEC-05 | Aprovada | Anterior aprovado permanece durante revisão do substituto; rejeição não o substitui; autor pode retirar apenas texto (9/10) |
| R2-DEC-06 | Aprovada | Apenas texto é denunciável; conta autenticada confirmada ou não e visitante sem login podem denunciar (2/5/6) |
| R2-DEC-07 | Aprovada | Motivo fechado obrigatório sem justificativa livre; uma denúncia aberta por conta/versão; visitantes podem repetir, com separação de origens na fila (13/14) |
| R2-DEC-08 | Aprovada | Suspender com 50 contas autenticadas distintas com denúncia aberta da mesma versão; não contar anônimas/encerradas; contas não confirmadas contam (15/16) |
| R2-DEC-09 | Aprovada | PO concede/retira papel de moderador de membros da equipe com conta autenticada e confirmada (17) |
| R2-DEC-10 | Aprovada | Aprovar/rejeitar pendente, manter/remover denunciado, restaurar/remover suspenso; preservar critérios; impedimento de julgar comentário/denúncia próprios (18/19) |
| R2-DEC-11 | Aprovada | Autor acompanha próprio comentário; denunciante recebe confirmação sem acompanhamento em tempo real; agradecer a autenticados na suspensão ou remoção humana de denunciado (20/21) |
| R2-DEC-12 | Aprovada | Reenvio sem texto mantém comentário; retirada cancela substituto e encerra denúncias sem julgamento; substituição encerra denúncias antigas sem transferência (22) |
| R2-DEC-13 | Aprovada | Auditoria apenas de denúncias/decisões, privada; decisão registra motivo; moderador pode consultar nome/e-mail dos envolvidos autenticados (23/24) |
| R2-DEC-14 | Aprovada | Não conservar textos rejeitados/substituídos nem denúncias encerradas; textos retirados por autor/moderador e decisões por uma semana (25/27) |
| R2-DEC-15 | Aprovada | Agradecimento na aplicação disponível até primeira exibição; apagar depois (26) |

**Pendências e limites de evolução:**

| Item | Estado | Responsável / efeito |
|---|---|---|
| Lista de termos proibidos do filtro | Decisão pendente | Solicitante definirá depois; bloqueia ativação do filtro, não a moderação humana |
| Correspondência do filtro futuro | Aprovada, não ativada | Palavras/expressões completas, ignorando maiúsculas e acentos (resposta 7); sem promessa de detectar toda forma de disfarce |
| IA sem aprovação humana prévia | Objetivo futuro condicionado; não aprovado como fluxo atual | Viabilidade e validação posterior antes de substituir humanos; toda edição continua sujeita ao mecanismo vigente |
| Modelo de dados, rotas, códigos HTTP, concessão operacional do papel e descarte programado | Detalhamento técnico pendente | #156/#160/#161, conforme requisitos e governança; esta issue não aprova schema, biblioteca ou provedor |
| Reconhecimento de autoria de denúncia sem autenticação | Limitação do fluxo aprovado | Não há identidade de conta para visitantes; não prometer detecção automática de todo impedimento pessoal nem introduzir coleta de identidade por suposição. A proibição de julgar caso próprio permanece |
| Sugestão antiga de ocultação após 5 denúncias | Sugestão não adotada | Limiar aprovado é 50 contas autenticadas distintas; não aplicar o exemplo da #149 |
| Comentários avulsos, denúncia dos cinco critérios e arquivo permanente de denúncias | Fora do escopo aprovado | RF20 vincula à avaliação, RF21 restringe a texto e R2-DEC-14 determina descarte |

A aprovação destas regras específicas não promove RNF01 nem os demais RNFs propostos,
não aprova automaticamente ADRs, não altera as escalas/agregação e não comprova entrega
de aplicação. As issues dependentes #156/#159/#160/#161/#162/#163 devem consumir estas
decisões; mudanças substanciais de dados/arquitetura mantêm sua aprovação própria.

### Continuidade da busca no acesso — Issue #155

Na reavaliação de 27–28/10/2026, o solicitante autorizou nesta tarefa a ampliação restrita do destino
de retorno já entregue na #158: a rota interna de avaliação pode carregar também
tipo de busca, termo e ordenação. O contexto deve permanecer independente em cada
link de cadastro/confirmação, inclusive entre abas, sem guardar credenciais ou
respostas do formulário. Destinos antigos sem contexto continuam válidos.

O contrato aprovado permite somente `busca`, `q` e `ordem` na query de `return_to`,
com até 2.048 caracteres no destino completo e validação no frontend e no backend.
Não autoriza URLs externas, fragmentos, chaves extras/duplicadas, novas regras de
sessão ou preservação de rascunho. RF01/RF02/RF14 e as escalas permanecem vigentes.

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
- **[Auditoria de clareza e rastreabilidade (Issue #149)](estudos/auditoria-requisitos-issue-149.md):**
  auditoria de lacunas, termos vagos, estados pós-Release 1 e decisões pendentes de produto
- **[Issue #154](https://github.com/unb-mds/2026-02-UnDb/issues/154) / [Epic #145](https://github.com/unb-mds/2026-02-UnDb/issues/145):**
  detalhamento de RF20–RF22, com decisões humanas desta sessão registradas na seção 11
- **[Board de requisitos (Figma)](https://www.figma.com/board/qs0bvgeJXyfCxYFEDSX9VH/G7---Requisitos--Avalia%C3%A7%C3%A3o-de-Professores-UnB-):**
  pesquisa, personas, Double Diamond, priorização, story map e fluxos de usuário
- **Epic:** `[EPIC] Avaliações (Core do Produto)` (#14)
- **Sub-issues:** #38 a #43 e derivadas do story map
- **Governança:** `skills/governance/project-governance/` define quais decisões exigem
  aprovação humana explícita
