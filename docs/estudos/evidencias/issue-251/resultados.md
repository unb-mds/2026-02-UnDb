# Evidências reproduzíveis — busca, Issue #251

[Avaliação e interpretação](../../avaliacao-busca-autocomplete-issue-251.md).

Dados integralmente sintéticos. Listas em ordem de posição (primeiro item = posição 1). FP indica resultado fora do julgamento de intenção; ∅ indica ausência. P12 é alias de P1 e permanece fora de todas as consultas de listagem.

## Catálogo

| ID | Tipo | Nome | Código | Unidade |
|---|---|---|---|---|
| P1 | professores | Maria Emília dos Santos | — | CIC |
| P2 | professores | Maria Emília dos Santos | — | MAT |
| P3 | professores | Maria Elisa de Sousa | — | CIC |
| P4 | professores | João-Pedro D'Ávila | — | ENM |
| P5 | professores | José Álvaro Lima | — | MAT |
| P6 | professores | Ana Clara Costa | — | CIC |
| P7 | professores | Ana Carolina Costa | — | MAT |
| P8 | professores | Bruno Nascimento | — | CIC |
| P9 | professores | José Lima | — | CIC |
| P10 | professores | Mario Santos | — | CIC |
| P11 | professores | Santos | — | ENM |
| P12 | professores | Maria Emília dos Santos | — | CIC |
| D1 | disciplinas | Algoritmos e Programação de Computadores | CIC0004 | CIC |
| D2 | disciplinas | Programação Orientada a Objetos | CIC0005 | CIC |
| D3 | disciplinas | Cálculo 1 | MAT0025 | MAT |
| D4 | disciplinas | Cálculo 2 | MAT0026 | MAT |
| D5 | disciplinas | Banco de Dados | CIC0099 | CIC |
| D6 | disciplinas | Estatística Aplicada | EST0101 | EST |
| D7 | disciplinas | Métodos Numéricos | ENM0001 | ENM |
| D8 | disciplinas | Fundamentos Teóricos da Computação | CIC0002 | CIC |
| D9 | disciplinas | Algoritmos | FGA0004 | FGA |
| D10 | disciplinas | Algoritmos e Estruturas de Dados | CIC0014 | CIC |

## Casos e ordenação

Meilisearch: não executado em todos os casos (bloqueio pelo Controle de Aplicativo do Windows). Não há resultados nem tempos atribuídos a esse motor. O caso 12 foi chamado diretamente na camada SQL; a interface vigente o impede.

| Caso | Cenário / termo | Relevantes | Atual | Literal experimental | pg_trgm experimental (0,3) |
|---|---|---|---|---|---|
| 01 | nome exato: `Maria Emília dos Santos` | P1, P2 | P1, P2 | P1, P2 | P1, P2 |
| 02 | nome parcial: `emilia` | P1, P2 | P1, P2 | P1, P2 | P1, P2 |
| 03 | sobrenome: `santos` | P1, P2, P10, P11 | P1, P2, P10, P11 | P1, P2, P10, P11 | P11, P1, P2, P10 |
| 04 | transposição: `emliia` | P1, P2 | ∅ | ∅ | P1, P2 |
| 05 | caixa/acentos: `MARIA EMILIA DOS SANTOS` | P1, P2 | P1, P2 | P1, P2 | P1, P2 |
| 06 | composto/omissão: `maria emlia santos` | P1, P2 | ∅ | ∅ | P1, P2 |
| 07 | homônimos: `maria emília` | P1, P2 | P1, P2 | P1, P2 | P1, P2 |
| 08 | nome exato: `Algoritmos e Programação de Computadores` | D1 | D1 | D1 | D1 |
| 09 | nome parcial: `programacao` | D1, D2 | D1, D2 | D1, D2 | D2, D1 |
| 10 | código exato: `CIC0004` | D1 | D1 | D1 | D1 |
| 11 | código/omissão: `CIC004` | D1 | ∅ | ∅ | ∅ |
| 12 | curto; UI não consulta: `a` | ∅ | P7 **(FP)**, P6 **(FP)**, P8 **(FP)**, P4 **(FP)**, P5 **(FP)**, P9 **(FP)**, P3 **(FP)**, P1 **(FP)**, P2 **(FP)**, P10 **(FP)**, P11 **(FP)** | ∅ | P7 **(FP)**, P6 **(FP)**, P5 **(FP)**, P4 **(FP)**, P8 **(FP)**, P9 **(FP)**, P3 **(FP)**, P1 **(FP)** |
| 13 | sem correspondência: `zzqxv` | ∅ | ∅ | ∅ | ∅ |
| 14 | múltiplos candidatos: `ana costa` | P6, P7 | P7, P6 | P7, P6 | P7, P6 |
| 15 | duplicação: `emiilia` | P1, P2 | ∅ | ∅ | P1, P2 |
| 16 | espaços/ordem: `  santos   maria  ` | P1, P2 | P1, P2 | P1, P2 | P1, P2, P10 **(FP)** |
| 17 | pontuação omitida: `joao pedro davila` | P4 | ∅ | P4 | P4 |
| 18 | pontuação preservada: `joao-pedro d'avila` | P4 | P4 | P4 | P4 |
| 19 | prefixo de código: `CIC000` | D1, D2, D8 | D1, D8, D2 | D1, D8, D2 | D8, D1, D2 |
| 20 | acentos/ambiguidade: `calculo` | D3, D4 | D3, D4 | D3, D4 | D3, D4 |
| 21 | duas letras; substring: `ma` | P1, P2, P3, P5, P9, P10 | P5, P9, P3, P1, P2, P10 | P5, P9, P3, P1, P2, P10 | P3, P1, P2, P10, P9, P5 |
| 22 | curingas LIKE; nenhuma intenção nominal: `%%` | ∅ | P7 **(FP)**, P6 **(FP)**, P8 **(FP)**, P4 **(FP)**, P5 **(FP)**, P9 **(FP)**, P3 **(FP)**, P1 **(FP)**, P2 **(FP)**, P10 **(FP)**, P11 **(FP)** | ∅ | ∅ |
| 23 | nomes incompatíveis: `maria alvaro` | ∅ | ∅ | ∅ | ∅ |
| 24 | código/transposição; intenção não inferível: `CIC0400` | D1 | ∅ | ∅ | ∅ |
| 25 | nome/transposição: `algortimos` | D1, D9, D10 | ∅ | ∅ | D9, D10, D1 |
| 26 | sobrenome/omissão: `nascimnto` | P8 | ∅ | ∅ | P8 |

