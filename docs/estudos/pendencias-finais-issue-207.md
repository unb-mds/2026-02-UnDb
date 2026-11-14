# Investigação das 41 ocorrências — issue #207

Consulta pública realizada em 13/11/2026. Nenhuma alteração em código ou banco de produção.

## Conclusão

40 ocorrências foram reencontradas nas ofertas públicas de graduação de 2026.2, com nome completo, unidade, disciplina e turma esperados. Uma ocorrência (Li Chong Lee, ENC0147) não reapareceu na consulta atual. A lista de turmas comprova atribuição nominal, mas não fornece por si só um identificador institucional único.

## Múltiplos perfis

| Nome | Identificadores | Comparação | Recomendação |
|---|---|---|---|
| JULIANA ALBUQUERQUE BALTAR | [1902506](https://sigaa.unb.br/sigaa/public/docente/portal.jsf?siape=1902506) e [2902506](https://sigaa.unb.br/sigaa/public/docente/portal.jsf?siape=2902506) | Mesmo e-mail público, nome, unidade e histórico (113 linhas em cada perfil) | Tratar como mesma pessoa por decisão revisada; causa cadastral ou múltiplos vínculos não determinada |
| JULIANA ARAIS HOCEVAR KRISTOSCHEK | [1489153](https://sigaa.unb.br/sigaa/public/docente/portal.jsf?siape=1489153) e [2489153](https://sigaa.unb.br/sigaa/public/docente/portal.jsf?siape=2489153) | Mesmo e-mail público, nome, unidade e histórico (68 linhas em cada perfil) | Tratar como mesma pessoa por decisão revisada; causa cadastral ou múltiplos vínculos não determinada |
| WANDEMBERG VENCESLAU ROSENDO DOS SANTOS | [1375765](https://sigaa.unb.br/sigaa/public/docente/portal.jsf?siape=1375765) e [2375765](https://sigaa.unb.br/sigaa/public/docente/portal.jsf?siape=2375765) | Mesmo e-mail público, nome, unidade e histórico (10 linhas em cada perfil) | Tratar como mesma pessoa por decisão revisada; causa cadastral ou múltiplos vínculos não determinada |

## Casos por unidade

| Nome | Unidade | Ocorrências | Evidência atual | Recomendação |
|---|---|---:|---|---|
| LUCIANA RESENDE BORGES | 314 | 3 | CET0042 / turma 01, CET0050 / turma 01, CET0053 / turma 01 | Associação local provisória por nome completo + unidade; não inventar confirmação institucional da disciplina |
| BRENO NORONHA MATOS | 678 | 1 | FAR0176 / turma 03A | Associação local provisória por nome completo + unidade; não inventar confirmação institucional da disciplina |
| JOEL ANTONIO CORDEIRO DE ABREU | 678 | 2 | FAR0003 / turma 02, FAR0007 / turma 02 | Associação local provisória por nome completo + unidade; não inventar confirmação institucional da disciplina |
| JUAREZ OLIVEIRA SAMPAIO | 393 | 5 | FEF0462 / turma 01, FEF0468 / turma 01, FEF0468 / turma 02, FEF0476 / turma 02, FEF0495 / turma 01 | Associação local provisória por nome completo + unidade; não inventar confirmação institucional da disciplina |
| KARLA DIAS LOPES CAETANO | 666 | 2 | FUP0154 / turma 02, FUP0417 / turma 01 | Associação local provisória por nome completo + unidade; não inventar confirmação institucional da disciplina |
| LI CHONG LEE BACELAR DE CASTRO | 437 | 1 | Não reencontrada na oferta atual; perfil contém ENC0147 em 2026.1 e 2027.1 | Associação local provisória por nome + unidade é opção com risco residual; não marcar ENC0147/2026.2 como confirmada pelo perfil |
| LUANA DIAS DA COSTA | 420 | 1 | DSC0056 / turma 01 | Associação local provisória por nome completo + unidade; não inventar confirmação institucional da disciplina |
| LUANA DIAS DA COSTA | 672 | 1 | FCE0280 / turma 02 | Associação local provisória por nome completo + unidade; não inventar confirmação institucional da disciplina |
| RENATA QUEIROZ DUTRA | 370 | 1 | FDD0244 / turma 04 | Associação local provisória por nome completo + unidade; não inventar confirmação institucional da disciplina |
| WESLY JEAN | 327 | 1 | ADM0273 / turma 54 | Associação local provisória por nome completo + unidade; não inventar confirmação institucional da disciplina |

## Regra mínima recomendada

1. Reutilizar associações institucionais já confirmadas.
2. Permitir decisão revisada de equivalência nos três pares acima, preservando a evidência de ambos os perfis.
3. Para histórico ausente/incompleto, usar associação local provisória por nome completo normalizado + unidade, sem declarar a disciplina institucionalmente confirmada.
4. Não unir unidades diferentes apenas pelo nome. Luana fica com associações locais distintas nas unidades 420 e 672, salvo confirmação institucional específica.
5. Preservar separações humanas, conflitos de identidades já confirmadas e avaliações conflitantes; não descartar avaliações.

## Fontes complementares

- Luciana: convocação do CET em 17/08/2026: https://www.concursos.unb.br/index.php/editais-temporario/temporario-2026/2371-edital-de-abertura-n-045-2026
- Joel: convocação em 21/09/2026: https://concursos.unb.br/index.php/editais-temporario/temporario-2025/2364-edital-de-abertura-n-223-2025
- Breno: convocação em 17/08/2026: https://www.concursos.unb.br/index.php/editais-temporario/temporario-2026/2372-edital-de-abertura-n-046-2027
- Oferta pública (requisição JSF com sessão, graduação, ano 2026, período 2): https://sigaa.unb.br/sigaa/public/turmas/listar.jsf?aba=p-ensino

## Decisão autorizada

Nicolas autorizou aplicar o tratamento após conferir os exemplos e aceitar o risco
residual da associação por nome completo e unidade. A implementação mantém essa
associação como local, preserva os candidatos revisados e volta à fila quando
uma nova ocorrência traz um conjunto de perfis diferente. Não atribui a causa
dos perfis repetidos a erro da UnB sem comprovação.

Limitação: uma oferta ausente na consulta atual não prova que nunca existiu.
Ausência no histórico não prova pessoa diferente. Nenhuma oferta histórica deve
ser apagada como consequência desta investigação.

## Verificação da implementação

- Suíte local Python 3.12: 255 testes, sucesso, 2 ignorados por condição de ambiente.
- Contratos de identidade, reavaliação e reconciliação em PostgreSQL 18 isolado:
  64 testes aprovados, incluindo novo semestre, conjunto de perfis alterado,
  unidades diferentes, colisão de avaliações e repetição da aplicação.
- Ruff: análise e formatação aprovadas para todo o backend.
- Ensaio numa nova restauração local do backup anterior à manutenção: aplicar os
  52 grupos institucionais já confirmados, consolidar grupos locais e incluir os
  revisados terminou com **8.277 ocorrências APLICADA e zero PENDENTE**. As
  **17 avaliações** mantiveram todos os campos, exceto a referência ao professor
  consolidado quando necessária. Repetir a aplicação não encontrou grupos.
- O ensaio foi local, sem escrita em produção. O tempo local não estima a duração
  no Neon. Os dados de produção ainda precisam de aplicação e conferência após
  integrar/publicar a alteração.
- A suíte completa na imagem Docker antiga apresenta uma falha já reproduzida na
  versão anterior: o teste de conexão SQLite com `%` no caminho, dependente das
  versões instaladas na imagem. O mesmo teste passa no ambiente Python 3.12 local.
- O texto da fila foi ajustado para distinguir múltiplos perfis de pessoas
  homônimas. Lint/tipos do frontend ficam para o CI; Node/npm não estão no PATH
  deste ambiente.
