# Mapeamento do Portal Público do SIGAA — Issue #22

**Data do levantamento:** 13/09/2026  
**Escopo:** RF16–RF17 — professores, disciplinas, turmas e cobertura por departamento/unidade.  
**Objetivo:** documentar as fontes públicas e o caminho de navegação necessários para orientar o protótipo da Issue #23 e o modelo da Issue #24.

> Este documento é um levantamento de fontes e comportamento observado. Ele **não** define o modelo de dados da aplicação e **não** comprova, por si só, a viabilidade completa do scraper. Essas responsabilidades permanecem nas Issues #23 e #24.

---

## 1. Resultado resumido

O Portal Público do SIGAA da UnB disponibiliza, sem autenticação, páginas para:

- enumerar centros/unidades e chegar aos respectivos portais;
- listar docentes vinculados a uma unidade;
- listar componentes curriculares vinculados a uma unidade;
- consultar o perfil público e as disciplinas de um docente;
- consultar detalhes públicos de componentes curriculares;
- consultar turmas por nível, unidade e período.

Para RF17, a rota mais útil encontrada para iniciar a enumeração é a lista pública de centros/unidades. Na data do levantamento, ela informava **95 centros/unidades especializadas** e expunha links para portais com um parâmetro numérico `id`.

Para RF16, os dados não estão concentrados em uma única página: docentes, componentes e turmas precisam ser relacionados a partir de páginas diferentes.

O ponto de maior risco técnico está na consulta de turmas. A investigação complementar de 13/09/2026 executou uma busca pública do CIC em 2026.2, retornando 108 turmas em 57 agrupamentos de componentes, e observou sessão, renovação de ViewState e detalhes de componente (seção 13). O relato externo de 2023 continua sendo evidência histórica, não prova da execução atual. Os controles devem ser relidos pela #23, sem tratar valores observados como contrato estável.

---

## 2. Páginas e rotas públicas relevantes

| Finalidade | URL / padrão | Parâmetros relevantes | Observação |
|---|---|---|---|
| Portal Público | `https://sigaa.unb.br/sigaa/public/home.jsf` | — | Entrada principal; não exige login |
| Lista de centros/unidades | `https://sigaa.unb.br/sigaa/public/centro/lista.jsf?aba=p-academico` | `aba=p-academico` | Ponto de partida para enumerar unidades |
| Busca geral de docentes | `https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf` | formulário | Permite busca por nome e departamento |
| Portal de departamento/unidade | `https://sigaa.unb.br/sigaa/public/departamento/portal.jsf?id=<ID>&lc=pt_BR` | `id`, `lc` | Exemplo CIC: `id=508` |
| Docentes da unidade | `https://sigaa.unb.br/sigaa/public/departamento/professores.jsf?id=<ID>` | `id` | Lista docentes ligados à unidade |
| Componentes da unidade | `https://sigaa.unb.br/sigaa/public/departamento/componentes.jsf?id=<ID>` | `id` | Mistura disciplinas, atividades e módulos |
| Perfil público do docente | `https://sigaa.unb.br/sigaa/public/docente/portal.jsf?siape=<SIAPE>` | `siape` | Identificador público do docente na URL |
| Disciplinas do docente | `https://sigaa.unb.br/sigaa/public/docente/disciplinas.jsf?siape=<SIAPE>` | `siape` | Agrupadas por período |
| Busca geral de componentes | `https://sigaa.unb.br/sigaa/public/componentes/busca_componentes.jsf?nivel=S` | `nivel` + formulário | Busca por tipo, código, nome e unidade responsável |
| Detalhe de componente | `https://sigaa.unb.br/sigaa/link/public/ensino/visualizarComponente/<ID_COMPONENTE>` | ID na própria rota | Exibe metadados detalhados |
| Busca de turmas | `https://sigaa.unb.br/sigaa/public/turmas/listar.jsf` | formulário JSF | Consulta por nível, unidade e ano/período |
| Turmas/comunidades publicadas | `https://sigaa.unb.br/sigaa/public/cursosabertos.jsf?aba=p-ensino` | `aba=p-ensino` + formulário | Útil como fonte auxiliar, não como prova de cobertura total |

Exemplo rastreável: docentes do CIC → “Ver página” (`siape=1223368`) → “Disciplinas Ministradas” → CIC0108 → `visualizarComponente/178391` → redirect para `public/componentes/resumo.jsf`, acessado com sucesso na investigação complementar. Para turmas: Portal Público → link `listar.jsf?aba=p-ensino` → selecionar nível/unidade/ano/período → “Buscar” → agrupamento do componente → comando de detalhe. Os POSTs observados estão na seção 13.

---

## 3. Caminho para enumerar departamentos/unidades — RF17

### Caminho recomendado para o protótipo

