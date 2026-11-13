# Reavaliação seletiva de identidades — #207

Em 13/11/2026, diagnóstico dos 70 nomes das 193 ocorrências inconclusivas na
cópia restaurada do backup de 12/11, após ensaiar a consolidação geral.
Nenhuma conexão ou escrita em produção foi realizada nesta etapa.

A primeira verificação de perfis (com retentativa nos casos sem sucesso)
resultou em 63 nomes consultáveis, seis sem perfil e um sem linhas verificáveis
na aba graduação. Essa verificação sozinha não comprova identidade por oferta.

A prévia do novo comando recuperou as 193 ofertas correspondentes sem lacunas.
Consultando novamente a fonte e exigindo período/código/ID de componente exatos:

| Motivo | Ocorrências |
|---|---:|
| Compatível | 175 |
| Perfil ausente | 12 |
| Disciplina não confirmada | 3 |
| Consulta inconclusiva | 3 |

A prévia não alterou a fila local. O ensaio seguinte aplicou somente à cópia
local os resultados recém-obtidos: 62 associações aplicadas, 113 confirmadas e
18 ainda pendentes. Comparação de hashes das linhas de avaliações e dos vínculos
turma-professor permaneceu idêntica após essa reavaliação.

O ensaio da manutenção administrativa subsequente consolidou 51 grupos sem
bloqueios. Resultado local: 7.849 aplicadas, 428 pendentes e duas avaliações.
Essa simulação reaproveitou as evidências da prévia em memória; a CLI real com
`--aplicar` faz novas consultas públicas, portanto seus resultados podem variar.

Biofísica CEL0023 ficou com três cadastros distintos: Antonio Francisco Pereira
de Araujo com duas turmas, Joao Alexandre Ribeiro Goncalves Barbosa com duas e
Werner Leopoldo Treptow com uma, todas de 2026.2. Os dois primeiros tinham suas
ocorrências em `CONSULTA_INCONCLUSIVA`, coerente com a captura de produção.

Validação: 40 testes direcionados, 39 aprovados e um dependente de PostgreSQL
ignorado; Ruff check/format e diff check. O ensaio real em PostgreSQL local
complementa os testes, sem comprovar publicação ou aplicação em produção.

Próximas etapas: revisão/publicação da CLI, prévia em produção com o papel do
importador e reavaliação explícita; se houver UUIDs a unir, novo backup e janela
de manutenção. As outras categorias originais da fila não entram nesta seleção.

## Investigação das demais categorias

Análise posterior na mesma cópia local: 428 ocorrências restantes, sendo 387
por perfil ausente (258 nomes), 23 por múltiplos perfis (três nomes), 15 por
componente/semestre não confirmado (oito nomes) e três inconclusivas (um nome).
Essa distribuição é uma projeção do ensaio, não nova leitura de produção.

Foram consultados todos os oito nomes com disciplina não confirmada. Os perfis
foram lidos, mas os códigos esperados não aparecem no semestre exato. Exemplos:
Breno Noronha Matos tem FAR0176 em 2020.2; Li Chong Lee Bacelar de Castro tem
ENC0147 em 2026.1/2027.1, não em 2026.2; os demais possuem ausência do código ou
histórico sem 2026.2. Não converter outra edição do componente em evidência para
o semestre solicitado. Não foi demonstrado novo defeito do parser nesses casos.

Os três nomes classificados como HOMONIMOS possuem dois perfis cada:

- Juliana Albuquerque Baltar: 2902506 e 1902506, 113 linhas em cada histórico.
- Juliana Arais Hocevar Kristoschek: 2489153 e 1489153, 68 linhas em cada histórico.
- Wandemberg Venceslau Rosendo dos Santos: 2375765 e 1375765, dez linhas em cada.

As listas extraídas de disciplinas de cada par são idênticas. Isso é indício de
múltiplos vínculos/perfis institucionais para a mesma pessoa, não prova de pessoas
homônimas distintas nem autorização para escolher o identificador menor/maior.
A regra vigente permanece conservadora. Um caso sofreu redirecionamento e
funcionou na repetição. Qualquer política de alias institucional exige decisão
explícita e rastreabilidade; não foi implementada nesta investigação.

Luciana Resende Borges (3552906) tem página e aba de graduação válidas, sem linhas:
a fonte exibe explicitamente “Nenhuma turma encontrada”. Não é evidência de falha
de rede nem confirma CET0053/CET0042/CET0050 de 2026.2. O rótulo genérico atual
CONSULTA_INCONCLUSIVA agrupa essa falta de histórico com erros técnicos; melhorar
a distinção é recomendável, preservando a pendência e sem assumir histórico vazio.

Para perfis ausentes, amostra de 22 dos 258 nomes, correspondendo a 81 ocorrências:
os 15 com mais ocorrências e sete adicionais por grafia/acentos e diversidade.
A busca integral não apresentou nome exato normalizado. Buscas pelos dois primeiros
nomes não recuperaram correspondência exata nos casos completados. Exemplos:
ANA CLARA devolve três pessoas com sobrenomes diferentes; ANDRE RIBEIRO encontra
Joao Alexandre Ribeiro Goncalves Barbosa, que não é nome equivalente. Não associar
por substring ou semelhança. Diego Andres Barrios Diaz teve zero resultados na
busca integral e redirecionamento na busca curta; esta última ficou inconclusiva.
A amostra não comprova ausência de todos os outros 236 nomes e não estabelece
se alguém é substituto, aposentado, visitante ou mudou de nome.

A análise é somente leitura pública + backup local; nada foi alterado em produção.
Não é necessário eliminar toda pendência para publicar uma correção: permanecem
sem confirmação os casos que as fontes públicas não permitem decidir.
