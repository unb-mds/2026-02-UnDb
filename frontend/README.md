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

## Proposta parcial de padrão visual — Issue #31

Esta seção registra o que já existe no frontend e a proposta inicial da Issue #31. Ela não
representa um padrão visual aprovado nem conclui a Issue. Paleta, tipografia e layout ainda
precisam de decisão explícita do time antes de se tornarem regras para novas telas.

### Paleta candidata

Os tokens estão em `src/app/globals.css` e geram as classes Tailwind correspondentes.

| Token | Uso proposto | Claro | Escuro | Estado atual |
|---|---|---|---|---|
| `--background` / `bg-background` | Fundo da página | `#ffffff` | `#0a0a0a` | Em uso |
| `--foreground` / `text-foreground` | Texto principal | `#171717` | `#ededed` | Em uso |
| `--accent` / `text-accent` | Link e elemento interativo primário | `#2563eb` | `#60a5fa` | Disponível, ainda não aplicado |

As telas atuais usam opacidade sobre `foreground` (`text-foreground/70`, `/60`, `/50`) para
texto secundário. Dificuldade e chamada não recebem codificação de valor em vermelho/verde,
ícone de alerta ou posição em ranking, conforme a restrição de apresentação definida em
`docs/requisitos.md`. A comparação agregada atual está em `/disciplinas/[id]`.

### Tipografia observada

- A interface aplica atualmente `Arial, Helvetica, sans-serif` no `body`.
- Geist Sans e Geist Mono são carregadas via `next/font` e disponibilizadas como variáveis.
- `font-mono` já é usada em identificadores, como códigos de disciplina.
- As telas atuais usam tamanhos de `text-xs` a `text-3xl`, conforme o contexto.

Definir a família principal e uma escala tipográfica normativa continua pendente na Issue
#31. A presença das fontes e classes no código não constitui aprovação desse padrão.

### Layout observado

As telas de busca usam coluna centralizada com `max-w-2xl`, `px-4`, `py-10` e `gap-6`.
Outras telas possuem necessidades distintas: a página inicial usa espaçamento e cartões
maiores, enquanto a comparação em `/disciplinas/[id]` usa `max-w-5xl` e grade responsiva.
Links em listas normalmente usam borda e mudança neutra de fundo no `hover`.

### O que falta para concluir a Issue #31

- pesquisar e registrar as referências visuais previstas na Issue;
- obter aprovação explícita do time para a paleta, a tipografia e o layout base;
- decidir quais variações de largura, escala e cartão fazem parte do padrão;
- aplicar o padrão aprovado às telas existentes e verificar sua responsividade;
- substituir este registro parcial pela documentação definitiva do padrão aprovado.
