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
