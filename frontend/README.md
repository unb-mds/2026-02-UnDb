# frontend

Next.js (App Router) + Tailwind CSS. Instruções completas de execução local — incluindo
como apontar para o backend — estão no [README da raiz do repositório](../README.md#frontend).

```bash
npm install
npm run dev
```

## Padrão visual (proposta — Issue #31)

Esta seção documenta o padrão que já vem sendo seguido nas telas existentes
(`/professores`, `/disciplinas`), pra qualquer tela nova partir do mesmo lugar em vez de
decidir cor e espaçamento do zero. É uma **proposta**, não uma identidade de marca fechada —
o produto ainda não tem uma definida, e a Issue #31 pede especificamente cor, tipografia e
layout base, não uma marca completa.

### Paleta de cores

Tokens em `src/app/globals.css`, com um par claro/escuro cada — nunca usar valor hexadecimal
direto no JSX, sempre a classe Tailwind correspondente ao token.

| Token | Uso | Claro | Escuro |
|---|---|---|---|
| `--background` / `bg-background` | Fundo da página | `#ffffff` | `#0a0a0a` |
| `--foreground` / `text-foreground` | Texto principal | `#171717` | `#ededed` |
| `--accent` / `text-accent` | Link e elemento interativo primário | `#2563eb` | `#60a5fa` |

Texto secundário usa opacidade sobre `foreground` (`text-foreground/70`, `/60`, `/50`) em vez
de um token de cinza separado — mantém a hierarquia visual coerente em claro e escuro
automaticamente, sem precisar de um segundo par de tokens.

**Regra de produto, não só de estilo:** dificuldade e chamada (ver `docs/requisitos.md`)
**nunca** recebem cor semântica (vermelho/verde, ícone de bom/ruim) — são informativos, não
avaliações de qualidade. A tela de avaliação agregada (`/professores/[id]/disciplinas/[id]`)
já segue isso: todo critério é texto simples, sem cor condicional.

### Tipografia

- **Geist Sans** — texto de interface (títulos, corpo, rótulos). Carregada via `next/font`
  em `layout.tsx`, já otimizada (sem link externo, sem flash de fonte).
- **Geist Mono** — dado tabular e identificador: código de disciplina (`CIC0002`), nota
  numérica (`4.3 / 5`), percentual (`75%`). Sinaliza "isso é um dado", não prosa.

Escala usada até aqui: título de página `text-2xl font-semibold`, seção `text-sm font-medium`,
corpo `text-sm`, legenda `text-xs`. Não introduzir tamanho fora dessa escala sem necessidade.

### Layout base

- Coluna única centralizada, `max-w-2xl`, `px-4` de respiro lateral, `py-10` vertical.
- Espaçamento entre blocos por `gap-6` no container, nunca margem manual em cada filho.
- Cartão: `rounded-lg border border-foreground/10 px-4 py-3`, com
  `hover:border-foreground/30 hover:bg-foreground/[0.03]` quando é link.
- Navegação de volta como link de texto simples acima do título (`← Buscar outro professor`),
  não breadcrumb nem botão.

### O que ainda não está aqui

As telas já existentes (`#44`, `#45`, `#43`) foram construídas **antes** desta proposta ser
formalizada — elas já seguem esse padrão porque foi daí que ele foi extraído, mas não foram
retocadas para usar o token `--accent` (nenhuma ainda usa cor de destaque; toda a interação
hoje é por contraste de borda/fundo neutro). Aplicar `--accent` nelas, se o time aprovar essa
paleta, fica para quem pegar essa tarefa em seguida — não foi feito aqui para não reabrir
código já testado e commitado em outra branch.
