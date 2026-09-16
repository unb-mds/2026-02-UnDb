# Documento de Visão — G7

> Documento **derivado** de [`docs/requisitos.md`](requisitos.md), fonte de verdade dos
> requisitos do projeto. Se houver divergência, o documento de requisitos prevalece e esta
> visão deve ser atualizada.

## 1. Propósito

Apresentar, de forma sintética, o problema, o público, a proposta de valor, o escopo e os
critérios de sucesso do sistema de Avaliação de Professores e Disciplinas da UnB.

## 2. Contexto e problema

Estudantes da UnB recorrem principalmente a grupos gerais e contatos pessoais para conhecer
professores e disciplinas antes da matrícula. A informação existe, mas circula de forma
informal, desigual e pouco comparável. Alunos sem uma rede consolidada — especialmente os de
2º e 3º semestre, os introvertidos e os que cursam módulo livre em outro departamento —
frequentemente decidem sem base suficiente.

A pesquisa que originou o produto foi composta por conversas abertas com 20 a 30 alunos da
UnB, de diferentes semestres. Ela identificou a necessidade de tornar esse conhecimento
acessível sem depender de contatos pessoais.

## 3. Visão do produto

Para estudantes da UnB que precisam escolher professores e disciplinas, o G7 será uma
aplicação web de consulta pública que consolida avaliações estruturadas e comparáveis. O
produto transforma relatos dispersos em resultados agregados, informa a quantidade de
avaliações que sustenta cada resultado e integra dados institucionais públicos do SIGAA.

O objetivo é permitir uma decisão de matrícula mais fundamentada,
**independentemente de quantas pessoas o estudante conheça no curso**.

## 4. Público e partes interessadas

| Público | Necessidade | Papel no produto |
|---|---|---|
| **Aluno sem rede** | Consultar informação que não consegue obter por contatos pessoais | Principal consumidor |
| **Veterano que já teve experiências relevantes** | Transformar experiência individual em dado útil e comparável | Principal colaborador |
| **Visitante** | Consultar professores, disciplinas e resultados sem criar conta | Consumidor |
| **Estudante autenticado** | Consultar e registrar avaliação estruturada | Consumidor e colaborador |
| **Moderador** | Fazer curadoria de conteúdo textual denunciado | Release 2 |
| **Product Owner e equipe** | Priorizar, desenvolver e validar o produto | Governança e entrega |

## 5. Proposta de valor

| Necessidade identificada | Resposta do produto |
|---|---|
| Informação presa em redes pessoais | Consulta pública, sem cadastro obrigatório |
| Relatos difíceis de comparar | Cinco critérios estruturados e agregados |
| Ausência de contexto sobre a confiabilidade do resultado | Exibição da quantidade de avaliações |
| Poucos dados ou nenhum dado | Estados explícitos de ausência ou insuficiência |
| Escolha entre docentes da mesma disciplina | Comparação lado a lado e ordenação por recomendação |
| Disciplinas fora do curso do aluno | Busca sem restrição por curso ou departamento |
| Risco de avaliações repetidas | Uma avaliação por estudante, professor e disciplina, com substituição |

## 6. Capacidades do produto

### Release 1

- consulta pública de professores, disciplinas e resultados agregados;
- busca por nome de professor, nome ou código de disciplina e entre departamentos;
- comparação entre professores da mesma disciplina;
- cadastro enxuto com e-mail `@aluno.unb.br`, confirmação de endereço e sessão autenticada;
- registro de avaliação estruturada com didática, dificuldade, chamada, material e
  recomendação;
- substituição de avaliação anterior para a mesma combinação de estudante, professor e
  disciplina;
- exibição detalhada somente a partir de três avaliações por professor e disciplina;
- importação periódica de professores, disciplinas e turmas a partir de páginas públicas do
  SIGAA, com registro de sucesso ou falha.

### Release 2

- comentários em texto livre;
- denúncia de conteúdo;
- fila de moderação.

## 7. Limites de escopo da Release 1

Não fazem parte da primeira release:

- avaliação da personalidade do professor;
- comentários em texto livre e a respectiva moderação;
- calouros como público primário;
- verificação de que o estudante cursou a disciplina, pois o histórico individual não está
  disponível publicamente no SIGAA.

O produto não cria nota geral nem índice composto. A ordenação usa exclusivamente o
percentual de recomendação. Dificuldade e chamada são informações neutras e não devem ser
tratadas visualmente como positivas ou negativas.

## 8. Critérios de sucesso

| Métrica | Interpretação |
|---|---|
| **Cobertura** | Percentual de professores com pelo menos N avaliações |
| **Adoção** | Avaliações registradas por semestre |
| **Alcance** | Consultas realizadas por semestre |
| **Amplitude** | Percentual de consultas a disciplinas fora do curso do aluno |

Cobertura é a métrica mais crítica, pois o produto depende de volume suficiente de dados. O
valor de N ainda será definido após o primeiro semestre de uso; ele não deve ser confundido
com o mínimo de três avaliações já definido para exibição detalhada.

## 9. Restrições, hipóteses e riscos

### Decisões vigentes

- consulta pública e avaliação restrita a conta com e-mail confirmado;
- mínimo inicial de três avaliações para exibir critérios agregados;
- ausência de matrícula, CPF e histórico acadêmico no cadastro;
- ausência de texto livre na Release 1;
- agregação e desempates conforme as regras registradas em `docs/requisitos.md`.

### Hipótese não validada

Didática e taxa de reprovação foram citadas na pesquisa, mas não há evidência de que sejam os
fatores decisivos de escolha nem medição do peso relativo entre fatores.

### Riscos e decisões pendentes

- alcançar massa crítica de avaliações suficiente para gerar valor;
- definir o provedor de e-mail e a validade do link de confirmação;
- resolver identidade de docentes, homônimos, múltiplos docentes e reimportação;
- comprovar e operacionalizar a cobertura da coleta em todas as unidades do SIGAA;
- definir a estratégia de execução e deploy do frontend;
- validar os requisitos não-funcionais ainda propostos, exceto o RNF02 já validado.

## 10. Releases

| Release | Data planejada | Foco |
|---|---|---|
| **Release 1** | 28/09/2026 | Consulta, comparação, avaliação estruturada e dados do SIGAA |
| **Release 2** | 25/11/2026 | Comentários, denúncia e moderação |

## 11. Artefatos relacionados

- [Engenharia de requisitos](requisitos.md) — fonte de verdade do escopo e das regras de
  produto;
- [Board de requisitos no Figma](https://www.figma.com/board/qs0bvgeJXyfCxYFEDSX9VH/G7---Requisitos--Avalia%C3%A7%C3%A3O-de-Professores-UnB-) — pesquisa, personas, Double Diamond, priorização, story map e fluxos;
- [Especificação de implementação](https://github.com/unb-mds/2026-02-UnDb/blob/develop/specs.md) — tradução dos requisitos para regras de
  implementação;
- [Arquitetura](arquitetura.md) — decisões e estrutura técnica;
- [Board de desenvolvimento](https://github.com/orgs/unb-mds/projects/60) — acompanhamento
  das entregas.
