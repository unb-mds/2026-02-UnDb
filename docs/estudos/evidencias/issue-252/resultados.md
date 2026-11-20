# Resultados exploratórios — Issue #252

[Relatório técnico](../../avaliacao-ofensas-disfarcadas-issue-252.md) · [Dados completos](resultados.json) · [Corpus](casos.json)

Rótulos propostos; revisão humana pendente. API real e triagem real não executadas. Os três controles usam mocks e o serviço atual; não medem qualidade da IA.

| Variante local | TP | FN | FP | TN |
|---|---:|---:|---:|---:|
| atual | 8 | 24 | 0 | 24 |
| busca_nfkd | 10 | 22 | 0 | 24 |
| invisiveis | 13 | 19 | 0 | 24 |
| unicode | 15 | 17 | 0 | 24 |
| separadores_repeticoes | 22 | 10 | 0 | 24 |
| leet_contextual | 28 | 4 | 1 | 23 |
| leet_4_como_e | 29 | 3 | 2 | 22 |

Contextuais excluídos de TP/FN/FP/TN; sinal lexical não prova ofensa.

Códigos dos controles: P = PENDENTE, U = PUBLICADO apenas no objeto em memória. Sempre sem avaliação persistida ou publicada.

| ID | Entrada escapada | Grupo | Local atual | Erro local | Esperada proposta | IA real / combinada real | Mock sem sinal / sinal / falha |
|---|---|---|---|---|---|---|---|
| P01 | `Que merda de aula.` | positivo | PALAVRAO | TP | PENDENTE | não executadas | P / P / P |
| P02 | `Voc\xea \xe9 um idiota.` | positivo | OFENSA_PESSOAL | TP | PENDENTE | não executadas | P / P / P |
| P03 | `Que porra!` | positivo | PALAVRAO | TP | PENDENTE | não executadas | P / P / P |
| P04 | `Vai   se foder!` | positivo | XINGAMENTO | TP | PENDENTE | não executadas | P / P / P |
| P05 | `Seu OT\xc1RIO!` | positivo | XINGAMENTO | TP | PENDENTE | não executadas | P / P / P |
| P06 | `ID\xcdOTA!` | positivo | OFENSA_PESSOAL | TP | PENDENTE | não executadas | P / P / P |
| P07 | `Que m4rda de aula.` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P08 | `Que m3rda de aula.` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P09 | `Voc\xea \xe9 um b4b4c4.` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P10 | `Seu 1d10ta!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P11 | `Que m.e.r.d.a!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P12 | `Seu b-a-b-a-c-a!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P13 | `Voc\xea \xe9 i d i o t a!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P14 | `Que m er da!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P15 | `Que meeerda!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P16 | `Seu babacaaaa!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P17 | `Que me\u200brda!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P18 | `Seu idi\u200dota!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P19 | `Que por\ufeffra!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P20 | `Que \uff4d\uff45\uff52\uff44\uff41!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P21 | `Seu \U0001d41b\U0001d41a\U0001d41b\U0001d41a\U0001d41c\U0001d41a!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P22 | `Que m\u0435rda!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P23 | `Seu b\u0430b\u0430c\u0430!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P24 | `Seu B.4.B.4.C.4!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P25 | `Que M\u200b3 R D A!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P26 | `Vai.se.foder!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P27 | `Vou te matar.` | positivo | AMEACA | TP | PENDENTE | não executadas | P / P / P |
| P28 | `V0u te m4t4r.` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P29 | `Que meeeeeeeerda!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P30 | `Que \u1d0derda!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| P31 | `Seu imbecil!` | positivo | XINGAMENTO | TP | PENDENTE | não executadas | P / P / P |
| P32 | `Que m....e....r....d....a!` | positivo | ∅ | FN | PENDENTE | não executadas | U / P / P |
| N01 | `A did\xe1tica foi ruim; n\xe3o recomendo.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N02 | `As provas cobraram assuntos ausentes das aulas.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N03 | `A organiza\xe7\xe3o da disciplina foi p\xe9ssima.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N04 | `Reprovei e discordo dos crit\xe9rios de corre\xe7\xe3o.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N05 | `A an\xe1lise discute a imbecilidade do argumento.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N06 | `O cap\xedtulo descreve a anatomia escrotal.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N07 | `O texto aborda a canalhice como conceito liter\xe1rio.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N08 | `Estudamos a fam\xedlia Otariidae.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N09 | `Tirei 4 na P1 e 3 na P2, com m\xe9dia 3,5.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N10 | `A matriz 4 por 3 tem 12 entradas.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N11 | `Em 2026.2 cursei CIC0004 e MAT0031.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N12 | `Usamos C++, C# e Python 3.12 no laborat\xf3rio.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N13 | `A prova separa os itens a, b, c e d.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N14 | `O algoritmo processa uma fila e uma pilha.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N15 | `Conforme o cap\xedtulo 3, se\xe7\xe3o 4, a hip\xf3tese foi refutada.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N16 | `A fun\xe7\xe3o f(x)=\u03b1x+\u03b2 representa o modelo.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N17 | `A discuss\xe3o cita a\xe7\xe3o, \xf3rg\xe3o e frequ\xeancia.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N18 | `A did\xe1\u200btica precisa melhorar.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N19 | `Usamos a vari\xe1vel prefixo_merda_sufixo no exerc\xedcio de strings.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N20 | `A vari\xe1vel m3rda armazena o resultado da matriz no exemplo.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N21 | `No exerc\xedcio, m4rda \xe9 o c\xf3digo de uma c\xe9lula.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N22 | `O material \xe9 insuficiente e as aulas s\xe3o confusas.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N23 | `A bibliografia inclui o artigo intitulado Cr\xedtica da raz\xe3o pura.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| N24 | `A convers\xe3o hexadecimal usa 0x4A e 0x3E.` | negativo | ∅ | TN | PUBLICADO | não executadas | U / P / P |
| C01 | `O texto cita a palavra merda para analisar linguagem.` | contextual | PALAVRAO | contextual | PENDENTE | não executadas | P / P / P |
| C02 | `N\xe3o chame ningu\xe9m de idiota.` | contextual | OFENSA_PESSOAL | contextual | PENDENTE | não executadas | P / P / P |
| C03 | `O escroto foi descrito no material de anatomia.` | contextual | XINGAMENTO | contextual | PENDENTE | não executadas | P / P / P |
| C04 | `Essa prova foi de matar.` | contextual | ∅ | contextual | a julgar | não executadas | U / P / P |
| C05 | `O argumento foi idiota ou apenas equivocado?` | contextual | OFENSA_PESSOAL | contextual | PENDENTE | não executadas | P / P / P |
| C06 | `A aula foi um lixo.` | contextual | ∅ | contextual | a julgar | não executadas | U / P / P |