1. Acessar `public/centro/lista.jsf?aba=p-academico`.
2. Extrair cada link que leva a `public/departamento/portal.jsf?id=<ID>`.
3. Registrar pelo menos:
   - `id` público da unidade;
   - sigla, quando disponível;
   - nome;
   - URL do portal.
4. Para cada `id`, acessar:
   - `/departamento/professores.jsf?id=<ID>`;
   - `/departamento/componentes.jsf?id=<ID>`.
5. Para turmas, confrontar os IDs com os valores do formulário de `public/turmas/listar.jsf`; a correspondência foi observada para CIC (`508`), não para todo o conjunto.
6. Registrar unidades sem docentes, componentes ou turmas, em vez de descartá-las silenciosamente.

### Observação de cobertura

Na data do levantamento, a lista pública apresentava **95 centros/unidades especializadas**.

Esse número **não deve ser interpretado automaticamente como “95 departamentos acadêmicos”**. A lista inclui diferentes tipos de unidade institucional, como institutos, faculdades, centros e outras estruturas administrativas/acadêmicas. Portanto:

- ela é uma boa fonte para iniciar a enumeração;
- a Issue #23 deve verificar quais entradas efetivamente expõem os dados acadêmicos necessários;
- a taxonomia pública é insumo para verificar RF17, não uma redefinição de “todos os departamentos”; diferenças entre listas e eventuais exclusões precisam ser justificadas e submetidas ao time quando afetarem escopo;
- `cursosabertos.jsf` não deve ser usado sozinho para determinar a cobertura, pois representa turmas/comunidades publicadas e não necessariamente toda a estrutura institucional.

### Paginação observada

Não foi observada paginação na extração textual das páginas verificadas abaixo:

- lista de centros/unidades: contador de 95 na representação consultada; não é contagem validada de IDs únicos;
- docentes do CIC (`id=508`): 50 docentes em uma página;
- componentes do CIC (`id=508`): 399 componentes em uma página.

Na busca real de turmas CIC/Graduação/2026.2, foram contadas 108 linhas de dados, correspondentes ao total de 108 informado no rodapé, numa única resposta HTML. Foram inspecionados links, comandos JSF, inputs ocultos, selects e atributos: não havia controles de próxima/anterior, números de página, tamanho de página ou limite declarado nesse resultado. Os 57 comandos JSF da tabela abrem detalhes de componentes, não outras páginas de resultados. Isso documenta a navegação desta consulta, não prova ausência universal de paginação ou de limite interno; a #23 deve revalidar outros cenários.

A validação consultou também as entradas das buscas gerais de docentes, componentes e turmas/comunidades, mas não submeteu esses formulários nem verificou paginação dos seus resultados. São rotas auxiliares: o caminho documentado usa listagens por unidade e detalhes via perfil docente ou resultado de turmas. O controle “Ver” da listagem de componentes não foi executado; o comando de detalhe na tabela de turmas foi (seção 13). A ausência de paginação na representação textual das listagens não prova ausência de controles no HTML ou após interação. A lista de centros consultada pelo navegador de pesquisa veio de cache anterior (seção 12).

---

## 4. Campos disponíveis

### 4.1 Departamento/unidade

No portal de departamento/unidade podem aparecer:

- identificador público `id` na URL;
- sigla;
- nome;
- chefia/responsável;
- telefone;
- endereço ou informações de contato, quando preenchidos;
- links para corpo docente;
- links para componentes curriculares.

Nem todos os campos administrativos são necessários ao produto. Para a integração RF16–RF17, `id`, nome/sigla e relacionamento com docentes/componentes são os dados mais importantes observados.

### 4.2 Professor/docente

Na listagem de docentes da unidade foram observados:

- nome;
- vínculo/categoria, por exemplo permanente, substituto ou visitante;
- titulação;
- resumo de formação, quando informado;
- link Lattes, quando informado;
- link para página pública do docente.

No perfil do docente podem aparecer:

- `siape` na URL pública;
- nome;
- departamento/unidade;
- descrição pessoal;
- formação acadêmica;
- formação profissional;
- áreas de interesse;
- currículo Lattes;
- endereço profissional;
- sala;
- telefone;
- e-mail.

Vários campos de perfil podem estar como **“não informado”**. Sua presença não deve ser presumida.

### 4.3 Disciplina/componente curricular

Na página de componentes de uma unidade foram observados:

- tipo do componente;
- código;
- nome;
- carga horária;
- link “Ver” para detalhes.

A página inclui mais de um tipo de componente. No exemplo analisado aparecem seções como:

- `ATIVIDADE`;
- `DISCIPLINA`;
- `MÓDULO`.

Logo, para RF16, não é correto tratar toda linha dessa página como disciplina. O scraper deve identificar/filtrar o tipo correspondente.

