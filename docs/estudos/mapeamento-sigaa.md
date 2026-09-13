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

O ponto de maior risco técnico está na consulta de turmas. O endpoint é uma página JSF (`.jsf`) e existe evidência pública específica do mesmo endpoint da UnB de que a busca usa sessão, `javax.faces.ViewState` e `POST`. Os identificadores gerados pelo JSF, especialmente o campo do botão de busca, podem variar e **não devem ser hardcoded**. A Issue #23 deve revalidar esses controles no HTML atual antes de implementar o scraper.

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
5. Para turmas, usar o mesmo identificador/unidade conforme os valores atuais do formulário de `public/turmas/listar.jsf`.
6. Registrar unidades sem docentes, componentes ou turmas, em vez de descartá-las silenciosamente.

### Observação de cobertura

Na data do levantamento, a lista pública apresentava **95 centros/unidades especializadas**.

Esse número **não deve ser interpretado automaticamente como “95 departamentos acadêmicos”**. A lista inclui diferentes tipos de unidade institucional, como institutos, faculdades, centros e outras estruturas administrativas/acadêmicas. Portanto:

- ela é uma boa fonte para iniciar a enumeração;
- a Issue #23 deve verificar quais entradas efetivamente expõem os dados acadêmicos necessários;
- a cobertura do RF17 deve ser medida contra a taxonomia pública encontrada, registrando exceções;
- `cursosabertos.jsf` não deve ser usado sozinho para determinar a cobertura, pois representa turmas/comunidades publicadas e não necessariamente toda a estrutura institucional.

### Paginação observada

Não foi observada paginação na extração textual das páginas verificadas abaixo:

- lista de centros/unidades: 95 entradas em uma página;
- docentes do CIC (`id=508`): 50 docentes em uma página;
- componentes do CIC (`id=508`): 399 componentes em uma página.

Isso não autoriza assumir que nenhuma outra unidade ou resultado de busca jamais terá paginação. A paginação da **tabela de resultado da busca de turmas** deve ser verificada no protótipo #23, porque este levantamento não conseguiu submeter o formulário JSF atual.

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

Na página pública de detalhe do componente podem aparecer:

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

Há evidência pública anterior do **mesmo endpoint da UnB** mostrando resultados com dados como:

- código da turma;
- ano/período;
- docente;
- horário;
- quantidade de vagas ofertadas;
- quantidade de vagas ocupadas;
- local;
- disciplina/componente ao qual a turma pertence.

Como o formulário atual não pôde ser submetido por este ambiente de levantamento, os nomes e a estrutura exata das colunas atuais devem ser confirmados na Issue #23 antes que sejam tratados como contrato estável.

---

## 5. Relacionamentos encontrados

| Origem | Destino | Como relacionar |
|---|---|---|
| Unidade | Docente | `/departamento/professores.jsf?id=<ID>` |
| Unidade | Componente | `/departamento/componentes.jsf?id=<ID>` |
| Docente | Unidade | perfil público informa o departamento; `siape` identifica a página do docente |
| Docente | Disciplina | `/docente/disciplinas.jsf?siape=<SIAPE>`, agrupada por período |
| Unidade | Turma | unidade é um dos parâmetros do formulário de busca de turmas |
| Turma | Disciplina | resultado da busca é associado ao componente/código da disciplina |
| Turma | Docente | resultado da turma apresenta docente |
| Componente | Unidade | detalhe do componente informa a unidade responsável |

### Identificadores públicos úteis observados

- **unidade/departamento:** `id` numérico na URL;
- **docente:** `siape` na URL;
- **componente:** código acadêmico e um ID numérico usado na rota de detalhe;
- **turma:** nenhum identificador público estável, independente e reutilizável foi confirmado neste levantamento.

### Limitação importante para o relacionamento turma ↔ docente

O resultado de turmas precisa ser inspecionado no HTML atual para verificar se o nome do docente contém um link com `siape` ou outro identificador. Se houver apenas o nome textual, a associação automática por nome pode ser ambígua.

Essa decisão não deve ser escondida dentro do scraper. O protótipo #23 deve primeiro verificar o HTML real; a estratégia de identidade/persistência pertence à #24.

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

Páginas institucionais da própria UnB publicadas em 2026 ainda orientam usuários a usar esse fluxo no Portal Público para consultar turmas.

### Evidência específica do endpoint de turmas

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

Este levantamento não conseguiu confirmar no HTML bruto atual os nomes gerados do botão nem os valores numéricos atuais dos `<option>`, porque a ferramenta usada para inspecionar as páginas expõe o conteúdo textual, mas não os controles ocultos e não executa o `POST`. Isso fica explicitamente como verificação do protótipo #23.

---

## 7. Barreiras e ausências registradas

1. **Não foi encontrada exigência de login** para as fontes mapeadas; elas são páginas do Portal Público.
2. Campos de perfil de docente podem estar ausentes ou marcados como “não informado”.
3. A lista de 95 centros/unidades é mais ampla que uma lista simples de “departamentos acadêmicos”.
4. `cursosabertos.jsf` não deve ser interpretado como inventário completo de departamentos ou turmas.
5. A página de disciplinas do docente pode apresentar entradas repetidas no mesmo período e não expõe, na visualização observada, um código de turma suficiente para individualizar turmas.
6. A página de componentes da unidade mistura disciplinas, atividades e módulos.
7. Nenhum ID público estável de turma foi confirmado.
8. A ligação turma ↔ docente precisa ser verificada no HTML atual para saber se há `siape` ou apenas nome.
9. Os valores internos dos `<select>` e o identificador do botão JSF precisam ser capturados dinamicamente.
10. A paginação dos resultados pós-busca de turmas ainda precisa ser verificada em #23.
11. Não se deve considerar uma amostra de unidades como prova de cobertura RF17.

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

---

## 10. Verificação dos critérios de aceite da #22

- [x] URLs e passos de navegação até os dados documentados.
- [x] Campos disponíveis de professor, disciplina e turma identificados, com relacionamentos e limitações.
- [x] Caminho para enumerar departamentos/unidades documentado, incluindo a limitação da taxonomia de 95 entradas.
- [x] Formulários e parâmetros necessários à navegação registrados.
- [x] JSF confirmado no Portal Público atual; uso de ViewState/sessão/postback documentado para o mesmo endpoint de turmas, com revalidação dinâmica encaminhada à #23.
- [x] Ausências de campos, limitações de identidade e barreiras de cobertura registradas sem presumir disponibilidade.
- [x] Paginação explicitamente registrada onde não foi observada e marcada como pendente de verificação no resultado POST de turmas.

**Conclusão:** o mapeamento exigido pela #22 está documentado. A próxima atividade técnica é a #23, que deve executar o POST atual e validar a viabilidade do scraper sem transformar valores históricos do JSF em constantes.

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
