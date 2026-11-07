# Base visual dark — issue #202

A aplicação oficial usa agora os tokens e a navegação compartilhada da proposta dark. As páginas de home/resultados (#203), perfil/comparação (#204), conta/avaliação (#205) e comentários/moderação (#206) continuam com entregas próprias. A #202 não conclui essas issues.

## Contrato para as próximas entregas

- `src/app/globals.css` contém os tokens e as classes comuns. Use `--background`, `--foreground`, `--panel`, `--raised`, `--border`, `--muted`, `--accent`, `--on-accent`, `--primary`, `--primary-hover`, `--on-primary`, `--focus`, `--danger` e `--radius`. `accent` é a cor clara de texto/realce; `primary` é a superfície azul de ação. Preserve os pares de contraste.
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