Na investigação complementar, o link atual de CIC0108 (`visualizarComponente/178391`) retornou 302 para `public/componentes/resumo.jsf`, seguido de HTTP 200. Foram confirmados os campos abaixo; o Cache miss da primeira validação foi uma limitação daquela ferramenta, superada pelo acesso direto:

- identificador interno numérico na URL;
- tipo;
- unidade responsável;
- código;
- nome;
- carga horária teórica;
- carga horária prática;
- carga horária EAD;
- carga horária total;
- pré-requisitos;
- correquisitos;
- equivalências;
- ementa;
- outras configurações acadêmicas do componente.

### 4.4 Turma

A página atual de consulta de turmas apresenta como entradas:

- nível de ensino;
- unidade;
- ano;
- período.

Na resposta atual da consulta CIC/Graduação/2026.2 foram observados os cabeçalhos:

- código da turma;
- ano/período;
- docente;
- horário;
- quantidade de vagas ofertadas;
- quantidade de vagas ocupadas;
- local;

A associação ao componente está no agrupador precedente (`tr.agrupador`), que contém código/nome e comando JSF com ID numérico do componente. As linhas de turma seguintes pertencem a esse agrupamento até o próximo agrupador. Exemplo: CIC0002, ID `177942`, turma `01`, período `2026.2`. O detalhe acionado confirmou código e nome do componente.

Há sete cabeçalhos; “Horário” tem `colspan="2"`, e cada linha tem oito células. O horário inclui código, eventualmente datas e popup com dias/horas legíveis. Docentes aparecem como nome e carga horária, podendo haver mais de um na mesma célula. Exemplos, atributos e limites de identidade estão na seção 13. A saída de 2023 não mostrava o vínculo ao componente; a evidência atual acima é independente dela.

---

## 5. Relacionamentos encontrados

| Origem | Destino | Como relacionar |
|---|---|---|
| Unidade | Docente | `/departamento/professores.jsf?id=<ID>` |
| Unidade | Componente | `/departamento/componentes.jsf?id=<ID>` |
| Docente | Unidade | perfil público informa o departamento; `siape` identifica a página do docente |
| Docente | Disciplina | `/docente/disciplinas.jsf?siape=<SIAPE>`, agrupada por período |
| Unidade | Turma | unidade é um dos parâmetros do formulário de busca de turmas |
| Turma | Disciplina | Agrupador com código/nome e comando JSF contendo ID do componente; detalhe conferido |
| Turma | Docente | Texto na célula `td.nome`, com nome(s) e carga(s) horária(s); sem link/SIAPE observado |
| Componente | Unidade | Listagem por unidade e campo Unidade Responsável nos detalhes CIC0108 e CIC0002 |

### Identificadores públicos úteis observados

- **unidade/departamento:** `id` numérico na URL;
- **docente:** `siape` na URL;
- **componente:** código acadêmico e um ID numérico usado na rota de detalhe;
- **turma:** nenhum identificador público estável, independente e reutilizável foi confirmado neste levantamento.

### Limitação importante para o relacionamento turma ↔ docente

Nas 108 linhas observadas não há links ou inputs; o HTML da resposta não contém `siape`. A célula do docente contém somente nome(s) e carga(s) horária(s), sem identificador inequívoco encontrado. Relacionar esse texto aos perfis por nome é uma inferência sujeita a homônimos, não uma associação validada.

Essa limitação não deve ser escondida dentro do scraper. A #23 deve verificar sua ocorrência em outros casos; a estratégia de identidade/persistência pertence à #24.

---

## 6. JSF, ViewState, formulário e postback

### O que foi confirmado no estado atual

As páginas principais de consulta do Portal Público continuam usando rotas `.jsf`, incluindo:

- busca de docentes;
- busca de componentes;
- busca de turmas;
- páginas de departamento;
- páginas de docente.

A busca atual de turmas continua solicitando:

- nível;
- unidade;
- ano;
- período.

A extensão `.jsf`, isoladamente, é apenas indício. Na validação de 13/09/2026, um GET direto, sem login, retornou HTTP 200 e permitiu inspecionar o HTML de `https://sigaa.unb.br/sigaa/public/turmas/listar.jsf`:

- formulário `id/name="formTurma"`, `method="post"`, `action="/sigaa/public/turmas/listar.jsf"`, `enctype="application/x-www-form-urlencoded"`;
- campo oculto `formTurma=formTurma` e campo oculto `javax.faces.ViewState` presente;
- controles `formTurma:inputNivel`, `formTurma:inputDepto`, `formTurma:inputAno` e `formTurma:inputPeriodo`;
- opções observadas: Graduação `G`, Stricto Sensu `S`, CIC `508`; ano inicial `2026` e períodos `1`, `2`, `3`, `4` (selecionado `2`);
- botão submit `formTurma:j_id_jsp_1370969402_11`, valor `Buscar`.