## Falsos negativos

| Caso | Atual | Literal | pg_trgm 0,3 |
|---|---|---|---|
| 01 | — | — | — |
| 02 | — | — | — |
| 03 | — | — | — |
| 04 | P1, P2 | P1, P2 | — |
| 05 | — | — | — |
| 06 | P1, P2 | P1, P2 | — |
| 07 | — | — | — |
| 08 | — | — | — |
| 09 | — | — | — |
| 10 | — | — | — |
| 11 | D1 | D1 | D1 |
| 12 | — | — | — |
| 13 | — | — | — |
| 14 | — | — | — |
| 15 | P1, P2 | P1, P2 | — |
| 16 | — | — | — |
| 17 | P4 | — | — |
| 18 | — | — | — |
| 19 | — | — | — |
| 20 | — | — | — |
| 21 | — | — | — |
| 22 | — | — | — |
| 23 | — | — | — |
| 24 | D1 | D1 | D1 |
| 25 | D1, D9, D10 | D1, D9, D10 | — |
| 26 | P8 | P8 | — |

## Tempos por consulta

Milissegundos, p50 / p95 de 30 repetições após aquecimento. Incluem ponte JavaScript/WASM e tratamento local, sem rede, FastAPI, React ou partidas a frio. Atual de disciplina inclui duas consultas sequenciais na conexão embarcada e ordenação local; o navegador faz a dupla em paralelo. Não servem para comparar latência HTTP de produção. No caso 12, a variante literal retorna sem SQL.

