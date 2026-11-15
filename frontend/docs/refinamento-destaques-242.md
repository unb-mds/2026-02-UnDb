# Refinamento dos destaques — Issue #242

Fonte: [Issue #242](https://github.com/unb-mds/2026-02-UnDb/issues/242), feedback do PO de 14/11/2026. Base inicial das capturas: `develop`, commit `edd4a7beb22fbde74df34fa22f44f35e57ddf642`.

## Comparação definida antes da alteração

- **Mantido:** grade estável de uma/duas/três colunas, até seis disciplinas dos serviços existentes, código, nome, contagem, até dois resumos por professor, mensagem de insuficiência, busca e destinos de comparação. A implementação já tinha contagens pequenas; não havia necessidade de acrescentar números ou rankings.
- **Reduzido:** tipografia dos títulos (20 para 18 px), espaçamento e altura decorativa. Mobile usa padding de 16 px e gap de 12 px; a partir de `sm`, padding de 20 px. Nomes podem ocupar todas as linhas necessárias, inclusive palavras longas.
- **Removido da seção:** topo decorativo com gradientes azul/verde e altura mínima de 128 px, recorte com seta circular e deslocamento vertical no hover. O título passa de “Explore as disciplinas” para “Disciplinas mais avaliadas”; o texto explica que quantidade não indica qualidade. Catálogo e busca existentes permanecem; a proposta rejeitada de cartões coloridos em caixa alta não foi implementada.

Reutilizados `.panel`, `.code-chip`, `.section-title`, `.link`, foco global e tokens atuais. Nenhuma alteração em `globals.css`, rota da home, catálogo, serviços, contratos, permissões ou regras de avaliação/privacidade. Dados sintéticos ficam exclusivamente na fixture do teste; o produto continua consultando `/api/disciplinas/destaques` e a comparação por disciplina, sem fallback de demonstração.

## Referências e coordenação

O Figma fornecido não pôde ser consultado: a tentativa de abrir o [arquivo de design](https://www.figma.com/design/5ydNmYipNHOVfG1oME5j7l/UnDb---Design-atual?node-id=11-2) retornou recurso inacessível. Não se afirma fidelidade ao seu conteúdo. A comparação usa a implementação vigente, `ui-dark.md` e a descrição da issue; alinhamento visual final depende de revisão humana.

Antes das alterações, o conector GitHub confirmou #233 fechado/integrado e encontrou #243 aberto para #237. As buscas por PRs abertos relacionados a #204, #205 e #206 não retornaram resultados. A mudança ficou em `DestaquesHome`, sem editar componentes compartilhados ou CSS global. Durante a execução, `develop` avançou para `d59e48b`, integrando #243 e #244. Os commits locais ainda não publicados foram reaplicados sobre essa base; o único conflito foi o script `test:browser`, resolvido preservando o runner da #237 e acrescentando o da #242. A seção de destaques da base permaneceu igual à versão usada nas capturas anteriores.

## Evidências de navegador

Edge headless/CDP e Node Windows 24.14.1 existentes, sem instalação de dependências. Build da versão-base gerado antes da mudança e usado nas capturas “antes”. As capturas definitivas foram refeitas sobre a apresentação original para retirar a sobreposição do cabeçalho fixo identificada na primeira inspeção. Build do refinamento usado no “depois”.

Mesma fixture HTTP nos dois lados, com seis disciplinas, título longo, contagens singular/plural e professores com dados suficientes/insuficientes. São dados sintéticos explícitos de teste, não dados do Figma ou de produção. Viewports emulados de 320, 768 e 1280 px, altura 900 px e escala 1. Capturas recortadas para toda a seção, aguardando fontes; preferência de movimento reduzido. As preferências clara/escura do sistema foram verificadas, mantendo o tema dark fixo do produto.

| Largura | Antes | Depois |
| --- | --- | --- |
| 320 px | [Captura](capturas/issue-242/antes/destaques-320.png) | [Captura](capturas/issue-242/depois/destaques-320.png) |
| 768 px | [Captura](capturas/issue-242/antes/destaques-768.png) | [Captura](capturas/issue-242/depois/destaques-768.png) |
| 1280 px | [Captura](capturas/issue-242/antes/destaques-1280.png) | [Captura](capturas/issue-242/depois/destaques-1280.png) |

O teste verifica preservação de nomes/códigos/contagens/resumos e destinos, títulos sem corte, colunas esperadas, ausência de overflow horizontal na página/cartões, Tab, foco visível, Enter até o destino e ausência da seção com resposta vazia/erro. A inspeção estática confirma a manutenção dos mesmos serviços e da condição `dadosSuficientes`; não foi executada integração nova com API/PostgreSQL reais nem teste em aparelhos físicos.

[Medições estruturadas dos seis cenários por versão](capturas/issue-242/medidas.json). A altura da grade passou de 2302 para 1657,81 px em 320 px, de 1194 para 918,03 px em 768 px e de 799 para 590,19 px em 1280 px, com a mesma fixture. Essas alturas não são limites fixos da implementação.

Para reproduzir o cenário isolado, após `npm run build`, use Node 22+ e configure `BROWSER_PATH` se o Edge não estiver no caminho padrão do projeto:

```sh
node tests/destaques-home-browser.mjs
```

Nesta execução, a captura final usa `PREVIEW_DIR=docs/capturas/issue-242/depois` propagado ao processo Windows via `WSLENV=PREVIEW_DIR`. O caminho absoluto do executável foi `/mnt/e/Program Files/nodejs/node.exe`. A opção de saída grava somente capturas, sem credenciais.

## Contraste calculado

Fórmula de luminância relativa sRGB, tokens hex opacos atuais, em `tests/paleta.test.mjs`. São pares efetivamente usados na seção; os cálculos não estabelecem conformidade WCAG da aplicação inteira.

| Par | Razão |
| --- | --- |
| foreground / panel | 17,60:1 |
| ink-soft / panel | 11,91:1 |
| muted / panel | 7,05:1 |
| accent / panel | 8,88:1 |
| accent / accent-soft (código) | 5,88:1 |
| ink-soft / background (texto introdutório) | 13,23:1 |
| focus / background (offset do cartão) | 14,96:1 |

Todos os pares de texto acima atingem 4,5:1 e o indicador de foco atinge 3:1. Não se usa a borda decorativa do painel como único indicador de interação: o cartão contém chamada textual azul e foco global com offset.

## Verificações

Node Linux 24.14.1 e dependências já instaladas; nenhuma dependência nova ou alteração no lockfile. O CI usa Node 22; a diferença de runtime permanece explícita.

| Comando, em `frontend/` | Resultado observado |
| --- | --- |
| `npm run lint` | Sem erros/avisos |
| `npm run typecheck` | Tipos de rota e TypeScript aprovados |
| `npm run test:coverage` | 78 testes, 78 passaram, zero falhas |
| `npm run build` | Build de produção aprovado |
| `node.exe tests/destaques-home-browser.mjs` | Aprovado nas duas versões, 320/768/1280 px e preferências clara/escura, Tab/foco/Enter e estados vazio/erro |
| `git diff --check` | Sem erros |

Cobertura de linhas/statements: 18,81%; branches: 75,31%; funções: 49,12%. A cobertura global não equivale à cobertura completa da interface.

O npm Windows não conseguiu executar `npm run test:browser` no caminho UNC do WSL. Uma primeira execução dos runners em sequência foi interrompida com código 143 após os cenários de comentários; isso não foi contabilizado como aprovação da suíte completa. Os runners desse script são executáveis diretamente com o Node Windows e o Edge existentes; o resultado completo é registrado no PR. Na base final, avaliação/busca/catálogo, moderação e denúncia passaram. O runner de comentários falhou duas vezes em `document.body.innerText` durante navegação (body ausente). A espera foi tornada tolerante à ausência transitória de body, preservando as condições funcionais; a reexecução passou. Revisão humana e CI remoto precisam ser conferidos antes do merge; a contribuição usa `Refs #242` para preservar o aceite humano.


### Resultado final dos runners

Sobre `develop` em `d59e48b`, foram executados individualmente com Node Windows/Edge os nove runners do script atual `test:browser`: `avaliacao`, `moderacao`, `denuncia`, `comentarios`, `cabecalho`, `identidades`, `transicao`, `conta-avaliacao-sessao` e `destaques-home`. Todos terminaram com código 0 na validação final. O teste específico de destaques foi repetido sobre a base integrada e passou; as capturas anteriores continuam representando a mesma apresentação da seção.

Revisão estática do diff da #242 concluída sem findings confirmados. O ajuste de uma espera no teste de comentários não altera o produto nem remove asserções. A revisão técnica não substitui aprovação humana.
