# Resultados da ampliação numérica — #252

[Relatório](../../implementacao-substituicoes-issue-252.md) · [Dados completos](resultados-leet.json)

Rótulos exploratórios; IA real não executada. Fluxos usam mocks, sem publicação.

| Camada | TP | FN | FP | TN |
|---|---:|---:|---:|---:|
| anterior_239 | 10 | 36 | 0 | 36 |
| etapa1 | 24 | 22 | 0 | 36 |
| leet | 42 | 4 | 3 | 33 |

| ID | Texto escapado | Grupo | Antes | Depois | Erro depois | Decisão controlada antes/depois (IA sem sinal) |
|---|---|---|---|---|---|---|
| P01 | `Que merda de aula.` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| P02 | `Voc\xea \xe9 um idiota.` | positivo | OFENSA_PESSOAL | OFENSA_PESSOAL | TP | PENDENTE / PENDENTE |
| P03 | `Que porra!` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| P04 | `Vai   se foder!` | positivo | XINGAMENTO | XINGAMENTO | TP | PENDENTE / PENDENTE |
| P05 | `Seu OT\xc1RIO!` | positivo | XINGAMENTO | XINGAMENTO | TP | PENDENTE / PENDENTE |
| P06 | `ID\xcdOTA!` | positivo | OFENSA_PESSOAL | OFENSA_PESSOAL | TP | PENDENTE / PENDENTE |
| P07 | `Que m4rda de aula.` | positivo | ∅ | ∅ | FN | PUBLICADO / PUBLICADO |
| P08 | `Que m3rda de aula.` | positivo | ∅ | PALAVRAO | TP | PUBLICADO / PENDENTE |
| P09 | `Voc\xea \xe9 um b4b4c4.` | positivo | ∅ | XINGAMENTO | TP | PUBLICADO / PENDENTE |
| P10 | `Seu 1d10ta!` | positivo | ∅ | OFENSA_PESSOAL | TP | PUBLICADO / PENDENTE |
| P11 | `Que m.e.r.d.a!` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| P12 | `Seu b-a-b-a-c-a!` | positivo | XINGAMENTO | XINGAMENTO | TP | PENDENTE / PENDENTE |
| P13 | `Voc\xea \xe9 i d i o t a!` | positivo | OFENSA_PESSOAL | OFENSA_PESSOAL | TP | PENDENTE / PENDENTE |
| P14 | `Que m er da!` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| P15 | `Que meeerda!` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| P16 | `Seu babacaaaa!` | positivo | XINGAMENTO | XINGAMENTO | TP | PENDENTE / PENDENTE |
| P17 | `Que me\u200brda!` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| P18 | `Seu idi\u200dota!` | positivo | OFENSA_PESSOAL | OFENSA_PESSOAL | TP | PENDENTE / PENDENTE |
| P19 | `Que por\ufeffra!` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| P20 | `Que \uff4d\uff45\uff52\uff44\uff41!` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| P21 | `Seu \U0001d41b\U0001d41a\U0001d41b\U0001d41a\U0001d41c\U0001d41a!` | positivo | XINGAMENTO | XINGAMENTO | TP | PENDENTE / PENDENTE |
| P22 | `Que m\u0435rda!` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| P23 | `Seu b\u0430b\u0430c\u0430!` | positivo | XINGAMENTO | XINGAMENTO | TP | PENDENTE / PENDENTE |
| P24 | `Seu B.4.B.4.C.4!` | positivo | ∅ | XINGAMENTO | TP | PUBLICADO / PENDENTE |
| P25 | `Que M\u200b3 R D A!` | positivo | ∅ | PALAVRAO | TP | PUBLICADO / PENDENTE |
| P26 | `Vai.se.foder!` | positivo | XINGAMENTO | XINGAMENTO | TP | PENDENTE / PENDENTE |
| P27 | `Vou te matar.` | positivo | AMEACA | AMEACA | TP | PENDENTE / PENDENTE |
| P28 | `V0u te m4t4r.` | positivo | ∅ | AMEACA | TP | PUBLICADO / PENDENTE |
| P29 | `Que meeeeeeeerda!` | positivo | ∅ | ∅ | FN | PUBLICADO / PUBLICADO |
| P30 | `Que \u1d0derda!` | positivo | ∅ | ∅ | FN | PUBLICADO / PUBLICADO |
| P31 | `Seu imbecil!` | positivo | XINGAMENTO | XINGAMENTO | TP | PENDENTE / PENDENTE |
| P32 | `Que m....e....r....d....a!` | positivo | ∅ | ∅ | FN | PUBLICADO / PUBLICADO |
| P33 | `me\ufe0frda` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| P34 | `me\u034frda` | positivo | PALAVRAO | PALAVRAO | TP | PENDENTE / PENDENTE |
| N01 | `A did\xe1tica foi ruim; n\xe3o recomendo.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N02 | `As provas cobraram assuntos ausentes das aulas.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N03 | `A organiza\xe7\xe3o da disciplina foi p\xe9ssima.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N04 | `Reprovei e discordo dos crit\xe9rios de corre\xe7\xe3o.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N05 | `A an\xe1lise discute a imbecilidade do argumento.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N06 | `O cap\xedtulo descreve a anatomia escrotal.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N07 | `O texto aborda a canalhice como conceito liter\xe1rio.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N08 | `Estudamos a fam\xedlia Otariidae.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N09 | `Tirei 4 na P1 e 3 na P2, com m\xe9dia 3,5.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N10 | `A matriz 4 por 3 tem 12 entradas.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N11 | `Em 2026.2 cursei CIC0004 e MAT0031.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N12 | `Usamos C++, C# e Python 3.12 no laborat\xf3rio.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N13 | `A prova separa os itens a, b, c e d.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N14 | `O algoritmo processa uma fila e uma pilha.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N15 | `Conforme o cap\xedtulo 3, se\xe7\xe3o 4, a hip\xf3tese foi refutada.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N16 | `A fun\xe7\xe3o f(x)=\u03b1x+\u03b2 representa o modelo.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N17 | `A discuss\xe3o cita a\xe7\xe3o, \xf3rg\xe3o e frequ\xeancia.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N18 | `A did\xe1\u200btica precisa melhorar.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N19 | `Usamos a vari\xe1vel prefixo_merda_sufixo no exerc\xedcio de strings.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N20 | `A vari\xe1vel m3rda armazena o resultado da matriz no exemplo.` | negativo | ∅ | PALAVRAO | FP | PUBLICADO / PENDENTE |
| N21 | `No exerc\xedcio, m4rda \xe9 o c\xf3digo de uma c\xe9lula.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N22 | `O material \xe9 insuficiente e as aulas s\xe3o confusas.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N23 | `A bibliografia inclui o artigo intitulado Cr\xedtica da raz\xe3o pura.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| N24 | `A convers\xe3o hexadecimal usa 0x4A e 0x3E.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| C01 | `O texto cita a palavra merda para analisar linguagem.` | contextual | PALAVRAO | PALAVRAO | contextual | PENDENTE / PENDENTE |
| C02 | `N\xe3o chame ningu\xe9m de idiota.` | contextual | OFENSA_PESSOAL | OFENSA_PESSOAL | contextual | PENDENTE / PENDENTE |
| C03 | `O escroto foi descrito no material de anatomia.` | contextual | XINGAMENTO | XINGAMENTO | contextual | PENDENTE / PENDENTE |
| C04 | `Essa prova foi de matar.` | contextual | ∅ | ∅ | contextual | PUBLICADO / PUBLICADO |
| C05 | `O argumento foi idiota ou apenas equivocado?` | contextual | OFENSA_PESSOAL | OFENSA_PESSOAL | contextual | PENDENTE / PENDENTE |
| C06 | `A aula foi um lixo.` | contextual | ∅ | ∅ | contextual | PUBLICADO / PUBLICADO |
| L01 | `Que p0rra de aula!` | positivo | ∅ | PALAVRAO | TP | PUBLICADO / PENDENTE |
| L02 | `P0RR4!` | positivo | ∅ | PALAVRAO | TP | PUBLICADO / PENDENTE |
| L03 | `Que m3rd4!` | positivo | ∅ | PALAVRAO | TP | PUBLICADO / PENDENTE |
| L04 | `Seu b4b4c4!` | positivo | ∅ | XINGAMENTO | TP | PUBLICADO / PENDENTE |
| L05 | `Seu 1d10t4!` | positivo | ∅ | OFENSA_PESSOAL | TP | PUBLICADO / PENDENTE |
| L06 | `Seu 0t4r10!` | positivo | ∅ | XINGAMENTO | TP | PUBLICADO / PENDENTE |
| L07 | `V41 s3 f0d3r!` | positivo | ∅ | XINGAMENTO | TP | PUBLICADO / PENDENTE |
| L08 | `V0u t3 m4t4r!` | positivo | ∅ | AMEACA | TP | PUBLICADO / PENDENTE |
| L09 | `Que c4r4lh0!` | positivo | ∅ | PALAVRAO | TP | PUBLICADO / PENDENTE |
| L10 | `Que c4c3t3!` | positivo | ∅ | PALAVRAO | TP | PUBLICADO / PENDENTE |
| L11 | `P.0.R.R.4!` | positivo | ∅ | PALAVRAO | TP | PUBLICADO / PENDENTE |
| L12 | `M\u200b3 R D 4!` | positivo | ∅ | PALAVRAO | TP | PUBLICADO / PENDENTE |
| LN01 | `A vari\xe1vel p0rra armazena o resultado da matriz.` | negativo | ∅ | PALAVRAO | FP | PUBLICADO / PENDENTE |
| LN02 | `O identificador 1d10ta pertence ao exemplo de programa\xe7\xe3o.` | negativo | ∅ | OFENSA_PESSOAL | FP | PUBLICADO / PENDENTE |
| LN03 | `A vari\xe1vel p0rra_total cont\xe9m a soma.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| LN04 | `O identificador prefixo_m3rda_sufixo est\xe1 no exemplo.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| LN05 | `A matriz 4 por 3 tem 12 entradas.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| LN06 | `Tirei 3,0 na P1 e 4,0 na P2.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| LN07 | `Usamos 0, 1, 3, 4, 5 e 7 no exerc\xedcio.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| LN08 | `Cursei CIC0004 e MAT0031 em 2026.2.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| LN09 | `O c\xf3digo m3rdas identifica a coluna da tabela.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| LN10 | `O identificador c4r4lhometro aparece no exerc\xedcio de strings.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| LN11 | `A did\xe1tica foi ruim e faltou organiza\xe7\xe3o nas avalia\xe7\xf5es.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
| LN12 | `No relat\xf3rio, m4rda identifica a c\xe9lula da matriz.` | negativo | ∅ | ∅ | TN | PUBLICADO / PUBLICADO |
