# Home, busca e unidades — #203

Base: `72227cc`, `origin/develop`, com a #202 integrada pelo PR #208. Referências: critérios da [#203](https://github.com/unb-mds/2026-02-UnDb/issues/203), [guia de integração](../../docs/referencias/ui-dark/issues/203.md), [contrato da base](ui-dark.md), RF04–RF07 e continuidade da busca da #155 em `docs/requisitos.md`.

## Contratos para a #204

`DisciplinasProfessor` permanece um componente de apresentação sem efeitos nem consultas. Recebe `professorId: string`, `disciplinas: DisciplinaDetalhe[]` e `contexto?: ContextoBusca | null` (padrão `null`). A lista vazia mantém a mensagem sobre ausência de turma ativa. Cada disciplina preserva seu ID, código e unidade, com links para consulta do par professor/disciplina, avaliação direta e comparação. As rotas e os parâmetros autorizados de contexto são os mesmos da #155.

O componente é usado nos resultados e no perfil. A #204 pode continuar fornecendo as mesmas props, sem adaptar serviços. Não agrupar docentes pelo nome. `ProfessorResultado` é montado por `professor.id`, carrega as disciplinas desse ID e permite nova tentativa se essa leitura falhar. Os resultados de professor ocupam uma coluna; os de disciplina usam uma, duas ou três conforme a largura.

`DisciplinaCatalogo` compartilha a apresentação de disciplinas entre home, unidades e busca. Recebe a disciplina, contexto opcional e `titulo?: "h2" | "h3"`. Na home usa `h3`, abaixo do título da seção. Não consulta agregados nem mostra notas ou contagens de avaliações.

## Dados e navegação

- A home mantém o formulário GET compartilhado da #202, incluindo envio antes da hidratação. `/busca` redireciona para a listagem com termo, modalidade e ordem. A edição na listagem mantém debounce, descarte de respostas obsoletas e ordenação local sem HTTP adicional.
- Home e `/departamentos` consultam `listarDisciplinas()` por meio de `useCatalogo`. A leitura ocorre no cliente para permitir nova tentativa no mesmo local; o formulário e a composição da home continuam renderizados no servidor. Não há nova infraestrutura, cache compartilhado ou dependência.
- As unidades são os nomes exatos retornados no campo `departamento` das disciplinas, sem inventar siglas, entidades ou estatísticas. Esta API não oferece endpoint de unidades separado. A home mostra até seis disciplinas em ordem alfabética e até oito unidades; a página de unidades contém o catálogo completo.
- `/departamentos?unidade=...` filtra por nome exato na URL, sem consulta adicional. Uma unidade desconhecida tem mensagem própria e link para todas. Os cartões do catálogo abrem a comparação oficial; o histórico do navegador conserva o filtro de origem. O contexto `busca/q/ordem` continua restrito às buscas de professor e disciplina, sem ampliar `returnTo`.
- Catálogo em carregamento, vazio e erro são estados distintos; vazio e erro oferecem nova tentativa. A pesquisa de menos de duas letras mantém a orientação existente. Nenhum dado demonstrativo ou fonte de `/prototipo` é usado no produto.

## Verificação

Os cenários da #203 foram incorporados a `tests/busca.test.mjs` e `tests/busca-browser.mjs`, que já integram os runners do projeto. Os testes de navegador usam HTTP controlado, com dados explicitamente sintéticos, sem mutações no banco do usuário. Evidências e limitações da execução ficam em `verificacao-ui-busca-203.md`.