| Caso | Atual p50 / p95 | Literal p50 / p95 | pg_trgm p50 / p95 |
|---|---|---|---|
| 01 | 0,627 / 1,180 | 0,447 / 1,056 | 0,863 / 1,981 |
| 02 | 0,474 / 0,784 | 0,364 / 0,537 | 0,601 / 1,071 |
| 03 | 0,491 / 0,650 | 0,330 / 0,410 | 0,588 / 0,731 |
| 04 | 0,413 / 0,661 | 0,314 / 0,462 | 0,572 / 0,836 |
| 05 | 0,479 / 0,674 | 0,342 / 0,497 | 0,666 / 0,886 |
| 06 | 0,437 / 0,641 | 0,325 / 0,477 | 0,661 / 0,929 |
| 07 | 0,520 / 1,197 | 0,422 / 0,900 | 0,702 / 1,666 |
| 08 | 1,609 / 2,477 | 0,693 / 1,136 | 1,453 / 2,643 |
| 09 | 1,481 / 2,107 | 0,598 / 0,907 | 1,103 / 1,591 |
| 10 | 0,997 / 2,137 | 0,421 / 0,972 | 0,319 / 0,799 |
| 11 | 0,763 / 1,491 | 0,286 / 0,470 | 0,232 / 0,436 |
| 12 | 0,538 / 0,586 | 0,002 / 0,002 | 0,537 / 0,602 |
| 13 | 0,410 / 1,180 | 0,345 / 1,116 | 0,554 / 1,475 |
| 14 | 0,425 / 0,730 | 0,301 / 0,526 | 0,554 / 0,917 |
| 15 | 0,362 / 0,402 | 0,284 / 0,483 | 0,517 / 0,756 |
| 16 | 0,432 / 0,734 | 0,315 / 0,408 | 0,567 / 0,982 |
| 17 | 0,400 / 0,556 | 0,310 / 0,502 | 0,602 / 0,909 |
| 18 | 0,428 / 0,832 | 0,309 / 0,780 | 0,569 / 1,305 |
| 19 | 0,631 / 0,845 | 0,263 / 0,336 | 0,204 / 0,257 |
| 20 | 0,635 / 0,998 | 0,266 / 0,450 | 0,509 / 0,818 |
| 21 | 0,447 / 0,514 | 0,294 / 0,487 | 0,477 / 0,747 |
| 22 | 0,491 / 0,538 | 0,261 / 0,317 | 0,409 / 0,502 |
| 23 | 0,368 / 0,425 | 0,276 / 0,397 | 0,508 / 0,587 |
| 24 | 0,643 / 0,988 | 0,306 / 0,492 | 0,217 / 0,346 |
| 25 | 0,570 / 1,058 | 0,266 / 0,459 | 0,477 / 0,983 |
| 26 | 0,342 / 0,502 | 0,263 / 0,613 | 0,496 / 1,052 |

## Métricas lexicais

24 consultas: excluídos 12 (UI bloqueia) e 22 (sonda de curingas), apresentados separadamente acima. 45 pares consulta/registro relevantes, 22 consultas positivas e duas negativas. TP/FP/FN são contados por par; MRR usa a posição do primeiro relevante e zero quando ausente.

| Variante | TP / FP / FN | Precisão | Cobertura | MRR | Consultas positivas com acerto |
|---|---|---|---|---|---|
| atual | 32 / 0 / 13 | 100,0% | 71,1% | 0,636 | 14/22 |
| literal | 33 / 0 / 12 | 100,0% | 73,3% | 0,682 | 15/22 |
| trgm | 43 / 1 / 2 | 97,7% | 95,6% | 0,909 | 20/22 |

## Varredura de limiar

Conjunto completo de 26 consultas, inclusive as duas sondas de controle. Os oito retornos indevidos da consulta de uma letra são contabilizados aqui; não confundir esta precisão com a métrica lexical. Os casos 11 e 24 permanecem ausentes em todos os limiares porque aproximação em código foi desativada deliberadamente.

| Limiar inclusivo do menor word_similarity por termo | TP / FP / FN | Precisão | Cobertura | MRR |
|---|---|---|---|---|
| 0,3 | 43 / 9 / 2 | 82,7% | 95,6% | 0,909 |
| 0,4 | 43 / 9 / 2 | 82,7% | 95,6% | 0,909 |
| 0,5 | 38 / 9 / 7 | 80,9% | 84,4% | 0,818 |
| 0,6 | 35 / 9 / 10 | 79,5% | 77,8% | 0,727 |

## Índices no ensaio auxiliar

12.000 linhas artificiais; consulta `nome % 'maria emlia santos'`, limiar padrão de `%` (0,3). Este é outro SQL, destinado a verificar planos e armazenamento: não comprova indexação da consulta por mínimo de `word_similarity` usada no corpus. GiST usa assinatura padrão. Os índices foram criados um por vez.

| Índice | p50 / p95 (ms) | Tabela (bytes) | Índices (bytes) | Plano |
|---|---|---|---|---|
| sem_indice | 32,277 / 56,343 | 1056768 | 0 | Seq Scan |
| gin | 0,963 / 1,435 | 1056768 | 679936 | Bitmap Heap Scan |
| gist | 2,346 / 4,093 | 1056768 | 1351680 | Index Scan |

Planos completos, buffers, amostras individuais, pontuações e versões: [resultados.json](resultados.json). SQL do repository, parâmetros e judgments: [dataset.json](dataset.json). Comandos e limitações: [reprodução](reproducao.md).
