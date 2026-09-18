# Frontend

Scaffold do frontend do UnDb com Next.js 16, TypeScript e Tailwind CSS.

## Execução local

**Pré-requisitos:** Node.js 20.9 ou superior com npm e o backend acessível pelo navegador.

```bash
npm ci
copy .env.example .env.local  # Windows
# cp .env.example .env.local  # Linux/macOS
npm run dev
```

A aplicação fica disponível em [http://localhost:3000](http://localhost:3000). Configure
`NEXT_PUBLIC_API_URL` em `.env.local` com a URL pública do backend. Para a execução local
documentada no repositório, o valor padrão é `http://localhost:8000`.

O App Router está em `src/app/`. Para alterar a página inicial, edite
`src/app/page.tsx`; o servidor de desenvolvimento atualiza a página automaticamente.

## Comandos disponíveis

- `npm run dev`: inicia o servidor de desenvolvimento.
- `npm run lint`: executa o ESLint.
- `npm run build`: gera o build de produção.
- `npm run start`: serve um build de produção já gerado.

A estratégia definitiva de execução e containerização do frontend permanece pendente na
[Issue #36](https://github.com/unb-mds/2026-02-UnDb/issues/36).

## Padrão visual básico — Issue #31

Base implementada nesta entrega para orientar as próximas telas. A solicitação de
implementação da [Issue #31](https://github.com/unb-mds/2026-02-UnDb/issues/31) é a origem
deste trabalho; este registro não afirma aprovação coletiva nem fechamento da issue.
Os valores ficam centralizados em `src/app/globals.css` e o header em `src/app/layout.tsx`.

### Referência pesquisada

O [SuaGradeUnB](https://github.com/unb-mds/2023-2-SuaGradeUnB) atende ao mesmo contexto
universitário. Suas [notas da versão 1.0.0](https://github.com/unb-mds/2023-2-SuaGradeUnB/releases/tag/v1.0.0)
registram uma identidade com cores próximas às da UnB e nome associado à universidade.
Para o UnDb, a escolha é manter o azul já existente como destaque sobre uma base neutra,
e usar o nome do projeto no header. Não foram copiados componentes ou valores de cores
da referência. A paleta abaixo consolida os tokens que já existiam no UnDb.

### Paleta

| Token / classe Tailwind | Uso | Claro | Escuro |
|---|---|---|---|
| `--background` / `bg-background` | Fundo e campos | `#ffffff` | `#0a0a0a` |
| `--foreground` / `text-foreground` | Texto principal | `#171717` | `#ededed` |
| `--accent` / `text-accent` | Marca, destaque de navegação e foco | `#2563eb` | `#60a5fa` |

O tema acompanha `prefers-color-scheme`; `color-scheme` adapta também os controles nativos.
Use `text-foreground/70` para descrições e `/60` para metadados. `/50` fica reservado a
informação auxiliar; não o use para instruções essenciais. Bordas de cartões usam
`border-foreground/10`, campos `/20` e hover de cartões `/30` com `bg-foreground/[0.03]`.
Erros de busca usam `text-red-600 dark:text-red-400`, sempre acompanhados de mensagem.
Não use vermelho/verde, alertas ou ranking para julgar Dificuldade e Chamada: são
informações neutras, conforme [requisitos](../docs/requisitos.md).

### Tipografia

Geist Sans é a família principal, aplicada no `body`, com fallback Arial, Helvetica e
sans-serif. Geist Mono (`font-mono`) fica reservada a códigos e identificadores. Ambas
já são carregadas por `next/font` no layout raiz, sem nova dependência.

| Papel | Classes | Tamanho / entrelinha |
|---|---|---|
| Título da página inicial | `text-3xl font-semibold` | 30 / 36 px |
| Título das demais páginas | `text-2xl font-semibold` | 24 / 32 px |
| Marca no header | `text-xl font-semibold` | 20 / 28 px |
| Título de cartão de entrada | `text-lg font-medium` | 18 / 28 px |
| Corpo e campos de busca | `text-base` | 16 / 24 px |
| Descrições e navegação | `text-sm` | 14 / 20 px |
| Rótulos auxiliares | `text-xs` | 12 / 16 px |

Mantenha um `h1` por página e hierarquia semântica de títulos. Peso regular para texto,
`font-medium` para ações e `font-semibold` para títulos.

### Layout base e espaçamentos

```text
┌──────────────────────────────────────────────────────┐
│ UnDb                         Professores Disciplinas │ header: max-w-5xl
├──────────────────────────────────────────────────────┤
│         Título e descrição                           │
│         Campo de busca / conteúdo                    │ main: max-w-2xl
│         Lista de resultados / cartões                │
└──────────────────────────────────────────────────────┘
Comparações: o conteúdo pode ocupar max-w-5xl.
Em telas estreitas, navegação e cartões quebram em linhas.
```

- Header compartilhado em todas as rotas: marca ligada a `/`, navegação para
  `/professores` e `/disciplinas`, borda inferior, `px-4 py-3`, sem altura fixa.
- Buscas e detalhes: `mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10`.
  A largura máxima é 42 rem (672 px com raiz de 16 px).
- Comparação de professores: `max-w-5xl` (64 rem / 1024 px) e grade responsiva existente.
- Início: `max-w-2xl`, `gap-8 py-16`, cartões em uma coluna e duas a partir de `sm`.
  Página não encontrada: mesma largura, `gap-3 py-16`.
- Espaçamentos: 4, 8, 12, 16, 24, 32, 40 e 64 px, correspondendo às unidades
  Tailwind 1, 2, 3, 4, 6, 8, 10 e 16. Cartões de entrada usam `p-5` (20 px).
- Listas: `gap-2`, cartões `rounded-lg px-4 py-3`. Cartões de entrada: `rounded-xl`.
- Campos: `rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base`.
- Links e controles recebem contorno azul de 2 px no `focus-visible`, com afastamento
  de 4 px. Não remova essa indicação de navegação por teclado.

### Exemplo para novas telas

O header é herdado do layout; não o repita na página.

```tsx
<main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
  <div>
    <h1 className="text-2xl font-semibold">Título da tela</h1>
    <p className="mt-1 text-sm text-foreground/70">Descrição da tarefa.</p>
  </div>
  {/* Conteúdo da tela */}
</main>
```

### Verificação

O frontend ainda não possui suíte de testes automatizados de interface nem script `test`.
Execute `npm run lint` e `npm run build`, como no CI. Eles verificam código e compilação,
mas não substituem a inspeção visual. Para revisar a interface com `npm run dev`:

- confira início, buscas, detalhes, comparação e página não encontrada;
- confira temas claro e escuro e larguras de 320, 768 e 1280 px;
- navegue por Tab e confira foco, links do header e quebra de linhas sem rolagem horizontal;
- confira estados de carregamento, lista vazia e erro com o backend disponível/indisponível.

Verificação desta entrega (18/09/2026): lint e build de produção passaram. Uma checagem
pontual no Edge headless cobriu início, as duas buscas e página não encontrada nos dois
temas e nas três larguras acima (24 combinações), verificando ausência de transbordamento
horizontal, header, destinos de navegação, fonte e tema. O foco por Tab na página inicial
também foi verificado. As capturas móveis dos dois temas foram inspecionadas visualmente.
Essa checagem não adiciona uma suíte ao projeto e não cobre fluxos com dados do backend.
