# Design system do UnDb

Catálogo documental da interface implementada, conferido em 17/11/2026 na base `df854bf`.
Fontes: `frontend/src/app/globals.css`, layout raiz e componentes de `frontend/src/components/`.
A orientação de documentar o design system foi relatada por Nicolas em
[17/11](orientacoes-2026-11-17.md). Este catálogo descreve decisões existentes e não
introduz redesign, biblioteca ou padrão de produto novo.

## Identidade e hierarquia

A interface usa fundo preto, superfícies frias, azul para informações e verde da UnB
nas ações principais. O tema atual é escuro, independentemente da preferência do sistema.
As fontes Geist Sans e Geist Mono são carregadas no layout raiz; páginas herdam a tipografia.

| Papel | Token / classe no código | Valor atual / uso |
|---|---|---|
| Fundo | `--background` | `#000000` |
| Texto principal | `--foreground` | `#f4f7fb` |
| Texto secundário | `--ink-soft` / `--muted` | `#c5cedb` / `#929fb2` |
| Superfície | `--panel` / `--raised` | `#0d1118` / `#131a24` |
| Borda | `--border` / `--border-strong` | `#273243` / `#46566e` |
| Informação e links | `--accent` | `#7eb4ff` |
| Ação principal | `--primary` / `--on-primary` | `#00822e` / `#ffffff` |
| Foco | `--focus` | `#86efac`, contorno 2 px com afastamento 4 px |
| Sucesso | `--success` / `--success-soft` | `#79d8b5` / `#133229` |
| Erro | `--danger` / `--danger-soft` | `#ff8d8d` / `#351b22` |
| Título de página | `.page-title` | `clamp(28px, 4vw, 40px)`, peso 600 |
| Título de seção | `.section-title` | `clamp(24px, 3vw, 32px)`, peso 600 |
| Arredondamento | `--radius-sm/md/radius/xl` | 6 / 10 / 16 / 24 px |

Esses valores são um retrato do código. Ao alterar a fonte, revisar este catálogo para
não manter especificação divergente. Espaçamentos utilitários e grades são definidos
nas rotas/componentes; não há uma nova escala imposta por este documento.

## Componentes e estados

| Elemento | Fonte para reutilização | Comportamento observado |
|---|---|---|
| Navegação | `cabecalho.tsx`, `rodape.tsx` | Menu responsivo, contexto de sessão e links de entrada |
| Botões | `.button`, `.button.primary` | Estados padrão/hover/active/disabled; mínimo visual de 44 px de altura |
| Campo de senha | `campo-senha.tsx` | Rótulo associado, mostrar/ocultar, ajuda de cadastro e preenchimento adequado |
| Busca | `busca-entrada.tsx`, `busca-institucional.tsx` | Estado de carregamento, resultado vazio, erro/nova tentativa e contexto na URL |
| Avaliação | `criterios-avaliacao.tsx` | Grupos de opções com legendas, critérios separados e seleção explícita |
| Resultado | Componentes de critérios/agregados e comparação | Contagem e insuficiência sem fabricar nota; conflito explícito |
| Conteúdo e feedback | `.status-box` e componentes de comentários/moderação | Sucesso/erro/pendência, permissões, retirada e estados privados |

Confirmar nome/contrato do componente na árvore atual antes de reutilizá-lo; o catálogo
não substitui seus serviços e tipos. Não copiar CSS da referência dark inteira para cada
rota. A referência de [06/11](referencias/ui-dark/README.md) preserva o histórico visual;
o código integrado posteriormente é a fonte atual.

## Acessibilidade e escrita

Os padrões existentes incluem um título principal por página, hierarquia de cabeçalhos,
rótulos associados, navegação por teclado, foco visível e mensagens em português.
Cor é acompanhada por texto/estado. Resultados insuficientes não recebem nota zero;
Dificuldade e Chamada são neutras. Autoria não divulgada publicamente não equivale a
anonimato absoluto.

As verificações de interface do projeto usam, conforme a suíte, 320/768/1280 px e outras
larguras registradas. Isso não declara conformidade universal, contraste auditado em todo
componente ou teste com smartphone físico. Evidências estão nos estudos e PRs de cada tela.

## Relação com Material Design

[Material Design 3](https://m3.material.io/) foi indicado como referência pela professora,
conforme relato de Nicolas. Pode orientar a organização de fundamentos, componentes e
estados; o UnDb continua usando seus componentes Next.js/Tailwind e tokens existentes.
Não foi adotado Material UI, SDK Android ou uma nova biblioteca por este registro.
O site oficial exige JavaScript; a referência não é evidência de conformidade Material 3.

Mudanças visuais futuras devem respeitar requisitos e decisões aprovadas. Este documento
não altera escalas, fluxos, tema ou poder de acesso.