Esses nomes e valores descrevem somente a resposta consultada. A investigação complementar executou o postback: a busca funcionou com sessão, o ViewState mudou e o mesmo payload sem cookies retornou ao portal (seção 13). O link atual do portal para busca de componentes de Graduação usa `nivel=G&aba=p-graduacao`; `nivel=S` é a alternativa de Stricto Sensu, não de Graduação.

### Evidência histórica específica do endpoint de turmas

Há documentação pública de 2023 que trabalha diretamente com:

`https://sigaa.unb.br/sigaa/public/turmas/listar.jsf?aba=p-ensino`

Nessa interação, o fluxo usa:

1. `GET` inicial;
2. leitura de `javax.faces.ViewState`;
3. manutenção da sessão/cookies;
4. `POST` para o mesmo formulário;
5. campos do namespace `formTurma:*`;
6. um identificador de botão gerado pelo JSF;
7. o `ViewState` obtido na resposta inicial.

Campos documentados naquele fluxo incluem, conceitualmente:

- `formTurma`;
- `formTurma:inputNivel`;
- `formTurma:inputDepto`;
- `formTurma:inputAno`;
- `formTurma:inputPeriodo`;
- campo dinâmico do botão de busca;
- `javax.faces.ViewState`.

### Regra para #23

O protótipo **não deve reutilizar valores históricos como constantes**.

Em cada sessão, deve:

1. fazer o `GET` da página atual;
2. extrair o `javax.faces.ViewState` atual;
3. extrair os `value` atuais dos `<option>` do formulário;
4. identificar dinamicamente o `name` do controle de busca;
5. enviar o `POST` na mesma sessão;
6. analisar a tabela retornada;
7. verificar se uma nova interação exige ViewState renovado;
8. identificar paginação ou outros postbacks, se existirem.

O levantamento original ficou limitado à extração textual; a primeira validação acrescentou o HTML inicial, e a investigação complementar observou os POSTs da seção 13. A sequência proposta para #23 deve ser adaptada ao comportamento real; esta observação descartável não implementa o protótipo nem decide tecnologia.

---

## 7. Barreiras e ausências registradas

1. **Não foi encontrada exigência de login nas páginas efetivamente consultadas**, incluindo resultado POST e dois detalhes de componente. Sessão pública foi necessária no contraste observado; isso não significa autenticação institucional.
2. Campos de perfil de docente podem estar ausentes ou marcados como “não informado”.
3. A lista de 95 centros/unidades é mais ampla que uma lista simples de “departamentos acadêmicos”.
4. `cursosabertos.jsf` não deve ser interpretado como inventário completo de departamentos ou turmas.
5. A página de disciplinas do docente pode apresentar entradas repetidas no mesmo período e não expõe, na visualização observada, um código de turma suficiente para individualizar turmas.
6. A página de componentes da unidade mistura disciplinas, atividades e módulos.
7. Nenhum ID público estável de turma foi confirmado.
8. A ligação turma ↔ docente é textual na amostra atual, sem `siape` encontrado; identidade inequívoca não confirmada.
9. Os valores internos dos `<select>` e o identificador do botão JSF precisam ser capturados dinamicamente.
10. As 108 turmas da consulta observada vieram numa resposta, sem controles de paginação; outros cenários e limites internos não foram comprovados.
11. Não se deve considerar uma amostra de unidades como prova de cobertura RF17.
12. `creditos`, presente no modelo derivado em `specs.md`, não foi confirmado na fonte; carga horária não autoriza conversão para créditos por suposição.

---

## 8. Handoff para a Issue #23 — protótipo de extração

A #23 pode começar com um protótipo mínimo e verificável:

1. abrir uma `requests.Session`;
2. fazer `GET` de `public/turmas/listar.jsf`;
3. confirmar e extrair `javax.faces.ViewState`;
4. descobrir dinamicamente:
   - valor de “Graduação”;
   - IDs/valores das unidades;
   - nome atual do botão de busca;
5. submeter uma consulta real, por exemplo uma unidade e `2026.2`;
6. registrar a estrutura real da resposta:
   - disciplina;
   - código da turma;
   - docente;
   - horários;
   - local;
   - vagas;
   - links/IDs presentes;
7. verificar paginação/postback;
8. repetir em unidades estruturalmente diferentes;
9. verificar se o docente possui `siape` no HTML da turma;
10. comparar o conjunto de unidades do formulário com a lista de 95 centros/unidades e registrar diferenças.

A #23 deve demonstrar viabilidade técnica. Ela não deve assumir que o comportamento histórico do JSF continua idêntico sem revalidá-lo.

---

## 9. Handoff para a Issue #24 — modelo de dados

O levantamento fornece **candidatos de identidade externa**, não uma decisão de modelo:

