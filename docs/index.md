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

## Plataforma e versão atual

Use o [UnDb](https://undb.app.br) para buscar professores e disciplinas, consultar
os cinco critérios e contribuir com sua experiência. A [página Sobre](https://undb.app.br/sobre)
apresenta a equipe e suas redes.

A [1.4.0](releases/1.4.0.md) reúne a revisão visual integrada pela PR #230,
com destaques por quantidade de avaliações, comparação por cartões e perfis completos.
As notas distinguem a candidata da publicação final no GitHub. O histórico anterior
inclui [1.3.0](releases/1.3.0.md) e [1.3.1](releases/1.3.1.md).

## Desenvolver, validar e operar

| Objetivo | Guia |
|---|---|
| Instalar e configurar | [Desenvolvimento local](desenvolvimento.md) |
| Executar verificações | [Qualidade](qualidade.md) |
| Publicar e acompanhar serviços | [Hospedagem](hospedagem.md) |
| Atualizar dados institucionais | [Operação do SIGAA](operacao-importacao-sigaa.md) |
| Revisar identidades docentes | [Identidades](identidades-docentes.md) |

## Planejamento e evidências

O planejamento original separa consulta e avaliação estruturada (R1) de comentários,
denúncia e moderação (R2). As versões intermediárias do código não substituem os
aceites desses marcos. Consulte a [visão](visao.md) e a
[reconciliação da R2](releases/2.0.0-reconciliacao.md) para pendências e evidências.

!!! info "Fonte de verdade"

    [Requisitos](requisitos.md) mantém as regras do produto. Esta página organiza
    o acesso à documentação; estudos preservam a data e o contexto das verificações.
