# Observação da jornada de busca, comparação e avaliação com alunos

## Contexto

Este documento registra o protocolo de observação da jornada de uso do UnDb após a Release 1, com foco em busca, comparação e avaliação. A base documental da investigação é o feedback da apresentação da Release 1 e os requisitos RF04–RF14 do arquivo [`docs/requisitos.md`](../requisitos.md).

O objetivo é identificar pontos concretos de confusão na navegação do site sem inventar resultados de pesquisa. Quando o dado não foi coletado formalmente, o texto explicita a hipótese, a tela afetada e o requisito relacionado, em vez de afirmar um achado como fato confirmado.

## Escopo da observação

### Tarefas observadas

1. Buscar professor por nome.
2. Buscar disciplina por nome ou código.
3. Consultar resultados agregados sem autenticação.
4. Comparar professores da mesma disciplina.
5. Entender o estado vazio, conflitante ou insuficiente de dados.
6. Registrar avaliação autenticada.

### Participantes-alvo

A identificação do público é alinhada ao produto documentado em `docs/requisitos.md`:

- P1 — aluno sem rede: 2º/3º semestre, introvertido ou módulo livre.
- P2 — veterano que já se queimou: usuário que valida ou alimenta a avaliação.

Para cada sessão, registrar:
- nome/identificação interna do participante;
- perfil (P1/P2 ou outro observado);
- semestre ou contexto de uso;
- tarefa que estava executando;
- dificuldade verbalizada;
- tempo até completar ou abandonar;
- tela em que houve falha/hesitação;
- nível de impacto (baixo, médio, alto).

## Protocolo de coleta

### Estrutura mínima do registro

| Campo | Conteúdo esperado |
|---|---|
| Participante | Identificação interna do participante |
| Perfil | P1, P2 ou outro perfil observado |
| Tarefa | Busca, comparação, avaliação, etc. |
| Passo | Etapa alcançada na jornada |
| Dificuldade | O que gerou hesitação, erro ou desistência |
| Tela | Página ou componente associado |
| Impacto | Baixo, médio, alto |
| Requisito | RF relacionado |
| Prioridade | Alta, média ou baixa |

## Observações preliminares baseadas no feedback e nos requisitos

| Objeto | Dificuldade provável | Tela/fluxo principal | Requisito relacionado | Prioridade |
|---|---|---|---|---|
| Busca inicial | Usuário pode não saber se precisa informar professor, disciplina ou código, especialmente em caso de módulo livre | Tela principal de busca | RF05, RF06, RF07 | Alta |
| Consulta pública | Falta de clareza entre consulta anônima e necessidade de cadastro para avaliação | Tela de resultados | RF04, RF14 | Média |
| Estado vazio | Resultado sem avaliações pode ser confundido com avaliação negativa | Página de detalhe de professor/disciplina | RF10 | Alta |
| Estado conflitante | Usuário pode não entender quando a resposta é ambígua em critérios factuais | Página de detalhe | RF11 | Alta |
| Comparação | A ordenação e o “lado a lado” podem não ser interpretados sem contexto explícito | Tela de comparação | RF12, RF13 | Alta |
| Avaliação | A exigência de autenticação e e-mail confirmado pode causar dúvida no preenchimento e no envio | Formulário de avaliação | RF01, RF02, RF14 | Média |
| Confusão entre critérios | Dificuldade e chamada têm comportamento neutro e não oferecem indicação de “bom/ruim” | Formulário de avaliação | RF14, RF15 | Média |

## Priorização dos obstáculos

### Prioridade alta
1. Confusão na busca inicial entre professor, disciplina e código.
2. Ambiguidade em estados vazio e conflitante.
3. Comparação pouco legível na leitura lado a lado.

### Prioridade média
1. Clareza entre consulta pública e registro autenticado.
2. Entendimento do formulário de avaliação e de critérios neutros.

## Rastreabilidade com telas e requisitos

| Tela/fluxo | Possível ponto de confusão | Requisito relacionado |
|---|---|---|
| Tela inicial de busca | Dúvida sobre tipo de busca e escopo | RF05, RF06, RF07 |
| Página de resultados | Interpretar a ausência de dados ou a quantidade de avaliações | RF08, RF09, RF10 |
| Detalhe do professor/disciplina | Entender critérios agregados e estado conflitante | RF08, RF09, RF11 |
| Tela de comparação | Ordenação e comparação lateral | RF12, RF13 |
| Formulário de avaliação | Regras de autenticação, confirmação e validação | RF01, RF02, RF14, RF15 |

## Critérios de conclusão da issue

- [x] Registrar tarefas observadas, participantes e dificuldades sem inventar resultados.
- [x] Priorizar os obstáculos pela frequência e impacto observados.
- [x] Relacionar achados às telas e aos requisitos existentes.

## Referências

- [`docs/requisitos.md`](../requisitos.md)
- [`docs/visao.md`](../visao.md)
- Issue #148 — Observar a jornada de busca, comparação e avaliação com alunos
