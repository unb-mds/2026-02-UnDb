# Frontend

Scaffold do frontend do UnDb com Next.js 16, TypeScript e Tailwind CSS.

## Execução local

**Pré-requisito:** Node.js 20.9 ou superior com npm.

```bash
npm ci
npm run dev
```

A aplicação fica disponível em [http://localhost:3000](http://localhost:3000). Nesta etapa
inicial, o frontend não depende do backend nem exige variáveis de ambiente para iniciar.

O App Router está em `src/app/`. Para alterar a página inicial, edite
`src/app/page.tsx`; o servidor de desenvolvimento atualiza a página automaticamente.

## Comandos disponíveis

- `npm run dev`: inicia o servidor de desenvolvimento.
- `npm run lint`: executa o ESLint.
- `npm run build`: gera o build de produção.
- `npm run start`: serve um build de produção já gerado.

A estratégia definitiva de execução e containerização do frontend permanece pendente na
[Issue #36](https://github.com/unb-mds/2026-02-UnDb/issues/36).
