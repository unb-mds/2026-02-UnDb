# Base visual dark — issue #202

A aplicação oficial usa agora os tokens e a navegação compartilhada da proposta dark. As páginas de home/resultados (#203), perfil/comparação (#204), conta/avaliação (#205) e comentários/moderação (#206) continuam com entregas próprias. A #202 não conclui essas issues.

## Contrato para as próximas entregas

- O tema dark é fixo: o layout aplica `.dark` em `html` e `globals.css` associa as variantes `dark:` a essa classe. Cores de erro, sucesso e demais estados devem acompanhar o tema da aplicação, inclusive quando o sistema prefere o tema claro. Não reintroduzir dependência de `prefers-color-scheme` para essas variantes.
- `src/app/globals.css` contém os tokens e as classes comuns. Use os pares de superfície/texto abaixo; `accent` continua azul para texto/realce e `primary` é verde nas ações integradas pela #212/PR #214. O PO solicitou o verde UnB e a logo; o refinamento geral da #211 usa essa base após #204/#206, sem bloquear retroativamente a #212. Preserve os pares de contraste.
- `.container` limita a largura compartilhada a 1280 px, com recuo lateral responsivo. `.panel` oferece superfície com bordas arredondadas. `.button` é a ação secundária e `.button.primary` a principal. Use elementos semânticos `button`/`Link`, labels e estados reais de `disabled`.
- `Cabecalho` e `Rodape` são montados uma vez no layout. O cabeçalho usa links existentes na home e busca compacta nas páginas internas; telas de conta ficam sem busca. Não repita esses componentes em cada página.
- `BuscaNavegacao` recebe `id` (obrigatório e único), `tipo`, `termo`, `ordem` e `compacta`. É formulário GET para `/busca`, cujo redirecionamento existente resolve a rota de resultados. `BuscaCabecalho` lê contexto da URL e remonta o formulário quando modalidade, termo ou ordenação mudam. Não adicionar outra rota de busca ou outra barra de etapas.
- `Caminho` recebe `itens: { nome: string; href?: string; retornoBusca?: boolean }[]`. Use links locais gerados pelos helpers de contexto. O último item sem `href` indica a página atual; `retornoBusca` identifica o link para os resultados. Breadcrumbs não são um indicador de etapas obrigatórias.
- O layout oferece link de teclado para `#conteudo`. Preserve esse destino, o foco visível e as labels dos formulários. A busca tem input arredondado, recuo interno e espaço próprio para a lupa.
- Os links de conta continuam validando `returnTo` pelo helper existente. Não montar retorno arbitrário nem mudar cookies, variáveis, endpoints ou permissões ao adaptar as telas.

## Fontes da referência

O [material de referência](../../docs/referencias/ui-dark/README.md) está versionado no repositório, com [guias por issue](../../docs/referencias/ui-dark/issues/203.md), fontes e capturas. Ele é consulta, não uma segunda aplicação nem código a ser substituído integralmente em `frontend/`. As notas e comentários das capturas são simulados.

A #202 importou esse material para permitir acesso direto a partir de `develop`; não é preciso adicionar novamente a pasta nos PRs seguintes. Os arquivos em `docs/referencias/ui-dark/src` preservam o snapshot anterior à integração. A implementação vigente e seus contratos ficam em `frontend/src` e neste documento.

## Validação da integração

Executar os scripts atuais de `frontend/package.json`: lint, typecheck, test e build. Conferir busca por professor/disciplina, alteração de consulta/ordem, navegação interna, retorno seguro de conta e foco de teclado. Verificar 320, 390, 768 e 1440 px. Os testes técnicos não substituem o reteste com alunos da #166.

## Verde, logo e favicon — Issue #212 / PR #214

**Estado:** integrado em `develop` pela PR #214, merge `ea7c39c`, aceito pelo PO;
issue #212 encerrada. Revisão adicional `73a535b`. Fora da tag v1.1.0.
Fonte: [direção do PO de 09/11/2026 na #212](https://github.com/unb-mds/2026-02-UnDb/issues/212).
Não se declara homologação da paleta pela UnB. A base dark é mantida e o azul
continua em links secundários, critérios e realces informativos.

| Token | Hex | Uso integrado |
|---|---|---|
| `--primary` | `#00822e` | Verde RGB 0, 130, 46 do manual UnB |
| `--primary-hover` | `#006b26` | Hover habilitado das ações principais |
| `--primary-active` | `#005a1c` | Ação principal pressionada |
| `--primary-border` | `#4ade80` | Limite visível da ação principal, inclusive hover/active |
| `--on-primary` | `#ffffff` | Texto/ícone sobre as três superfícies principais |
| `--focus` | `#86efac` | Contorno de teclado com offset de 4 px |
| `--control-border` | `#667b99` | Limite de botão secundário/desabilitado |
| `--disabled-surface` | `#253247` | Fundo sólido de botão desabilitado, sem reduzir opacidade |
| `--on-disabled` | `#b7c6db` | Texto/ícone desabilitado |
| `--accent` / `--on-accent` | `#75a7ff` / `#0b0f17` | Azul preservado para links e realces existentes |
| `--background` / `--foreground` | `#0b0f17` / `#e7ecf6` | Fundo dark e texto principal preservados |
| `--panel` / `--raised` | `#121825` / `#1b2537` | Superfícies dark preservadas |
| `--border` / `--muted` | `#29364e` / `#94a3bd` | Bordas de painéis e texto auxiliar preservados |
| `--danger` | `#fca5a5` | Alertas preservados; não reutilizar verde para erro/destruição |

### Inventário e hierarquia

- `.button.primary`: verde para Buscar na home/cabeçalho/resultados, Criar conta
  no cabeçalho, Avaliar um professor na home e Avaliar nas disciplinas agrupadas.
  Esses componentes já compartilham a classe e não precisam de cores por página.
- Formulários oficiais de login/cadastro e avaliação, ação de avaliar no detalhe
  professor/disciplina e ações principais da confirmação: migram apenas as classes
  para `.button.primary`. Labels, handlers, permissões e estados reais são preservados.
- `OpcoesAcesso`: opção atual verde e sublinhada com `aria-current` preservado; opção alternativa
  secundária. Logout e acesso antes de avaliar usam `.button` secundária.
- Detalhes existentes que usam `--primary`: gradiente da home, painel de
  convite a avaliar, fundos de código da disciplina e iniciais do professor. Os
  textos/links desses cartões continuam com foreground/accent; não há nota verde
  ou novo significado para Dificuldade/Chamada.
- `accent-color` de controles nativos herda primary; o contorno global de teclado
  herda focus. Os anéis azuis de seleção/foco dos critérios existentes permanecem.
- Consultar/comparar, navegação, mostrar/ocultar senha e links auxiliares continuam
  secundários/azuis. Erros, sucesso, retirada, denúncia e ações de moderação não
  recebem uma substituição indiscriminada de cores.

Estados de `.button`: normal; hover habilitado; active pressionado; foco de teclado
com contorno; disabled com superfície/texto próprios e cursor. Hover/active não
sobrescrevem disabled. `[aria-disabled="true"]` recebe apenas o estilo correspondente,
sem introduzir controle de permissões ou desabilitação pelo CSS.
Rótulos, `aria-current`, `aria-pressed`, mensagens e os indicadores existentes
continuam comunicando o estado além da cor.

### Contrastes calculados

`tests/paleta.test.mjs` calcula luminância relativa sRGB a partir dos tokens hex,
com a mesma fórmula do helper de navegador existente. São pares opacos teóricos;
isso não comprova contraste renderizado de cada combinação/transparência da tela.

| Par calculado | Razão |
|---|---|
| on-primary / primary normal | 4,96:1 |
| on-primary / primary-hover | 6,71:1 |
| on-primary / primary-active | 8,47:1 |
| on-disabled / disabled-surface | 7,45:1 |
| focus / background, panel, raised | 13,66:1 / 12,64:1 / 10,95:1 |
| primary-border / background, panel, raised | 11,01:1 / 10,19:1 / 8,82:1 |
| control-border / background, panel, raised | 4,44:1 / 4,11:1 / 3,56:1 |

Os testes exigem 4,5:1 para texto das ações e links nas superfícies dark e 3:1
para foco/limites dos controles nas superfícies adjacentes. Não se afirma
conformidade WCAG de toda a aplicação a partir desses cálculos.

### Coordenação e comparação visual realizada

O texto inicial descrevia a proposta de Tiago e navegador indisponível naquele
ambiente. A revisão posterior executou os checks e a inspeção de navegador em
320/390/768/1440 px. #205 também foi integrada e encerrada; #204/#206 permanecem
com entregas próprias. #211 deve aguardar essas integrações para o refinamento final.

Antes: primary azul `#2467e8`, hover `#1d58cb`, foco `#a3c4ff`, enquanto formulários
usavam fundo accent azul claro. Depois integrado: ações principais compartilham
primary verde; ações secundárias, superfícies dark e azul accent são preservados.

O verde vem do [Manual de Identidade Visual da UnB, p. 65](https://fcte.unb.br/wp-content/uploads/2025/05/Manual_Identidade_Visual_UnB.pdf):
RGB 0, 130, 46; a indicação WebSafe `#006633` é outra representação do manual.
Hover/active são derivações do projeto. Isso não declara homologação do produto
ou da marca UnDb pela universidade.

A logo fornecida pelo PO foi otimizada em `public/brand/undb-logo.png` (600×201).
O cabeçalho usa `next/image`, largura 140 px no desktop e 108 px no celular,
com link “UnDb — início”; a imagem tem `alt=""` para não duplicar o nome acessível.
O símbolo à esquerda foi isolado em imagem quadrada transparente com auxílio de
geração de imagem e reduzido para `src/app/favicon.ico` (16/32/48 px) e
`src/app/icon.png` (192 px). O favicon pode exigir recarga por cache do navegador.

`tests/identidade-browser.mjs` verifica imagem carregada, assinatura real de
ICO/PNG, estados normal/hover/active/disabled, foco e contraste renderizado nas
quatro larguras. A revisão passou por 68 testes unitários do frontend, lint,
tipos, build e suíte de navegador; todos os checks remotos passaram.
Os resultados são históricos da PR #214, não reexecução nesta PR documental.
[Comparações, capturas e limites](../../docs/estudos/identidade-conta-catalogo-2026-11-10.md).
Testes e emulação não substituem o reteste com alunos #166.
