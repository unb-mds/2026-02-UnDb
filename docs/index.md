# UnDb

## Informação para escolher melhor

O **UnDb** é uma aplicação web para consulta e avaliação de professores e disciplinas
da Universidade de Brasília. O projeto transforma relatos dispersos em resultados
estruturados e comparáveis, com dados institucionais provenientes de páginas públicas do
SIGAA.

<div class="grid cards" markdown>

-   :material-target:{ .lg .middle } **Visão do produto**

    ---

    Entenda o problema, o público, a proposta de valor, os limites e as releases.

    [:octicons-arrow-right-24: Ler a visão](visao.md)

-   :material-clipboard-check-outline:{ .lg .middle } **Requisitos**

    ---

    Consulte os requisitos funcionais e não funcionais, suas regras e rastreabilidade.

    [:octicons-arrow-right-24: Explorar requisitos](requisitos.md)

-   :material-sitemap-outline:{ .lg .middle } **Arquitetura**

    ---

    Veja componentes, camadas, modelo de dados, fluxos, ADRs e riscos técnicos.

    [:octicons-arrow-right-24: Ver arquitetura](arquitetura.md)

-   :material-vector-square:{ .lg .middle } **Board no Figma**

    ---

    Navegue pela pesquisa, personas, priorização, story map e fluxos do produto.

    [:octicons-arrow-right-24: Abrir o board](figma.md)

</div>

## Escopo das entregas

| Release | Data planejada | Foco |
|---|---|---|
| **Release 1** | 28/09/2026 | Consulta, comparação, avaliação estruturada e dados do SIGAA |
| **Release 2** | 25/11/2026 | Comentários, denúncia e moderação |

A [Release 1.0.0](releases/1.0.0.md) usa importação manual dos dados do SIGAA.
A atualização periódica está prevista para a Release 2.

A [v1.1.0](releases/1.1.0.md) foi publicada em 09/11/2026 e a aplicação está em
[undb.app.br](https://undb.app.br). Consulte o [guia de hospedagem](hospedagem.md),
o [resultado da carga manual no Neon](estudos/importacao-neon-2026-11-10.md) e a
[reconciliação da R2](releases/2.0.0-reconciliacao.md) para distinguir essa versão
das entregas posteriores de `develop` e dos aceites pendentes.

!!! info "Fonte de verdade"

    [`docs/requisitos.md`](requisitos.md) é a fonte de verdade dos requisitos. Esta página
    apenas organiza o acesso aos artefatos existentes e não redefine o escopo do produto.


### Próxima promoção intermediária

A [candidata 1.3.0](releases/1.3.0.md) reúne a reconciliação e associação institucional
de professores, fila de identidades e cabeçalho conforme a sessão, após a
[v1.2.0 publicada](releases/1.2.0.md). A conclusão da Release 2 acadêmica e a
reconciliação dos dados públicos permanecem separadas desta promoção de código.