- unidade: `id` público do SIGAA;
- docente: `siape`;
- componente: código acadêmico + ID público numérico disponível;
- turma: código da turma + período + componente + docente(s), caso não seja encontrado um ID estável.

A #24 deve decidir como persistir essas identidades e como tratar:

- múltiplos docentes em uma turma;
- homônimos, se o resultado não expuser SIAPE;
- mudanças entre períodos;
- componentes que não são do tipo `DISCIPLINA`;
- unidades institucionais que não correspondem a departamentos acadêmicos.

Na consulta de 13/09/2026, a #24 já estava fechada, com o critério de campos relacionados à fonte ainda desmarcado. Este handoff registra lacunas para avaliação do time, sem reabrir a issue ou substituir o modelo. A identidade composta de turma acima é hipótese, não chave validada; múltiplos docentes foram observados em CIC0004/02 e homônimos continuam sendo um risco, não ocorrência comprovada.

---

## 10. Verificação dos critérios de aceite da #22

- [x] URLs e passos de navegação até os dados documentados.
- [x] Campos disponíveis de professor, disciplina e turma identificados, incluindo vínculo ao componente e limitação da identidade textual do docente; detalhes atuais conferidos (seções 4–5 e 13).
- [x] Caminho para enumerar departamentos/unidades documentado, incluindo a limitação da taxonomia de 95 entradas.
- [x] Paginação, formulários e parâmetros necessários ao caminho documentado registrados: busca real com 108/108 linhas sem paginação exposta e POST de detalhe observado; rotas auxiliares e generalização explicitamente limitadas (seções 3 e 13).
- [x] Presença e execução de controles JSF/ViewState verificadas; comportamento de sessão e renovação observado para orientar #23 (seção 13).
- [x] Ausências de campos, limitações de identidade e barreiras de cobertura registradas sem presumir disponibilidade.

**Conclusão: pronta para aceite humano.** As lacunas de campos/relacionamentos e navegação pós-busca foram observadas no caminho documentado. Ausência de identidade inequívoca de docente/turma e limites da amostra estão registrados, sem inventar disponibilidade. O mapeamento não comprova cobertura integral ou viabilidade geral da extração e não implementa #23. O aceite oficial e o fechamento permanecem humanos.

---

## 11. Fontes consultadas

### Fontes do projeto

- `docs/requisitos.md` — RF16 e RF17.
- `docs/arquitetura.md` — risco de JSF/ViewState/postback.
- `specs.md` — decisões derivadas e indicação explícita de que a viabilidade do scraping ainda deve ser verificada.
- GitHub Issue #22 e Epic #12.

### Fontes públicas externas

- Portal Público SIGAA UnB:  
  https://sigaa.unb.br/sigaa/public/home.jsf
- Centros/unidades:  
  https://sigaa.unb.br/sigaa/public/centro/lista.jsf?aba=p-academico
- Busca de docentes:  
  https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf
- Busca de componentes:  
  https://sigaa.unb.br/sigaa/public/componentes/busca_componentes.jsf?nivel=S
- Busca de turmas:  
  https://sigaa.unb.br/sigaa/public/turmas/listar.jsf
- Turmas/comunidades publicadas:  
  https://sigaa.unb.br/sigaa/public/cursosabertos.jsf?aba=p-ensino
- Exemplo de portal de unidade (CIC):  
  https://sigaa.unb.br/sigaa/public/departamento/portal.jsf?id=508&lc=pt_BR
- Exemplo de docentes do CIC:  
  https://sigaa.unb.br/sigaa/public/departamento/professores.jsf?id=508
- Exemplo de componentes do CIC:  
  https://sigaa.unb.br/sigaa/public/departamento/componentes.jsf?id=508
- Registro público sobre o POST/ViewState no endpoint de turmas da UnB:  
  https://stackoverflow.com/questions/76593203/post-method-not-working-in-a-jsf-website-using-python-requests

## 12. Registro da validação — 13/09/2026

Base local: branch `feature/issue-22-mapeamento-sigaa`, **commit-base da validação** `e9fec6e8dcb8c8e66fcaf179063363deb2c3ab2a`. O working tree começou limpo na primeira validação; a investigação complementar começou com suas alterações locais neste arquivo. Nenhum commit foi produzido nessas atividades. Artefato encontrado neste caminho, não em `docs/estudos/sigaa.md`.

