# Avaliação de autocompletar e tolerância a erros — Issue #251

**Data:** 15/11/2026. **Estado:** avaliação concluída; propostas `Proposed` e decisão do PO `Pending Decision`.
**Proponente e responsável pela apresentação:** Vinícius, [@ViniGvdo](https://github.com/ViniGvdo).
**Autoridade de produto:** Nicolas, [@nicolaszanin06](https://github.com/nicolaszanin06).
**Origem:** [Issue #251](https://github.com/unb-mds/2026-02-UnDb/issues/251).

**Encaminhamento: recomendar ajustes.** Há evidência favorável a autocompletar consultando o catálogo existente e a investigar `pg_trgm` como complemento da busca literal. O ensaio recuperou grafias incorretas, mas também produziu uma aproximação indevida. Ainda faltam calibração com julgamentos humanos, validação em PostgreSQL 16 nativo e conferência do ambiente hospedado. Não recomendar Meilisearch neste momento: não foi demonstrado um limite que justifique outro serviço. A implementação das três funcionalidades permanece **não autorizada**.

## 1. Objetivo, autoridade e base verificada

Avaliar separadamente tolerância a erros, sugestões durante a digitação e “Você quis dizer…”, sem mudar a aplicação. Este documento não é um contrato aprovado, novo requisito ou ADR efetivo. Vinícius elabora/apresenta a proposta; Nicolas decide escopo, solução, comportamentos, critérios, prioridade e momento.

As instruções aplicadas foram as skills canônicas de governança, arquitetura, testes, PostgreSQL e requisitos. Suas fronteiras preservam a distinção entre análise e decisão. As duas skills tecnológicas/de requisitos consultadas estão `proposed`; sua consulta não as promove. Nesta tarefa a autorização humana é exclusivamente documental e experimental.

### Atualidade e preservação do Git

O checkout inicial estava limpo em `feature/247-telas-conta-confirmacao-moderacao`, `57c72c3cc253878c284e2d84deb3195911afe13e`, sete commits atrás de `develop`. A consulta SSH/HTTPS no sandbox falhou por restrição de rede. `git fetch https://github.com/unb-mds/2026-02-UnDb.git develop main feature/247-telas-conta-confirmacao-moderacao`, com acesso permitido, confirmou:

| Referência remota em 15/11 | SHA |
|---|---|
| `develop`, base deste estudo | `cd7a27c9b7835d1d42967bdc6d51e9596b8a952f` |
| `main`, referência de publicação | `17d9b62c720a8a4192adef86aff4b4ac8dd27989` |
| Branch inicial | `57c72c3cc253878c284e2d84deb3195911afe13e` |

A investigação e os experimentos usaram uma worktree isolada em `.worktrees/issue-251-estudo`, no SHA atual de `develop`. A branch original não foi avançada, trocada ou integrada. A documentação foi entregue no checkout original porque os arquivos de documentação e configuração envolvidos são iguais nas duas bases; o diagnóstico permanece referenciado ao SHA acima. Na etapa inicial de avaliação não houve commit, push, PR, merge ou deploy.

A issue remota estava aberta e sem comentários. Buscas de PR por `251` e pelos termos autocompletar/autocomplete/tolerância/“Você quis dizer” não encontraram PR relacionada; a segunda busca retornou apenas a PR #177 de documentação SIGAA. Isso descreve as buscas realizadas, não prova ausência absoluta de vínculo não indexado. Após a entrega inicial, o solicitante autorizou publicar este material em PR para `develop`; a branch documental `docs/251-avaliacao-busca` foi criada na worktree isolada sobre a mesma base verificada. Essa autorização abrange commit, push e abertura da PR documental, sem autorizar implementação, merge, deploy ou encerramento da issue.

### Classes de evidência

| Marca | Significado e alcance |
|---|---|
| **OBS** | Inspeção do código, testes e documentos na revisão verificada; não prova execução em produção |
| **MED** | Execução local reproduzível com dados sintéticos; resultados e amostras arquivados |
| **DOC** | Capacidade ou restrição descrita por fonte oficial consultada; não comprova a configuração da conta do UnDb |
| **EST** | Inferência arquitetural ou estimativa de esforço/custo, com condições explícitas |
| **PROP** | Comportamento, limiar ou critério para análise e aprovação futura de Nicolas |

## 2. Estado atual da busca

### Backend, dados e contratos — OBS

O fluxo é router FastAPI → `institucional_service` → repository SQLAlchemy síncrono → PostgreSQL. As rotas públicas de listagem retornam arrays completos, sem paginação, limite, pontuação, total separado ou metadados de correção:

| Rota / filtro | Consulta e ordenação atuais |
|---|---|
| `GET /api/professores?nome=...` | Normaliza, separa termos e exige **todos**, em qualquer ordem, como substrings de `nome_normalizado`; ordena por `nome`, `id`; exclui IDs de origem de `professor_correspondencias` |
| `GET /api/disciplinas?nome=...` | Mesmo AND de substrings em `nome_normalizado`; ordena por `codigo` |
| `GET /api/disciplinas?codigo=...` | `ILIKE '%termo%'`, com trim; código completo ou parcial, ignorando caixa |
| `GET /api/disciplinas?codigo=...&nome=...` | Interseção dos dois filtros, **não** união |

`normalizar_busca` aplica NFKD, remove marcas combinantes, usa `casefold` e compacta espaços. Nome original é preservado para exibição. Normalização já é persistida na importação e na atualização de registros; não depende de `unaccent`. Hífens e apóstrofos permanecem. Termos separados podem casar dentro de palavras: `ma` encontra também Li**ma**. Não há distância de edição ou pontuação de relevância.

Professor contém UUID, nome/normalizado, departamento, SIAPE opcional e estado de identidade. Disciplina contém UUID, código único de até 20 caracteres, nome/normalizado, departamento, identificador externo e créditos opcionais. `departamento_nome` é propriedade obtida de `Unidade.nome` por associação ORM de leitura, sem coluna nova; pode ser nulo. Departamento/unidade são contexto de exibição, **não campos pesquisados pelos filtros de nome**.

As listagens não exigem turma ativa para retornar um professor/disciplina. As consultas de disciplinas por professor e de turmas da disciplina usam turmas ativas. Um catálogo de sugestões deve preservar essa elegibilidade enquanto o PO não aprovar mudança. Não unir homônimos por nome nem ressuscitar aliases já excluídos. Busca por UUID antigo resolve o destino canônico.

Não foram encontrados índices de busca em `nome_normalizado` nas migrations/models. Existem PKs, unicidade de código/SIAPE/identidade e índices de outras responsabilidades. A unicidade B-tree de código não garante aceleração para `%trecho%`; não adicionar índice sem consulta/plano representativos.

### Frontend — OBS

Home e cabeçalho usam formulário GET por modalidade, encaminhado por `/busca` a `/professores` ou `/disciplinas`. Não exibem popup de sugestões. Nas páginas de resultados, `BuscaInstitucional` já consulta durante a digitação, com **300 ms de debounce**, mínimo de **dois caracteres**, estados inicial/carregando/erro/vazio e nova tentativa.

Para disciplina, `buscarDisciplinas` faz duas requisições em paralelo (nome e código), une por UUID e depois ordena. Falha de uma das duas rejeita a união, sem falso sucesso parcial. `ordenarResultados` usa colação `pt-BR`, nome/unidade conforme escolha, departamento e UUID para desempate. Portanto, ordenar por relevância apenas no servidor seria desfeito pelo frontend atual.

O efeito usa flag de cancelamento e confere termo/tipo/tentativa para não apresentar resposta antiga como atual. Não cancela o trabalho HTTP/SQL em andamento; os serviços de listagem não propagam `AbortSignal`, embora o cliente HTTP aceite essa opção. A região de estado tem `aria-live`, `aria-atomic` e `aria-busy`; não há interação de combobox/listbox. Cada cartão de professor busca suas disciplinas, acrescentando uma chamada por professor apresentado. Um popup de oito sugestões não deve reutilizar esse carregamento de cartões.

### Limitações e mudanças recentes

- **MED/OBS:** acentuação, sobrenome, nome incompleto, espaços e ordem de palavras já são atendidos quando cada termo existe literalmente. Transposição, omissão e duplicação de letras deixam de encontrar registros.
- **MED:** `joao pedro davila` não encontra `João-Pedro D'Ávila`; preservar a pontuação no termo encontra. Acentuação diferente, isoladamente, não explica essa falha.
- **MED:** `%` e `_` não são escapados como literais nos filtros LIKE. A sonda `%%` retorna todos os 11 docentes canônicos do corpus. Isso não é SQL injection: parâmetros continuam vinculados. É ampliação indevida da consulta e possível custo de carga.
- **OBS:** a API não aplica mínimo/máximo de termo nem limite de resultados. O mínimo do navegador não protege chamadas diretas. Termo vazio/sem filtros pode listar o catálogo inteiro. Não se encontrou proteção de frequência específica nessas rotas.
- **OBS:** RF23/ADR 07 evoluíram em 11–13/11: identidades institucionais e fallback local por unidade, aliases e decisões de separação. Busca aproximada não é ferramenta de reconciliação de identidade.
- **OBS:** PRs #214/#215 acrescentaram nomes institucionais; #211/#233 reorganizaram as telas; #248 e #246 já estão integradas na base atual. Os arquivos centrais de consulta e do componente de busca examinados não diferem de `main`, mas isso não certifica a revisão efetivamente implantada. Estudos de setembro sobre duplicatas/testes ausentes são históricos, não diagnóstico atual.

Fontes locais principais: [busca original verificada](verificacao-busca-professor-disciplina.md), [hospedagem](../hospedagem.md), [identidades docentes](../identidades-docentes.md) e os arquivos versionados relacionados na seção 14.

## 3. Requisitos e decisões relacionados

| Fonte vigente | Relação com a proposta |
|---|---|
| [RF05](../requisitos.md#modulo-2-busca-e-navegacao) | Exige busca de professor por nome, inclusive parcial; não aprova aproximação ou popup |
| RF06, no mesmo módulo | Exige nome ou código de disciplina; não autoriza interpretar código errado como disciplina certa |
| RF07, no mesmo módulo | Não restringir pelo curso/departamento do usuário; manter consulta pública entre unidades |
| Decisões institucionais da seção 11 dos requisitos | Nome parcial sem distinção de caixa/acento, vazio válido retorna `[]`, inexistente individual 404 e homônimos separados |
| [ADR 01](../arquitetura.md#adr-01-sqlalchemy-alembic-como-orm-e-ferramenta-de-migracao) | SQLAlchemy síncrono, psycopg2 e Alembic; extensão/índice futuro teria migration revisada, sem substituir a stack |
| ADR 02 / ADR 08 | Next.js/Tailwind e runtime servidor; sugestões no navegador consomem a API, sem acesso ao banco |
| ADR 07 / RF23 | Identidade por UUID e correspondências explícitas; similaridade de nome nunca autoriza união |
| RF08 / RNF02 | Sugestões não expõem avaliações individuais ou critérios abaixo do mínimo de três avaliações |
| RF16–RF19 | Sugestões derivadas do catálogo persistido, atualizado pela importação; não coletar SIGAA a cada tecla |

RNF02 está aprovado; os demais RNFs preservam o estado proposto indicado na fonte. Segurança e acessibilidade abaixo são análise e propostas desta tarefa, sem promover aqueles RNFs.

**PROP:** se houver autorização, detalhar em RF05 a tolerância por nome e a distinção entre literal/aproximado; em RF06 separar política de nomes e códigos; em RF07 preservar acesso entre unidades e desambiguação. Definir separadamente autocompletar e correção opcional, com critérios da seção 11. Não atribuir novo número RF nem alterar o texto aprovado nesta etapa.

**PROP:** ADR 01 pode receber referência futura ao uso opcional de extensão e índices via Alembic. Não precisa ser substituído: ORM, driver e migrações permanecem. Meilisearch exigiria decisão adicional sobre serviço derivado, consistência e operação. A ordenação de sugestões por pertinência deve ser aprovada explicitamente e distinguida da comparação de avaliações por recomendação (ADR 05/RF13), preservando as opções atuais nome/unidade e o contexto de navegação da #155.

## 4. Funcionalidades avaliadas separadamente

### 4.1. Tolerância a erros

**MED:** todos os casos 01–26, incluindo transposição, omissão, duplicação, nomes compostos, homônimos, códigos e controles, estão no [anexo de resultados](evidencias/issue-251/resultados.md). A variante literal sem extensão resolve pontuação definida no ensaio, mas não recupera os erros de letras. `pg_trgm` recupera esses erros com configuração por termo, sem dicionário independente.

**PROP:** preservar primeiro os resultados literais; só oferecer aproximações como alternativas identificadas quando não houver resultado literal satisfatório. Para códigos, manter exato/parcial inicialmente. `CIC004` tem similaridade 0,875 com `CIC0004` no ensaio, mas isso não prova a intenção: códigos vizinhos podem ser disciplinas diferentes. Correção de código precisa de decisão e corpus próprios. Homônimos continuam linhas separadas por UUID, com unidade/código visíveis.

### 4.2. Autocompletar

**EST:** é viável usar diretamente professores, disciplinas e unidades já persistidos. O catálogo é a fonte; não há necessidade demonstrada de tabela ou dicionário editorial de sugestões. Um índice Meilisearch seria uma projeção reconstruível desses dados, não outra autoridade de cadastro.

**PROP — comportamento para aprovação:**

| Tema | Comportamento candidato e motivo |
|---|---|
| Escopo e limite | Até **oito sugestões no total** para a modalidade selecionada, ordenadas antes do limite; combinar tipos seria outra opção do PO, com tipo explícito e oito no total, não oito por tipo |
| Conteúdo | Nome, unidade quando disponível; disciplina inclui código. Usar código/unidade identificável se nome institucional estiver ausente; não inventar unidade nem buscar dados privados |
| Termos curtos | Preservar orientação sem consulta com menos de dois caracteres; dois caracteres apenas literal/prefixo e limite no servidor. A amostra confirma que `ma` é pouco seletivo. Aproximação de palavras curtas precisa de calibração; não ativar só porque o motor permite |
| Frequência | Reaproveitar 300 ms como ponto inicial já existente, validando a experiência; isso é pausa antes da consulta e não promessa de tempo de resposta |
| Teclado/foco | Setas percorrem opções, Enter ativa somente opção explicitamente selecionada, Escape fecha sem apagar texto, Tab segue a ordem da página. Digitar continua possível; foco permanece no input enquanto se navega pelas opções |
| Estados | Distinguir digitando/carregando, vazio e falha; nova tentativa na falha. Não tratar indisponibilidade como ausência de professor/disciplina |
| Concorrência | Cancelar HTTP quando possível e manter identificação de termo/modalidade/tentativa. Descartar resposta antiga mesmo se o cancelamento chegar tarde; ao trocar modalidade/limpar/fechar, invalidar seleção anterior |
| Seleção | Não preencher/navegar automaticamente ao chegar resposta. Preservar consulta original e oferecer acesso à busca completa; sugestão por UUID leva ao recurso escolhido |
| Móvel | Popup dentro da viewport e acima do teclado quando necessário, área rolável, toque sem dupla ativação, nomes longos com quebra, sem overflow em 320 px; testar zoom, orientação e teclado virtual reais |

O mínimo de dois e o debounce existem na lista atual; o limite de oito e a interação de popup são novas propostas. Não afirmar que autocompletar já existe por haver consulta incremental na página de resultados.

### 4.3. “Você quis dizer…”

**PROP:** disparar a avaliação de alternativas após sucesso da busca literal com zero resultados; resultado literal pouco útil precisaria de definição do PO e julgamentos humanos antes de ampliar esse gatilho. Falha HTTP, consulta curta, só pontuação ou código ambíguo não devem produzir correção afirmativa.

Gerar candidatos no catálogo canônico, calcular semelhança por palavras e considerar a diferença entre os melhores **nomes distintos**. Empate entre homônimos não deve ocultar pessoas: pode-se oferecer a grafia comum e abrir nova busca que mantenha os dois registros. Nomes distintos com pontuações próximas devem ser apresentados como “Resultados semelhantes” ou não gerar correção, sem escolher uma pessoa como certa.

Exemplo proposto: `Nenhum resultado para “emliia”. Ver resultados para “Emília”?`, com ação explícita e alternativa de continuar a consulta original. A sugestão é possibilidade, não certeza ou porcentagem de confiança. Nunca substituir o texto sem ação do usuário. O ensaio não valida um limiar seguro para publicar essa frase automaticamente; a seção 7 mostra por quê.

## 5. Metodologia e ambiente experimental

**MED:** [dados e SQL](evidencias/issue-251/dataset.json), [amostras/planos completos](evidencias/issue-251/resultados.json), [tabelas por caso](evidencias/issue-251/resultados.md) e [comandos de reprodução](evidencias/issue-251/reproducao.md). Os scripts ficam junto das evidências e não são importados pela aplicação, CI ou migrations.

Foram criados 12 docentes sintéticos (um alias de outro docente, excluído da busca), dez disciplinas e cinco unidades. UUIDs determinísticos e campos seguem os modelos reais. Não foram usados contas, avaliações, credenciais, registros pessoais extraídos ou dados do banco compartilhado.

| Componente | Executado / configuração |
|---|---|
| Preparação | Python 3.14.7, SQLAlchemy 2.1.8; dependências já declaradas do backend instaladas em venv isolado, sem mudar manifests |
| Baseline | Repositories reais executados em SQLite em memória; suas consultas capturadas e compiladas pelo dialeto PostgreSQL com parâmetros vinculados, depois executadas em PostgreSQL embarcado; paridade dos conjuntos verificada nos 26 casos |
| PostgreSQL medido | PGlite 0.5.16, PostgreSQL **18.6 WASM**, `pg_trgm` 1.6; `datcollate=C`, `datctype=C.UTF-8`, Node 24.21.0; memória descartável |
| Variante literal | Mesmas substrings por termo, com `strpos` literal; remove apóstrofos e transforma hífens em espaços nos dois lados; mínimo de dois caracteres. Política experimental, não alteração de normalização de identidades |
| Variante trgm | Exato → prefixo da frase → todos os termos literais → aproximado; score = menor `word_similarity(termo, nome_normalizado)` entre termos; aproximação só para consulta com pelo menos três caracteres; códigos com letras+números permanecem literais; limite oito |
| Limiares | Varredura inclusiva 0,3 / 0,4 / 0,5 / 0,6. São cortes exploratórios, não configuração de produção; 0,3 toma como referência o padrão de similaridade global e os cortes mais estritos mostram a perda de cobertura |
| Tempos | Uma passagem de aquecimento antes das 30 repetições por caso/variante; ordem atual → trgm → literal, sequencial. p50/p95 e amostras arquivados; sem concorrência ou HTTP da aplicação |
| Índices | Ensaio auxiliar com 12.000 nomes artificiais, GIN e GiST testados um por vez em outra tabela; `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` e tamanhos coletados |
| Meilisearch | v1.56.2 oficial baixada e SHA-256 conferido; **não executado**, por bloqueio do Controle de Aplicativo do Windows (`spawn UNKNOWN`, -4094). Docker sem daemon. Não houve serviço instalado/configurado/publicado |

O PostgreSQL do Compose e do CI é **16**, não a versão WASM medida. As funções/opclasses usadas constam da documentação oficial do 16, mas compatibilidade de comportamento e planos ainda deve ser validada em servidor 16 nativo. PostgreSQL WASM não mede psycopg2, pool, latência Neon/Render, conexão TLS, concorrência ou partidas a frio. Não é benchmark de produção nem teste fim a fim.

Foi preparado um caminho opcional do ensaio para Meilisearch local: dois índices por tipo, UUID como chave, atributos pesquisáveis `codigo,nome`, exibição pública mínima, tolerância padrão 5/9 e desativada em `codigo`, oito hits, comparação de `matchingStrategy=last` e `all`. Esse caminho **não foi validado em execução**; não há medições, ordenação ou acertos atribuídos ao Meilisearch. Deve ser revisado e executado em ambiente permitido antes de qualquer decisão de adoção. Não foi usada alternativa remota para contornar o bloqueio.

## 6. Casos, resultados e limites das medições

O [anexo](evidencias/issue-251/resultados.md) contém os **26 termos, julgamentos, resultados em ordem de posição, falsos positivos/negativos e p50/p95 por consulta**. Abaixo, os casos que mudam a decisão:

| Termo e intenção sintética | Busca atual | Literal sem extensão | trgm a 0,3 | Interpretação MED |
|---|---|---|---|---|
| `Maria Emília dos Santos`, dois homônimos | P1, P2 | P1, P2 | P1, P2 | Manter ambos; P12 é alias e não reaparece |
| `emilia` / `santos` | Encontra os parciais/sobrenomes | Igual conjunto | Igual conjunto, ordem diferente | Não atribuir esse ganho à aproximação |
| `emliia`, transposição | ∅ | ∅ | P1, P2 | Ganho de recuperação; score 0,4286 |
| `maria emlia santos` | ∅ | ∅ | P1, P2 | Nome composto com omissão; score 0,5000 |
| `emiilia`, duplicação | ∅ | ∅ | P1, P2 | Score 0,6667 |
| `santos maria`, espaços/ordem | P1, P2 | P1, P2 | P1, P2, **P10 indevido** | “Mario Santos” entra com 0,6667, mesmo score de erro correto em outro caso |
| `joao pedro davila` | ∅ | P4 | P4 | Política literal de pontuação já resolve este exemplo |
| `CIC0004` / `CIC000` | Código completo/parcial encontrado | Mesmo conjunto | Mesmo conjunto | Recurso já disponível |
| `CIC004` / `CIC0400` | ∅ | ∅ | ∅ | Código aproximado deliberadamente desativado na variante, não incapacidade do motor |
| `algortimos` | ∅ | ∅ | D9, D10, D1 | Três disciplinas plausíveis, score 0,4667; não corrigir para um UUID |
| `nascimnto` | ∅ | ∅ | P8 | Sobrenome com omissão, score 0,6154 |
| `a` | 11 registros na API | ∅ | Oito registros | UI atual não faria a consulta; mínimo também deve existir no servidor futuro |
| `%%` | 11 registros | ∅ | ∅ | Escapar curingas/tratar entrada sem conteúdo nominal |
| `zzqxv` / `maria alvaro` | ∅ | ∅ | ∅ | Negativos preservados nesta amostra pequena |

### Métricas de relevância

Para evitar misturar sondas de abuso/UI com relevância, o recorte lexical usa 24 consultas: exclui `a` e `%%`. São 45 pares consulta/registro esperados, 22 consultas positivas e duas negativas. “Correto” significa pertencer ao julgamento sintético registrado, não identidade inferida. Código errado tem intenção conhecida no teste, impossível de conhecer automaticamente na aplicação.

| Variante medida | TP / FP / FN | Precisão | Cobertura | MRR do primeiro relevante | Positivas com algum acerto |
|---|---|---|---|---|---|
| Atual | 32 / 0 / 13 | 100,0% | 71,1% | 0,636 | 14/22 |
| Literal experimental | 33 / 0 / 12 | 100,0% | 73,3% | 0,682 | 15/22 |
| trgm experimental, 0,3 | 43 / 1 / 2 | 97,7% | 95,6% | 0,909 | 20/22 |
| Meilisearch | Não medido | Não medido | Não medido | Não medido | Não medido |

Precisão = TP/(TP+FP); cobertura = TP/(TP+FN); MRR = média de 1/posição do primeiro relevante, zero quando ausente, entre as 22 positivas. Para sugestões, essas métricas são observadas até oito; a baseline preserva a lista completa para reproduzir o comportamento atual. Os conjuntos lexicais não atingiram esse limite. As duas negativas lexicais ficaram vazias em todas as variantes medidas.

No corpus integral, os controles curtos/curingas reduzem a precisão da baseline para 59,3% e da variante trgm para 82,7%. Isso não é estimativa da precisão do produto: o caso de uma letra viola a política da UI e `%%` foi incluído deliberadamente. Também não medir “taxa de correções erradas” com esses resultados: nenhuma interface “Você quis dizer” foi construída ou submetida a pessoas.

### Desempenho e espaço — MED

Os tempos por caso estão no anexo. São custos locais de consultas pequenas: não demonstram que 300 ms de debounce mais rede/partida a frio serão aceitáveis. As duas consultas de disciplina foram serializadas na conexão WASM, enquanto o navegador usa paralelo; a variante também evita a consulta duplicada de código, confundindo qualquer comparação direta de velocidade entre algoritmos.

No ensaio auxiliar de 12.000 linhas, tabela de 1.056.768 bytes, o p50/p95 foi 32,277/56,343 ms sem índice, 0,963/1,435 ms com GIN e 2,346/4,093 ms com GiST. GIN ocupou 679.936 bytes; GiST, 1.351.680 bytes nessa execução. Houve Seq Scan, Bitmap Heap Scan e Index Scan, respectivamente; o plano KNN por distância também usou GiST. **Não generalizar tamanho nem vantagem de um índice:** distribuição, cache, ordem das medições e WASM influenciam os resultados.

O SQL auxiliar usa `nome % termo`, enquanto a variante de relevância calcula o mínimo de funções por termo. Esse cálculo, isoladamente, **não prova uso de índice**. Uma futura consulta precisa combinar candidatos gerados por operadores indexáveis e reavaliação da pontuação; verificar seu plano real e os efeitos nos writes da importação antes de escolher GIN ou GiST. Não recomendar ambos os índices por padrão.

## 7. Ordenação, pontuações e limiares

**DOC:** `pg_trgm` oferece `similarity`, `word_similarity`, `strict_word_similarity`, operadores `%`, `<%`/`%>`, `<<%`/`%>>` e distâncias, inclusive `<->`. O módulo trabalha com trigramas de palavras; não transforma acentos em letras equivalentes por si só. GiST/GIN suportam operadores de similaridade e LIKE/ILIKE; GiST permite KNN por distância, GIN não oferece essa ordenação eficiente. Padrões sem trigramas aproveitáveis podem degradar para varredura. [Documentação PostgreSQL 16](https://www.postgresql.org/docs/16/pgtrgm.html).

**MED:** similaridade global de `emliia` com `maria emilia dos santos` = 0,1154; `word_similarity` = 0,4286. Comparar sempre o nome completo penaliza sobrenome/fragmentos. Acento cru `emília`/`emilia` = 0,4; após a normalização existente = 1. Hífen/espaço no par `joao-pedro`/`joao pedro` = 1. Trigramas não substituem a política de normalização literal nem resolvem identidade.

**PROP:** para o popup, usar faixas explícitas: nome/código exato normalizado, prefixo, todos os termos parciais, depois aproximação identificada. Dentro da faixa, ordenar pela pontuação quando aplicável e desempatar por nome, unidade/código e UUID. A pesquisa por sobrenome deve considerar prefixo de cada palavra, não somente início do nome completo. A POC usa prefixo da frase como simplificação documentada. Não usar avaliação/recomendação do professor para a pertinência textual.

A varredura completa deu os mesmos resultados em 0,3 e 0,4. Em 0,5 perdeu `emliia` e as três disciplinas de `algortimos`; em 0,6 perdeu também `maria emlia santos` e a variante de pontuação. O FP “Mario Santos” permaneceu até 0,6. Logo, aumentar o corte não assegura maior precisão neste corpus. O valor 0,3 é apenas ponto de referência, e o default de `word_similarity_threshold` do operador é **0,6**, diferente do default 0,3 de `%`. A POC compara a função com parâmetros inclusivos; não usa esses GUCs como se fossem intercambiáveis.

Não há limiar de confiança aprovado ou empiricamente validado. Para nova rodada, 0,3–0,4 são candidatos de **geração** de alternativas por preservar os exemplos difíceis, nunca de certeza. A sugestão de correção precisa ser calibrada separadamente, com negativos próximos e conjunto reservado: o score 0,6667 tanto acertou duplicação quanto trouxe nome indevido. Não há suporte para publicar “Você quis dizer” simplesmente acima de 0,6 ou 0,7.

**PROP:** reduzir aproximações supérfluas usando fallback após resultados literais, mantendo palavras curtas como condição literal e aproximando somente palavras de comprimento validado. No caso 16 isso evitaria acrescentar P10; a arquitetura dessa política é inferência, não nova medição. Comparar melhores nomes distintos, empates e margem entre candidatos na próxima rodada. Não fixar margem numérica sem distribuição de erros/positivos. Códigos, nomes ambíguos e pontuações pouco separadas devem permitir abstenção.

## 8. Comparação das alternativas

### PostgreSQL e integração com a stack

**DOC/EST:** é possível combinar consultas literais e funções de similaridade via `func` e operadores parametrizados de SQLAlchemy, preservando o driver síncrono. `bool_op`/operadores customizados permitem predicados indexáveis. Índices usam opclass e método PostgreSQL (`postgresql_ops`, `postgresql_using`); o Alembic aceita opções do dialeto e execução de DDL de extensão. Isso requer migration explícita revisada; não presumir que autogenerate descobrirá todo o ciclo de extensão/índices. [SQLAlchemy](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html), [Alembic](https://alembic.sqlalchemy.org/en/latest/ops.html).

Operadores por termo precisam gerar candidatos sem excluir resultados aceitos pela regra final: limiar estrito do operador versus comparação inclusiva do score pode divergir na fronteira. Configurações por transação (`SET LOCAL`, se adotado) evitam vazar limiar entre requisições no pool; plano e parametrização precisam de teste. Não concatenar entrada do usuário no SQL.

**EST:** os três recursos podem compartilhar candidatos do catálogo e `pg_trgm`, mas o módulo não entrega debounce, combobox acessível, contratos, política de códigos, decisão de abstenção ou frase de correção. Exige lógica complementar da aplicação, sem evidência de necessidade de serviço/dicionário adicional.

### Meilisearch

**DOC:** oferece tokenização/normalização para português, busca por prefixo da última palavra e tolerância configurável por atributo/tamanho. O padrão admite um erro a partir de cinco caracteres e dois a partir de nove; convém desativar em `codigo`. Nomes compostos exigem avaliar a estratégia de correspondência: relaxar palavras pode trazer candidatos que ignoram parte do nome. [Tolerância](https://www.meilisearch.com/docs/capabilities/full_text_search/relevancy/typo_tolerance_settings), [prefixos](https://www.meilisearch.com/docs/resources/internals/prefix), [idiomas](https://www.meilisearch.com/docs/resources/help/language).

**DOC/PROP:** definir atributos pesquisáveis explicitamente (`codigo`, `nome` em disciplina; `nome` em professor), com unidade apenas como contexto inicialmente. A ordem dos atributos influencia relevância; regras de palavras, erros, proximidade e exatidão não equivalem automaticamente à ordem exato/prefixo/parcial proposta. Testar `matchingStrategy=all` para preservar todos os termos. `_rankingScore` não é probabilidade nem distância trigram; não reutilizar o mesmo corte. `limit=8` limita a resposta, mas as políticas de consulta curta e de “Você quis dizer” continuam na aplicação. [Ranking](https://www.meilisearch.com/docs/capabilities/full_text_search/relevancy/ranking_rules), [API de busca](https://www.meilisearch.com/docs/reference/api/search/search-with-post).

**EST:** FastAPI poderia consultar REST com cliente de backend ou SDK futuro aprovado, com timeout e limite; Next.js continuaria consumindo a API do UnDb. A escrita do índice ocorre fora da requisição de busca. Não ligar navegador a chave administrativa. Um SDK é conveniência de integração, não justificativa de adoção.

**DOC/EST:** indexação tem fila assíncrona; receber tarefa não significa dado pesquisável. O PostgreSQL continua fonte de verdade. Seriam necessários sincronização após commit da unidade importada, acompanhamento até sucesso, retentativas idempotentes, exclusões/aliases e reconstrução integral. É uma diferença operacional concreta em relação ao índice transacional no mesmo PostgreSQL. [Indexação e tarefas](https://www.meilisearch.com/docs/capabilities/indexing/overview).

### Matriz de decisão

Os resultados MED são do corpus sintético e do SQL auxiliar; Meilisearch é DOC/EST, sem benchmark comparativo. “Busca atual” abaixo distingue o existente da variante literal quando necessário.

| Critério | Busca atual | PostgreSQL + pg_trgm | Meilisearch |
|---|---|---|---|
| Tolerância a erros | MED: falha nos casos 04/06/15/25/26; pontuação pode melhorar sem extensão | MED: recupera esses casos, mas inclui P10 indevido em 16; depende da política por termo | DOC: tolerância por palavra/tamanho/atributo; eficácia em nomes UnDb não medida |
| Autocompletar | OBS: lista incremental já tem 300 ms; popup/limite oito não existem | EST: consulta limitada ao catálogo, índice se plano justificar; UI ainda necessária | DOC: prefixo e limite disponíveis; interface, proteção e foco ainda necessários |
| “Você quis dizer…” | OBS: mensagem de grafia/consulta curta sem alternativa calculada | MED/PROP: gera candidatos; score isolado não distingue FP a 0,6667 | DOC/EST: hits aproximados/score podem ajudar; não validam correção nem escolha de pessoa |
| Nomes compostos | MED: AND de partes sem ordem; um erro elimina o resultado | MED: mínimo por termo recupera 06; sem regra por termo a similaridade global penaliza fragmentos | DOC: proximidade e matching strategy influenciam; testar todos os termos para evitar relaxamento enganoso |
| Acentuação | MED: NFKD/casefold já resolve 05/20 | MED: reutilizar `nome_normalizado`; acento cru teve score 0,4 | DOC: normalização latina remove marcas; paridade do corpus não medida |
| Busca por código | MED: exato/parcial já funciona; não corrige 11/24 | MED: mantida literal; score alto de código errado exige política própria | DOC/PROP: pesquisar código, desativar typo no atributo; prefixo não equivale a substring arbitrária |
| Integração com arquitetura atual | OBS: FastAPI/SQLAlchemy/Neon existentes | EST: mesma fonte, ORM e Alembic; precisa extensão/permissão/migration | EST: adaptador de busca e projeção externa mais sincronizador; decisão estrutural nova |
| Complexidade de implementação | EST: menor para literal/limites; popup acessível ainda é trabalho real | EST: intermediária: ranking, calibração, extensão/índice, testes PostgreSQL e popup | EST: maior: mesmo popup/calibração mais exportação, tarefas, falhas e reconciliação do índice |
| Complexidade operacional | OBS/EST: operação atual; carga cresce sem limite/frequência | MED/EST: índice consome espaço e escrita; operação dentro do banco existente | DOC/EST: processo persistente, chaves, disco, backup, upgrades e índice eventualmente consistente |
| Infraestrutura adicional | OBS: nenhuma | EST: sem novo processo, mas recursos adicionais no PostgreSQL | EST: serviço com persistência ou Cloud; Render Free atual não oferece disco persistente |
| Custos | EST: CPU/transferência já existentes; chamadas por digitação e cartões ampliam consumo | MED: índices auxiliares ocuparam 0,68/1,35 MB; custo remoto depende de CU/storage e carga real | DOC: Cloud anunciado a partir de US$20/mês, variável por região; self-host exige compute/disco/operação |
| Manutenção | OBS/EST: uma fonte, preservar normalização e contratos | EST: uma fonte; monitorar planos, índices, imports e calibrar ranking sem alterar identidade | EST: PostgreSQL mais índice; monitorar atraso/falhas/exclusões, reconstrução e compatibilidade de versões |
| Reversibilidade | EST: mudanças opcionais pequenas podem ser desativadas preservando consultas antigas | EST: fallback literal; remover índice por migration se seguro; extensão pode ser compartilhada, não usar DROP CASCADE | EST: desligar roteamento e voltar ao PostgreSQL; manter capacidade de reconstruir antes de encerrar serviço/chaves |

## 9. Infraestrutura, permissões, custos e manutenção

**OBS:** o projeto documenta Vercel Hobby, Render Free e Neon Free para a demonstração, com importador separado. O histórico de 10/11 registra 8.267 cadastros docentes e 3.485 disciplinas, antes de reconciliações posteriores; não são pessoas únicas nem uma contagem atual auditada. Não há medição de QPS, volume atual de consultas ou saturação que justifique motor externo.

**DOC:** o Neon documenta suporte a `pg_trgm`. No PostgreSQL ele é extensão trusted e requer privilégio `CREATE` no banco para instalação por não superusuário. O runtime limitado da API não deve receber administração de extensão. Usar papel de migração, alinhado a `MIGRATION_DATABASE_URL` e ao [roteiro #170](../acesso-postgresql-api.md). [Neon pg_trgm](https://neon.com/docs/extensions/pg_trgm), [PostgreSQL current](https://www.postgresql.org/docs/current/pgtrgm.html).

**Não verificado no banco hospedado:** versão efetiva, extensão instalada/disponível nessa branch, privilégios efetivos, revisão de migração implantada, espaço livre e consumo do plano. Não foi aberta conexão com o banco compartilhado. Após decisão de continuar, o operador pode conferir, somente em leitura:

```sql
SELECT version();
SELECT name, default_version, installed_version
FROM pg_available_extensions WHERE name = 'pg_trgm';
SELECT has_database_privilege(current_user, current_database(), 'CREATE');
SELECT extname, extversion FROM pg_extension WHERE extname = 'pg_trgm';
```

Disponibilidade publicada pelo provedor sustenta viabilidade, não autorização nem prova do ambiente. Instalação e índices futuros seguem Alembic. Criar índice em tabela existente pode bloquear escrita/consumir I/O; avaliar janela ou criação concorrente com o tratamento transacional próprio. Verificar remoção de índices inválidos, rollback e dependências; migration da extensão não deve removê-la automaticamente se outra função passar a depender dela.

**DOC/EST — custos:** páginas consultadas em 15/11 anunciam Neon Free com 1 GB de armazenamento e 100 CU-h/mês por projeto; Meilisearch Cloud a partir de US$20/mês, com variação regional. Não foram auditados contrato, franquias da conta ou impostos/câmbio. Não são orçamento aprovado. [Preços Neon](https://neon.com/pricing), [preços Meilisearch](https://www.meilisearch.com/pricing).

`pg_trgm` não exige contratar outro serviço, mas índice/escrita/CPU podem consumir franquia ou exigir plano maior. Medir tamanho real, duração da importação e utilização antes/depois em cópia nativa. O índice auxiliar não estima fielmente o armazenamento do catálogo. Mais sugestões elevam a frequência de consultas mesmo com pouca informação transmitida.

Meilisearch Community evita licença do motor, mas exige processo durável, memória, CPU, volume persistente, snapshots/dumps e recuperação. Não há evidência de capacidade ou orçamento reservado no UnDb. O Render Free atual suspende por inatividade e não oferece disco persistente: não serve como persistência confiável desse índice. Cloud muda o custo e a responsabilidade operacional; indisponibilidade do serviço também afeta a busca. [Render Free](https://render.com/docs/free), [instalação Meilisearch](https://www.meilisearch.com/docs/resources/self_hosting/getting_started/install_locally).

**EST:** dependência de `pg_trgm` é ligada à extensão PostgreSQL disponível em outros provedores, mas exportação/restauração exige suporte correspondente. Meilisearch acrescenta API, regras de ranking, formato/versão de índice e fornecedor de hosting. Manter PostgreSQL como fonte e exportação determinística reduz o custo de saída, sem eliminá-lo.

## 10. Impactos arquiteturais e atualização SIGAA

Tudo nesta seção é **EST/PROP**, sem contrato ou código alterado.

| Área | Aprimoramento literal | Com pg_trgm | Com Meilisearch |
|---|---|---|---|
| FastAPI | Validar termo/frequência, consulta limitada e projeção de sugestão se aprovada | Mesmo fluxo, candidatos e classificação no service/repository | Adaptador REST/SDK, timeout, orçamento de falha e fallback limitado |
| SQLAlchemy/modelos | Reutiliza campos; política de pontuação pode ser expressão de consulta | Reutiliza `nome_normalizado`; extensão e índice são suficientes para a POC, sem entidade nova | Models de catálogo continuam; rotina exporta documento derivado por UUID |
| Alembic | Nenhuma alteração demonstrada necessária ao ensaio | Extensão/índices versionados e revisão de privilégios | Sem extensão para o motor; eventual outbox durável exigiria modelo/migration aprovados |
| Endpoints/contratos | Não mudar silenciosamente arrays existentes para limite oito/envelope | Sugestão específica ou opt-in explícito evita truncar catálogo usado pela home/unidades | Mesmo contrato UnDb pode ocultar motor; não retornar formato nativo de hits ao frontend |
| Dependências/env | Pode aproveitar stack existente; não foi demonstrada dependência nova | Não exige pacote Python novo para as funções PostgreSQL; papel de migração pode bastar | Cliente/SDK a decidir, URL e chave privadas, configuração de indexação/timeout e processo adicional |
| Next.js | Popup acessível, seleção explícita, estados, foco e cancelamento; uma consulta por pausa/modalidade | Igual, com identificação de aproximação e respeito à ordem devolvida | Igual; frontend não conhece chaves nem sincronização |

**Contrato candidato, não definitivo:** consulta de sugestões por modalidade e termo, limite máximo de oito imposto no servidor; item com tipo, UUID, nome, código se disciplina, departamento e nome opcional de unidade. Metadado de correspondência pode distinguir literal/aproximado; correção deve ser campo separado e opcional, nunca recurso escolhido. Erro precisa continuar distinto de lista vazia. Não expor score como “confiança”. Rotas, nomes de campos, códigos HTTP e decisão entre nova rota/opt-in dependem da aprovação e do detalhamento posteriores.

Não impor limite global às rotas existentes: a home/unidades lê o catálogo completo e a busca de disciplinas une dois arrays. Ordenar antes de limitar e não reordenar só uma página como se fosse o conjunto global. Aprovar se relevância será exclusiva das sugestões ou opção adicional na lista; novo valor de `ordem` afetaria validações de contexto/`return_to` dos dois lados.

### Depois da importação e da reconciliação

**Mesmo PostgreSQL:** consulta do catálogo vê os dados confirmados na transação por unidade; índice é mantido pelo banco na mesma escrita. Nome normalizado já é atualizado no importador. Não há job de dicionário. Cache opcional deve expirar/invadidar por atualização de catálogo e considerar modalidade/normalização; sem cache de resultado negativo duradouro que oculte registro novo. A busca não refaz SIGAA em tempo real.

**Meilisearch:** publicar somente após commit da unidade, com UUID canônico e campo de versão; monitorar tarefa até `succeeded`, repetir de forma idempotente e tratar renomes, remoções e aliases. Mudança de nome da unidade também deve atualizar os documentos derivados, mesmo sem nome de professor alterado. Importação parcial não pode apagar o índice como se o catálogo completo estivesse ausente.

Há janela de falha entre commit PostgreSQL e envio externo. Para a escala documentada, uma exportação completa periódica com conferência e troca de índice pode ser mais simples que eventos por oferta, mas tem atraso explícito; sincronização imediata confiável exigiria outbox ou mecanismo durável aprovado. Não prometer atomicidade entre os dois serviços.

Reconstrução proposta: ler snapshot consistente apenas do catálogo público e sem aliases de origem, criar índices temporários, aplicar configurações, aguardar tarefas, conferir IDs/contagens e casos de regressão, depois trocar os índices. Interromper sem trocar se falhar. Guardar versão das configurações e um procedimento de dump/snapshot/restore compatível; provar recuperação em ambiente isolado. Enquanto o índice está atrasado/indisponível, usar busca literal limitada no PostgreSQL ou informar falha, conforme política aprovada. Validar IDs atuais no catálogo para não apresentar exclusão/alias obsoleto como recurso novo. [Troca de índices](https://www.meilisearch.com/blog/zero-downtime-index-deployment).

## 11. Segurança, acessibilidade, métricas e critérios propostos

### Riscos e tratamento futuro — PROP

| Risco | Tratamento a validar |
|---|---|
| Frequência e termos muito amplos | Debounce não é rate limit; limitar frequência no servidor/entrada, tamanho do termo, quantidade de termos, tempo e quantidade de resultados. Reutilizar consulta por termo/modalidade, sem baixar catálogo a cada tecla |
| Curingas e SQL | Entrada vinculada, tratamento literal de `%`/`_`, mínimo no servidor e controle de carga; não mascarar SQL com concatenação |
| Indisponibilidade | Timeout, erro acessível e nova tentativa; aproximado não transforma falha em “nenhum resultado”. Meili indisponível deve ter fallback previamente limitado para não transferir pico ilimitado ao banco |
| Exposição | Projetar só dados institucionais já públicos; não indexar usuários, e-mails, sessões, denúncias, decisões privadas ou avaliações individuais. Não ampliar acesso por ser busca fuzzy |
| Chaves/serviço externo | Credenciais só no backend/operador, chave de pesquisa e de escrita separadas com escopo mínimo, rede/TLS e rotação; não expor chave administrativa em `NEXT_PUBLIC_*`. [Segurança Meilisearch](https://www.meilisearch.com/docs/resources/self_hosting/security/basic_security) |
| Foco e leitores de tela | Padrão combobox editável com listbox, `aria-expanded`, `aria-controls`, opção ativa via `aria-activedescendant`, nomes acessíveis com unidade/código; status de carregamento/contagem em região live moderada. Não mover foco quando resposta chega |
| Teclado/toque e corrida | Teclas da seção 4; preservar edição nativa, foco visível, Escape e Tab; cancelar/invalidar consultas e seleção; testar blur/clique/toque sem fechar antes de ativar a opção |
| Privacidade operacional | Minimizar logs de termos; não assumir que toda consulta digitada é pública só porque o catálogo é. Registrar contagens/latências sem credenciais ou conteúdo pessoal desnecessário |

O padrão de interação de referência é o [combobox do WAI-ARIA APG](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/). Leitura documental não certifica acessibilidade. Futura validação deve cobrir teclado integral, NVDA com navegador desktop e VoiceOver/TalkBack em celular, zoom e viewport 320/390/768/1280, com teclado virtual e orientação. Nenhum desses testes foi executado para um popup inexistente.

### Critérios candidatos para decisão de Nicolas

Os alvos abaixo são **propostas**, não requisitos ou gates aprovados. São escolhidos para exigir ganho sobre a baseline e limitar a piora observada, não porque a amostra pequena os tenha comprovado.

| Métrica / cenário | Definição e alvo proposto | Justificativa / lacuna |
|---|---|---|
| Preservação literal | 100% dos casos exatos/parciais existentes mantêm os UUIDs relevantes; nenhuma fusão de homônimos/retorno de alias | Não perder RF05–RF07 nem a reconciliação vigente |
| Precisão@8 | TP/(TP+FP) entre sugestões retornadas, meta ≥98% no conjunto reservado | POC trgm ficou em 97,7%; exige melhorar a política que acrescentou Mario |
| Cobertura@8 | Relevantes recuperados/relevantes julgados, meta ≥90% para nomes com erros e melhora sobre a baseline desse recorte | Meta de benefício; estratificar erros, nomes compostos e unidades, sem esconder piora em subgrupos |
| Posição | MRR ≥0,90 e registrar Recall@1/3/8 | POC atingiu 0,909 no conjunto misto; corpus reservado precisa confirmar descoberta nas primeiras posições |
| Correção indevida | Correções rejeitadas por julgadores/total de correções oferecidas, meta ≤1%; publicar também cobertura/abstenção | Sugestão errada pode direcionar à pessoa errada; não obter taxa baixa abstendo em tudo |
| Latência | p95 HTTP da API aquecida ≤300 ms; p95 entre última tecla e sugestões ≤700 ms com rede móvel definida | Orçamento proposto de 300 ms de debounce + API + rede/renderização; medir partida a frio separadamente, sem escondê-la na média |
| Carga e atualização | Ensaiar catálogo sintético de 12 mil registros com 10 sessões simultâneas e 1 consulta/s por sessão; medir CPU, planos, erros e custo da importação | Ponto inicial de carga para planejamento, não estimativa de tráfego real. Se Meili, medir lag p95 e propor ≤60 s após commit por unidade |
| Concorrência e inclusão | Zero respostas antigas visíveis na sequência controlada; até oito opções; teclado completo e anúncio correto de estados | Cenários determinísticos verificáveis, seguidos de teste humano com tecnologias assistivas |

Para calibração, propor pelo menos 100 consultas julgadas, cobrindo os 14 cenários exigidos, nomes próximos, homônimos da mesma/diferentes unidades, códigos vizinhos e negativos difíceis. Separar previamente ajuste e validação; não escolher limiar no mesmo corpus usado para anunciar acerto. Usar dois julgadores, resolver divergências com registro e apresentar denominadores/intervalos de incerteza. O número é plano de coleta proposto, não garantia estatística: para sustentar taxa de erro de correção ≤1% será necessária amostra suficiente de **correções oferecidas**, possivelmente centenas, e intervalo binomial; poucos acertos sintéticos não bastam.

## 12. Recomendação técnica e alternativas consideradas

**Recomendar ajustes**, com esta direção técnica para o PO avaliar:

1. Aprovar ou recortar **autocompletar literal do catálogo** como entrega independente, aproveitando campos/normalização/debounce existentes. Antes de qualquer implementação, definir oito no total, modalidade, seleção, acessibilidade e contrato que preserve listagens atuais.
2. Se tolerância a erros for prioridade, preferir uma próxima validação de **PostgreSQL + pg_trgm**, com literal primeiro e aproximação como fallback identificado. A evidência concreta é recuperar seis consultas positivas adicionais sobre a baseline, mantendo o catálogo como única fonte e sem operar outro serviço. A evidência também exige ajustar falso positivo e testar plano/custo em PostgreSQL 16 nativo.
3. Manter **“Você quis dizer…” pendente de calibração**. Não oferecer correção automática ou tratar score como certeza. O corpus mostra que um corte global não resolve a ambiguidade.

| Possibilidade exigida | Recomendação e motivo |
|---|---|
| Manter exatamente como está | Aceitável se o PO não priorizar a melhoria; satisfaz o núcleo literal aprovado, mas mantém oito consultas positivas perdidas no corpus |
| Aprimorar sem nova tecnologia | Boa primeira opção para sugestões literais e política de pontuação/limites; medição recuperou um caso a mais, sem resolver erros de letras |
| Adotar pg_trgm | Candidato preferencial para erros de nome, **condicionado** às validações e autorização; ganho de cobertura medido, custo de índices/CPU ainda depende do ambiente nativo |
| Adotar Meilisearch | Não recomendado agora: nenhuma limitação medida da opção PostgreSQL que compense sincronização, processo persistente e custo; execução local bloqueada impede comparação empírica |
| Solução híbrida | Literal + trgm no mesmo PostgreSQL é justificável como política de candidatos; PostgreSQL + Meilisearch só se carga/relevância/SLO medidos no futuro justificarem dois mecanismos. Não confundir com busca semântica/vetorial, sem necessidade demonstrada aqui |
| Adiar | Adequado para correção de grafia e para adoção de extensão enquanto faltarem calibração/ambiente; adiar toda a melhoria se o PO priorizar operação/importação e orçamento |

**EST — esforço relativo:** ajustes literais/contrato, popup acessível, calibração e testes são frentes comuns a qualquer opção. `pg_trgm` acrescenta migration/índice e ensaio nativo; Meilisearch acrescenta também provisionamento, exportação, consistência, observabilidade e recuperação. Não há capacidade de equipe/velocidade ou orçamento aprovado que sustente prometer dias de entrega. A experiência em SQLAlchemy/Alembic já existe na stack; novo motor amplia a manutenção para a equipe acadêmica sem benefício adicional medido.

## 13. Decisão pendente do PO e validação da entrega

### Material para Vinícius apresentar a Nicolas

| Ponto de decisão — todos Pending Decision | Opções que o PO precisa explicitar |
|---|---|
| Funcionalidades | Autocompletar literal, tolerância em nomes e/ou correção; podem ter prioridades diferentes |
| Tecnologia | Manter/aprimorar literal, autorizar extensão após ensaio nativo, ou pedir comparação externa adicional |
| Comportamento | Oito no total e modalidade; termos curtos; política de pontuação; aproximação como fallback; códigos; homônimos; escolha manual |
| Critérios | Aprovar/ajustar métricas, corpus, limiares calibrados, acessibilidade e orçamento de latência/carga |
| Infraestrutura | Operador responsável por conferir PostgreSQL/extensão/privilégios/espaço; orçamento e manutenção, se novo serviço for considerado |
| Prioridade e momento | Sprint/release e responsáveis; nenhuma prioridade foi presumida pela recomendação |

Se houver autorização explícita, **primeiro atualizar `docs/requisitos.md`**, depois contratos, documentos derivados e eventual decisão arquitetural. Só então planejar implementação/migrations/frontend sob a autorização delimitada. Este estudo não inicia essa sequência nem encerra a issue como aceita.

### Verificações desta entrega

- **MED:** 26 consultas e paridade de conjuntos dos repositories SQLite/PostgreSQL embarcado; varredura de quatro cortes; 12 mil linhas para planos/índices; arquivos de evidência reproduzíveis.
- **MED:** `python -m unittest tests.test_api_institucional tests.test_reconciliacao_professores -v`: 20 testes, **19 aprovados e um ignorado**, por exigir PostgreSQL nativo descartável. Não houve execução dessa integração nativa.
- **OBS:** testes existentes de frontend cobrem união por ID, ordenação, estados, homônimos, mínimo de termo e corrida de respostas; foram lidos, **não reexecutados** nesta entrega documental. Registros anteriores não substituem teste de nova UI.
- MkDocs estrito e revisão de links: resultado final registrado junto dos comandos na [reprodução](evidencias/issue-251/reproducao.md).
- Nenhum requisito/ADR aprovado, contrato, modelo, consulta da aplicação, dependência do projeto ou banco compartilhado foi alterado. PGlite e venv são ferramentas isoladas do ensaio, sem inclusão nos manifests. A publicação posterior deste estudo em branch/PR documental foi autorizada separadamente; não houve merge ou deploy.

## 14. Referências consultadas

### Projeto e rastreabilidade — revisão cd7a27c

- [Issue #251](https://github.com/unb-mds/2026-02-UnDb/issues/251), descrição e comentários em 15/11/2026; [requisitos completos](../requisitos.md) e [arquitetura completa](../arquitetura.md).
- [Governança](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/skills/governance/project-governance/SKILL.md), [limites humanos](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/skills/governance/project-governance/references/HUMAN_APPROVAL_BOUNDARIES.md), [arquitetura](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/skills/engineering/architecture/SKILL.md), [testing](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/skills/engineering/testing/SKILL.md), [PostgreSQL e referências](https://github.com/unb-mds/2026-02-UnDb/tree/cd7a27c/skills/technology/postgresql), [requisitos](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/skills/process/requirements/SKILL.md).
- [Normalização](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/backend/app/domain/texto.py), [repository de professores](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/backend/app/repositories/professor_repository.py), [de disciplinas](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/backend/app/repositories/disciplina_repository.py), [service](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/backend/app/services/institucional_service.py), [routers](https://github.com/unb-mds/2026-02-UnDb/tree/cd7a27c/backend/app/routers), [schemas](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/backend/app/schemas/institucional.py), [models](https://github.com/unb-mds/2026-02-UnDb/tree/cd7a27c/backend/app/models) e [migrations](https://github.com/unb-mds/2026-02-UnDb/tree/cd7a27c/backend/alembic).
- [Frontend e documentação](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/frontend/README.md), [contrato da busca #203](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/frontend/docs/ui-busca-203.md), [verificação histórica #203](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/frontend/docs/verificacao-ui-busca-203.md), [BuscaInstitucional](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/frontend/src/components/busca-institucional.tsx), [services](https://github.com/unb-mds/2026-02-UnDb/tree/cd7a27c/frontend/src/lib/services), [contexto/ordenação](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/frontend/src/lib/contexto-busca.ts), [testes](https://github.com/unb-mds/2026-02-UnDb/tree/cd7a27c/frontend/tests).
- [Importador](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/backend/app/services/sigaa_import_service.py), [integração SIGAA](../importacao-sigaa.md), [operação SIGAA](../operacao-importacao-sigaa.md), [identidades](../identidades-docentes.md), [importação histórica Neon](importacao-neon-2026-11-10.md), [hospedagem](../hospedagem.md), [acesso mínimo](../acesso-postgresql-api.md), [qualidade](../qualidade.md), [testes institucionais](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/backend/tests/test_api_institucional.py) e [reconciliação](https://github.com/unb-mds/2026-02-UnDb/blob/cd7a27c/backend/tests/test_reconciliacao_professores.py).

### Fontes oficiais externas — consulta em 15/11/2026

- PostgreSQL: [pg_trgm current](https://www.postgresql.org/docs/current/pgtrgm.html) e [versão 16](https://www.postgresql.org/docs/16/pgtrgm.html).
- [SQLAlchemy PostgreSQL](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html) e [operações Alembic](https://alembic.sqlalchemy.org/en/latest/ops.html).
- Neon: [pg_trgm](https://neon.com/docs/extensions/pg_trgm) e [preços/franquias](https://neon.com/pricing). Render: [limitações do Free](https://render.com/docs/free).
- Meilisearch: [documentação](https://www.meilisearch.com/docs), [tolerância](https://www.meilisearch.com/docs/capabilities/full_text_search/relevancy/typo_tolerance_settings), [ranking](https://www.meilisearch.com/docs/capabilities/full_text_search/relevancy/ranking_rules), [prefixos](https://www.meilisearch.com/docs/resources/internals/prefix), [idiomas](https://www.meilisearch.com/docs/resources/help/language), [busca/score](https://www.meilisearch.com/docs/reference/api/search/search-with-post), [indexação](https://www.meilisearch.com/docs/capabilities/indexing/overview), [troca de índices](https://www.meilisearch.com/blog/zero-downtime-index-deployment), [segurança](https://www.meilisearch.com/docs/resources/self_hosting/security/basic_security), [instalação](https://www.meilisearch.com/docs/resources/self_hosting/getting_started/install_locally), [release ensaiada](https://github.com/meilisearch/meilisearch/releases/tag/v1.56.2) e [preços](https://www.meilisearch.com/pricing).
- [PGlite — extensões](https://pglite.dev/extensions/) e [WAI-ARIA APG — combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/).
