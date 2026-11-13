# Refinamento visual do frontend — #211

Data: 12/11/2026. Branch: `feature/211-refinamento-design`, a partir de `origin/develop` (`baa8fe5`), com #202–#206 e #212 integradas.

Referência visual: [protótipo da #211 no Figma Make](../../docs/referencias/issue-211-design/README.md). O protótipo é direção visual, não contrato: escalas, agregações, privacidade, autenticação, permissões, contratos da API e dados do SIGAA não mudaram.

## Decisões tomadas na implementação

| Ponto do protótipo | Decisão | Motivo |
| --- | --- | --- |
| Ações principais em azul (`#7eb4ff`) e foco âmbar | Mantido o verde UnB (`--primary`) nas ações principais e o foco verde | Decisão integrada pela #212/PR #214 e pedido da #211 de reutilizar esses tokens; confirmado pela autora do protótipo |
| Comparação em carrossel coverflow com a dependência Swiper | Cartões por professor em rolagem horizontal com `scroll-snap` e setas, sem dependência nova | Evita nova tecnologia estrutural; todos os professores continuam acessíveis por rolagem, teclado e setas; confirmado pela autora |
| Botão “Entrar” isolado no cabeçalho | Mantido “Entrar ou criar conta” e “Minha conta” com sessão | Critério da #211 (ponto vindo da #221) e regressão `tests/cabecalho-browser.mjs` |
| “Sem comentários públicos” no passo Contribua | Texto ajustado: comentário opcional com moderação humana | Comentários existem desde a #206 |
| “Suas respostas foram preservadas” no login | Substituído por “Você voltará para esta avaliação” | O formulário não guarda respostas entre páginas; só o `returnTo` validado é preservado |
| Exemplo com professora e disciplina reais na home | Exemplo rotulado “Exemplo ilustrativo · dados fictícios”, com nomes genéricos | Não transformar dados demonstrativos em aparência de dado de produção |
| Menu hambúrguer no celular | Navegação quebra em linha abaixo da marca | Menos estados e nenhum conteúdo escondido; sem nova interação a manter |
| Selo “Dados demonstrativos” nas páginas internas | Não aplicado | As páginas oficiais exibem dados reais da API |

## Pontos revisados

| # | Tela/componente | Problema observado | Ajuste realizado |
| --- | --- | --- | --- |
| 1 | Tokens (`globals.css`) | Fundo azulado `#0b0f17` e superfícies com pouca separação | Canvas preto, superfícies `#0d1118`/`#131a24`, bordas `#273243`/`#46566e`, texto `#f4f7fb`, azul `#7eb4ff` só para realce; verde e foco da #212 preservados |
| 2 | Cabeçalho | Painel sólido com borda; navegação cinza de 13 px; “Comparar professores” duplicava “Disciplinas” | Cabeçalho fixo translúcido; navegação centralizada com pílula “Buscar”, Professores, Disciplinas e Unidades; `aria-current` na rota atual; ações de conta como botão fantasma |
| 3 | Busca (`BuscaNavegacao`) | Select e campo retangulares com lupa desenhada em CSS | Superfície contínua em pílula, ícone SVG, placeholder com exemplos; na home, seletor segmentado Disciplina/Professor com o mesmo campo `busca` |
| 4 | Botões | Raio 9 px, sem variante discreta, sem resposta ao toque | Raio 10 px, variantes `ghost` e `pill`, compressão leve ao pressionar (desligada com movimento reduzido); estados disabled preservados |
| 5 | Rodapé | Três textos soltos | Marca, descrição, navegação (com Unidades) e linha institucional |
| 6 | Home — destaque | Título de 48 px sem hierarquia de apoio | Sobretítulo com traço verde, título de 40–76 px, mapa de vento decorativo atrás do título |
| 7 | Home — exemplo | A home não mostrava como um resultado é lido | Cartão de exemplo rotulado como fictício, com o mesmo bento das páginas reais |
| 8 | Home — princípios, passos e dados | Texto institucional disperso | Faixa de princípios, “Como funciona” em três passos e “Dados com contexto e cuidado” |
| 9 | Catálogo da home e unidades | Títulos com borda lateral; cartões sem estado de hover consistente | Sobretítulo + título de seção; cartões `.tile` com chip do código e linha de realce |
| 10 | Disciplina — cabeçalho | Caixa azul com código em texto corrido | Chip do código, título de página, unidade e retorno alinhado |
| 11 | Disciplina — comparação | Tabela de 820 px com rolagem horizontal no celular | Cartões por professor: didática com estrelas, dificuldade/chamada/material neutros, recomendação com barra, ações; insuficientes em caixa tracejada; ordenação e homônimos preservados |
| 12 | Consulta — perfil | Avatar retangular de 134×168 px e muitas etiquetas | Avatar circular de iniciais, sobretítulo, título; cartão da disciplina com ações de avaliar e comparar |
| 13 | Consulta — critérios | Cinco cartões idênticos | Bento: Recomendação em destaque, Didática com estrelas, três critérios informativos sem cor de alerta; sem nota geral |
| 14 | Consulta — insuficiente/sem avaliações | Texto em painel simples | Painel com ícone, explicação do mínimo e ação “Contribuir com uma avaliação” |
| 15 | Avaliação — critérios | Selects exigiam dois toques e rótulos curtos | Botões de opção (rádios nativos) em grade, perguntas completas, dica de neutralidade por critério, seções 01/02/03 |
| 16 | Avaliação — contexto e mensagens | Contexto em painel genérico; sucesso/erro com bordas genéricas | Faixa de contexto com borda azul; caixas de status com tokens de sucesso e erro |
| 17 | Login e cadastro | Painel simples; “Mostrar senha” como botão grande | Cartão translúcido sobre fundo decorativo, campos sublinhados com realce em gradiente no foco, aviso de retorno; “Mostrar senha” como link com alvo de 44 px |
| 18 | Busca, professor e resultados por professor | Títulos e campos fora do novo padrão | Sobretítulo/título, campos `.field`, cartões `.tile`, avatar de iniciais |

Componentes novos: `Icone`, `MapaVento`, `FundoLiquido`, `EstrelasDidatica`, `ResultadoBento`, `MolduraConta` e o helper `lib/iniciais.ts`. `CriteriosAgregados` foi removido por ficar sem uso.

## Acessibilidade e estados

- Fundos animados (`MapaVento`, `FundoLiquido`) são `aria-hidden`, não recebem foco, pausam fora da tela e ficam estáticos com `prefers-reduced-motion`.
- As estrelas têm `role="img"` com a média por extenso; os demais critérios continuam em `dl`.
- Os critérios da avaliação continuam com os mesmos `name`/`value`, `required` e navegação por setas entre rádios; o foco visível é desenhado no rótulo.
- Fundos decorativos não usam `filter`/`backdrop-filter` animados (custo alto sem GPU); o mapa de vento roda a ~30 quadros por segundo.
- Os campos sublinhados trocam o contorno pelo sublinhado de 2 px em gradiente azul/verde, com contraste acima de 3:1 sobre o fundo.
- Estados cobertos: carregamento, vazio, erro, insuficiente, sem avaliações, sucesso e falha de envio, sessão autenticada e visitante.

## Verificação

Ambiente: macOS, Node 24.21.0, Next 16.3.5, Chrome (o CI usa Edge no Windows).

| Verificação | Resultado |
| --- | --- |
| `npm run lint` | Aprovado, sem avisos |
| `npm run typecheck` | Aprovado |
| `npm test` | 77 testes aprovados, incluindo contraste dos tokens (`tests/paleta.test.mjs`) |
| `npm run build` | Aprovado |
| `tests/moderacao-browser.mjs` | Aprovado |
| `tests/denuncia-browser.mjs` | Aprovado |
| `tests/comentarios-browser.mjs` | Aprovado; preenche o formulário pelos novos rádios |
| `tests/cabecalho-browser.mjs` | Aprovado: visitante, sessão, “Minha conta”, retorno e 320/768/1280 px |
| `tests/identidades-browser.mjs` | Aprovado |
| `tests/avaliacao-browser.mjs` | Primeira execução no CI (PR #230) revelou duas falhas, corrigidas: um passo ainda atribuía `value` ao campo `material` (agora clica o rádio) e os rótulos dos campos de conta ficavam em caixa alta no `innerText` (agora sem `text-transform`). **Localmente inconclusivo:** 1ª execução: passos do formulário (rádios, validação, envio, foco por teclado, notas em uma linha a 320 px) aprovados; parou depois, em `busca-browser.mjs:177` (“conta visitante validada”). 2ª execução: tempo esgotado no CDP (`Runtime.evaluate`) em outro ponto. Uma sonda isolada na mesma rota mostrou o cabeçalho de visitante correto. Depende de confirmação no CI |
| Transbordamento horizontal | Nenhum nas 10 rotas capturadas em 320, 390, 768 e 1440 px (`scrollWidth <= innerWidth`) |
| `git diff --check` | Aprovado |

Testes de navegador fora do CI (`busca`, `acesso`, `perfil`, `resultados`) tiveram seletores atualizados para rádios e cartões, mas não foram reexecutados nesta entrega.

## Capturas antes/depois

Fixture local com dados fictícios (sem backend real), Chrome headless via CDP, página inteira. Pasta: [`capturas/issue-211`](capturas/issue-211/).

| Tela | Largura | Antes | Depois |
| --- | --- | --- | --- |
| Home | 1440 px | [antes](capturas/issue-211/home-1440-antes.jpg) | [depois](capturas/issue-211/home-1440-depois.jpg) |
| Home | 390 px | [antes](capturas/issue-211/home-390-antes.jpg) | [depois](capturas/issue-211/home-390-depois.jpg) |
| Comparação da disciplina | 1440 px | [antes](capturas/issue-211/disciplina-1440-antes.jpg) | [depois](capturas/issue-211/disciplina-1440-depois.jpg) |
| Comparação da disciplina | 390 px | [antes](capturas/issue-211/disciplina-390-antes.jpg) | [depois](capturas/issue-211/disciplina-390-depois.jpg) |
| Consulta professor × disciplina | 1440 px | [antes](capturas/issue-211/consulta-1440-antes.jpg) | [depois](capturas/issue-211/consulta-1440-depois.jpg) |
| Consulta professor × disciplina | 390 px | [antes](capturas/issue-211/consulta-390-antes.jpg) | [depois](capturas/issue-211/consulta-390-depois.jpg) |
| Avaliação | 1440 px | [antes](capturas/issue-211/avaliar-1440-antes.jpg) | [depois](capturas/issue-211/avaliar-1440-depois.jpg) |
| Avaliação | 390 px | [antes](capturas/issue-211/avaliar-390-antes.jpg) | [depois](capturas/issue-211/avaliar-390-depois.jpg) |
| Login | 1440 px | [antes](capturas/issue-211/login-1440-antes.jpg) | [depois](capturas/issue-211/login-1440-depois.jpg) |
| Login | 390 px | [antes](capturas/issue-211/login-390-antes.jpg) | [depois](capturas/issue-211/login-390-depois.jpg) |

As capturas de 1440 px foram reduzidas para 1080 px de largura para economizar espaço no repositório.

Testes técnicos e emulação não substituem o reteste com alunos da #166.