Autoridade: `project-governance` 1.0.0 está `Defined`; `requirements` 0.1.0 permanece `Proposed`, usada apenas como apoio. Foram confrontados a [Issue #22](https://github.com/unb-mds/G7-2026-2/issues/22), a [Epic #12](https://github.com/unb-mds/G7-2026-2/issues/12), RF16–RF17 e seção 11 de `docs/requisitos.md`, seções 3–5 e 8 de `docs/arquitetura.md` e seções 3 e 10 de `specs.md`. RF16 exige as três entidades públicas; RF17 exige todos os departamentos. Nem esta amostra nem o modelo derivado comprovam esses requisitos. O risco arquitetural não determina previamente a necessidade de automação de navegador.

Todas as consultas abaixo ocorreram em **13/09/2026**, na primeira validação. A tabela preserva aquele estágio; as lacunas superadas pela investigação complementar estão na seção 13. “Cache” significa evidência anterior recuperada nesta data, não confirmação ao vivo; os caminhos relativos usam a base `https://sigaa.unb.br/sigaa/` e têm URLs completas na seção 11.

| Fonte | Observação verificável | Natureza/limite |
|---|---|---|
| `public/turmas/listar.jsf` | GET direto HTTP 200; formulário, opções e controles descritos na seção 6 | Atual, HTML inicial; nenhum POST executado |
| `public/centro/lista.jsf?aba=p-academico` | Contador 95 e links de departamentos; repetição de Música no texto | Cache indicado como mês anterior; total não validado como IDs únicos nem cobertura acadêmica |
| `public/departamento/professores.jsf?id=508` | Contador 50, categorias, titulação e links de perfil; formação não informada em entradas | Extração textual indicada como coletada hoje, cabeçalho 12/09/2026; sem paginação visível nessa representação |
| `public/departamento/componentes.jsf?id=508` | Contador 399; código, nome, CH, tipos e coluna Ver | Extração textual indicada como coletada hoje, cabeçalho 12/09/2026; sem paginação visível, controle Ver não executado |
| `public/departamento/portal.jsf?id=508` | CIC, chefia, telefone/endereço não informados | Cache; cabeçalho 07/08/2026 |
| [Perfil de exemplo](https://sigaa.unb.br/sigaa/public/docente/portal.jsf?siape=1223368) | Nome, unidade, SIAPE na URL e campos de perfil/contato, vários não informados | Cache; cabeçalho 15/07/2026 |
| [Disciplinas do exemplo](https://sigaa.unb.br/sigaa/public/docente/disciplinas.jsf?siape=1223368) | Código, nome, CH e agrupamento por período; repetições em períodos anteriores | Cache; cabeçalho 01/09/2026; não individualiza turma |
| [Detalhe CIC0108](https://sigaa.unb.br/sigaa/link/public/ensino/visualizarComponente/178391) | URL obtida pelo link de disciplina do docente; abertura falhou com Cache miss | Conteúdo não verificado; falha da ferramenta não prova bloqueio do SIGAA |
| `public/docente/busca_docentes.jsf` | Entradas nome/departamento | Cache; cabeçalho 09/09/2026; sem submissão |
| `public/componentes/busca_componentes.jsf?nivel=S` | Entradas nível, tipo, código, nome e unidade | Cache; cabeçalho 07/09/2026; sem submissão |
| `public/cursosabertos.jsf?aba=p-ensino` | Turmas/comunidades publicadas; filtros palavra-chave, centros/departamentos | Cache; cabeçalho 28/08/2026; sem submissão |
| Relato Stack Overflow da seção 11 | Autor e resposta de 01/07/2023 descrevem requisições ao endpoint e saída de turma de 2022.2 | Histórico de terceiros; não comprova comportamento atual nem vínculo ao componente |

O acesso direto ao HTML de turmas inicialmente falhou na restrição de rede e funcionou após autorização de execução externa. Isso é limitação do ambiente, não barreira pública do SIGAA. Não foram arquivadas respostas HTML integrais. A afirmação anterior sobre orientações institucionais publicadas em 2026 foi retirada por ausência de URL identificada.

Na primeira validação, as tarefas de inspeção e registro estavam parcialmente atendidas. Após a seção 13, **inspecionar páginas relevantes — atendida para o caminho mapeado**; **registrar URLs/campos/relacionamentos/navegação — atendida, com limites explícitos**; **entregar mapeamento para #23/#24 — atendida como handoff documental local**, pelas seções 8–9, sem comprovar recebimento pelo time ou autorizar modelo definitivo.

## 13. Investigação complementar — evidência atual de 13/09/2026

Observação por requisições HTTP descartáveis, sem login, banco ou código de produção. As respostas bem-sucedidas tinham cabeçalho HTTP `Date` de 13/09/2026, entre 14:23 e 14:24 UTC (11:23–11:24 em Brasília), sem cabeçalho `Age`. Scripts e HTML ficaram apenas em diretório temporário externo ao repositório; os fatos e payloads relevantes estão transcritos abaixo. Valores de cookies e ViewState foram omitidos.

### 13.1 Formulário e payload da busca

1. GET `https://sigaa.unb.br/sigaa/public/home.jsf` → HTTP 200.
2. Seguir o link atual do portal: GET `https://sigaa.unb.br/sigaa/public/turmas/listar.jsf?aba=p-ensino` → HTTP 200, sem redirect.
3. Formulário `id/name=formTurma`, método `post`, action `/sigaa/public/turmas/listar.jsf`, enctype `application/x-www-form-urlencoded`.
4. Nível e unidade selecionados pelas opções atuais com rótulos Graduação e DEPTO CIÊNCIAS DA COMPUTAÇÃO; ano e período lidos dos controles atuais (`2026`, selecionado `2`). Botão localizado pelo valor `Buscar`, não por constante histórica.
5. POST `https://sigaa.unb.br/sigaa/public/turmas/listar.jsf`, com o cookie público da sessão e o payload abaixo → HTTP 200 na mesma URL, sem redirect, contendo o resultado de turmas.

| Nome enviado | Valor usado |
|---|---|
| `formTurma` | `formTurma` |
| `formTurma:inputNivel` | `G` |
| `formTurma:inputDepto` | `508` |
| `formTurma:inputAno` | `2026` |
| `formTurma:inputPeriodo` | `2` |
| `formTurma:j_id_jsp_1370969402_11` | `Buscar` |
| `javax.faces.ViewState` | valor oculto recebido no GET, omitido aqui |

O corpo enviado foi a codificação URL-encoded desses sete pares; `Cancelar` não foi enviado. Foram usados `Referer` para a URL inicial da busca, `Origin: https://sigaa.unb.br`, `Cache-Control: no-cache` e User-Agent `Mozilla/5.0`. A necessidade individual desses cabeçalhos não foi isolada.

### 13.2 Sessão, redirects e ViewState

| Interação observada | Resultado | Limite da conclusão |
|---|---|---|
| GET direto inicial de `listar.jsf`, em sessão nova | HTTP 200; recebeu cookie `JSESSIONID`, `Path=/`, `Secure` | Sessão pública, sem autenticação |
| Primeiro POST direto, preservando o cookie | URL final `public/home.jsf`, HTTP 200; sem tabela de turmas | Houve mudança de URL; cadeia/status intermediários não foram registrados nessa tentativa. Causa não isolada |
| Fluxo via portal e link atual, com a mesma sessão entre GET e POST | HTTP 200 em `listar.jsf`, sem redirect; 108 turmas | Funcionou nesse fluxo, em duas execuções observadas; não demonstra que a visita ao portal seja sempre obrigatória |
| ViewState após a busca bem-sucedida | Diferente do recebido no GET | Comparados os valores do mesmo controle; valores omitidos |
| POST com o ViewState da resposta e mesmos filtros, mas sem enviar cookies | 302 para `/sigaa/public/`, seguido de 302 para `/sigaa/public/home.jsf`; final 200, sem tabela de turmas | Contraste simples indica dependência da sessão neste fluxo; não identifica causa interna do servidor |
| Mesmo payload na sessão original | HTTP 200, sem redirect; novamente 108 turmas; ViewState mudou outra vez | Reutilizar o estado mais recente funcionou; rejeição obrigatória de um estado antigo na mesma sessão não foi testada |
| Comando de detalhe com ViewState mais recente, na sessão original | HTTP 200, sem redirect, em `listar.jsf`, agora com detalhe CIC0002 | URL isolada não distingue resultado da busca de detalhe; é necessário inspecionar o conteúdo |

A sessão foi mantida por cookie jar em memória. No teste sem sessão foi usado cliente separado sem envio de cookies; os valores do cookie jar original não foram reaproveitados. Não se conclui que HTTP 200, sozinho, signifique sucesso da consulta.

### 13.3 Resultado, relacionamentos e identidade

Fonte: resposta POST descrita em 13.1, tabela `table.listagem`, com 57 linhas `tr.agrupador`, 108 linhas de dados (`54 linhaPar` + `54 linhaImpar`), cabeçalho e rodapé. O rodapé informa **108 turmas encontrada(s)**.

| Campo/estrutura | Evidência concreta |
|---|---|
| Cabeçalhos | Código; Ano-Período; Docente; Horário (`colspan=2`); Qtde Vagas Ofertadas; Qtde Vagas Ocupadas; Local |
| Agrupador de componente | `span.tituloDisciplina`: `CIC0002 - FUNDAMENTOS TEÓRICOS DA COMPUTAÇÃO` |
| Comando do componente | `a#formTurma:aqui`, `href="#"`, título “Visualizar Detalhes do Componente Curricular”; `onclick` chama `jsfcljs` com `formTurma:aqui=formTurma:aqui`, `id=177942`, `publico=public` |
| Primeira turma desse agrupador | `td.turma=01`; `td.anoPeriodo=2026.2`; `td.nome=MARIA EMILIA MACHADO TELLES WALTER (60h)` |
| Horário/local/vagas dessa turma | `24T45 (10/08/2026 - 14/12/2026)`; popup Segunda/Quarta 16:00–17:50; local `PJC BT 077`; 50 ofertadas, 43 ocupadas |
| Múltiplos docentes | CIC0004, turma 02: YURI COSSICH LAVINAS (60h) e JOAO GABRIEL ROSSI DE BORBA (30h), na mesma célula |
| Links/identificadores de docente | Nenhum link ou input nas 108 linhas de dados; `siape` ausente no HTML da resposta; nenhum outro identificador inequívoco encontrado na célula do docente |
| Identificadores de turma | Código textual e período presentes; nenhum ID estável de turma confirmado em link, input ou atributo inspecionado. IDs `ajuda...` são popups de horário: para a primeira turma, `ajuda715387` mudou para `ajuda162588` ao repetir a busca |

O ID `177942` identifica o **componente**, não a turma. Os comandos dos outros agrupadores têm nomes gerados (`formTurma:aquij_id_1` etc.); não devem virar constantes. O agrupamento associa a turma ao componente, mas a associação a um cadastro inequívoco de professor continua limitada ao texto. Código/período/componente são campos observados, não uma chave de persistência aprovada.

### 13.4 Paginação da resposta real

Foram examinados os links e comandos de toda a resposta, os inputs/selects do único formulário e os atributos das linhas. Os 57 links internos da tabela são comandos de detalhe de componente; as linhas de turma não têm links. Inputs: marcador `formTurma`, ano, Buscar, Cancelar e ViewState; selects: nível, unidade e período. Não foram encontrados controles de paginação ou tamanho/limite de página. Os popups de horário apenas alternam visibilidade no HTML já recebido.

As **108 linhas conferem com o total de 108 do rodapé**: resultado completo em relação ao contador exposto para esta consulta, numa única resposta. A amostra já contém mais de uma centena de turmas, portanto não foi necessário consultar outra unidade para ampliar o resultado. Não há evidência de limite fixo nessa resposta, mas completude do universo institucional, truncamento interno não anunciado e comportamento de outros filtros não foram demonstrados. Isso delimita a observação, sem afirmar que o SIGAA nunca pagina.

### 13.5 Detalhes atuais de componentes

- **CIC0108:** GET do link obtido novamente em `https://sigaa.unb.br/sigaa/public/docente/disciplinas.jsf?siape=1223368`: `https://sigaa.unb.br/sigaa/link/public/ensino/visualizarComponente/178391` → 302 → `https://sigaa.unb.br/sigaa/public/componentes/resumo.jsf` → 200. Tipo DISCIPLINA; unidade CIC (`11.01.01.15.01`); nome SISTEMAS OPERACIONAIS; CH teórica 90h, prática 0h, EAD 0h, total 90h; pré-requisito CIC0104; correquisitos em branco; equivalências CIC0030 ou CIC0107; ementa e configurações acadêmicas presentes. Também há históricos de pré-requisitos/equivalências e tabela de currículos. Campo de créditos não encontrado nesse detalhe; não converter CH por suposição.
- **CIC0002:** POST do comando atual do agrupador, mesma action da busca. Payload: `formTurma=formTurma`, nível `G`, unidade `508`, ano `2026`, período `2`, ViewState mais recente (omitido), `formTurma:aqui=formTurma:aqui`, `id=177942`, `publico=public`, **sem o botão Buscar**. HTTP 200 na própria URL `listar.jsf`, sem redirect. Confirma CIC0002, FUNDAMENTOS TEÓRICOS DA COMPUTAÇÃO, DISCIPLINA, modalidade Presencial, unidade CIC, ementa, pré/correquisitos/equivalências indicados por `-`, configurações acadêmicas e quadro detalhado de cargas horárias (teórica presencial 30h, prática presencial 30h, subtotal presencial 60h). O layout de CH difere do resumo CIC0108; não assumir um único formato de detalhe.

### 13.6 Limites e encaminhamentos

- **#23:** reproduzir e comparar a extração em outros casos, tratar respostas inesperadas/redirects e layouts distintos, descobrir controles dinamicamente, investigar comportamento de estado antigo se necessário e confrontar cobertura entre inventários. O sucesso destas consultas não é a implementação do protótipo nem prova da viabilidade geral.
- **#24:** tratar identidade textual dos docentes, múltiplos docentes, código de turma sem ID estável confirmado e ausência de créditos, sem adotar silenciosamente chave composta ou mudar o modelo.
- **Não verificados:** rejeição de ViewState antigo na mesma sessão, necessidade individual de cada cabeçalho/visita ao portal, causa do primeiro retorno ao portal, todos os departamentos/períodos, limites internos não expostos e submissão das buscas auxiliares. Essas rotas auxiliares não são necessárias ao caminho que foi documentado e executado.
- **Decisão humana:** aceite/fechamento da #22 e qualquer mudança de escopo/modelo. Nenhuma decisão desse tipo foi efetivada nesta investigação.
