# Contexto do UnDb para geração de páginas

Retrato inspecionado em 22/09/2026. Os caminhos abaixo partem da raiz do repositório. Esta referência encaminha às fontes; não substitui regras de produto nem congela versões.

## Stack e validação

- `frontend/package.json`: Next.js **16.3.5**, React **19.2.8**, TypeScript **5**, Tailwind **4**, ESLint **9**; conferir resoluções no lockfile antes de implementar.
- `frontend/tsconfig.json`: `strict: true`, `noEmit: true`, `moduleResolution: bundler`, alias `@/*` para `src/*`. Reusar tipos existentes e `import type`.
- `frontend/eslint.config.mjs`: configuração flat com `eslint-config-next/core-web-vitals` e `eslint-config-next/typescript`; não há `.eslintrc` como fonte vigente.
- `frontend/postcss.config.mjs` e `src/app/globals.css`: `@tailwindcss/postcss`, `@import "tailwindcss"` e `@theme inline`; não criar configuração Tailwind 3.
- `frontend/README.md` e `.github/workflows/pull-request.yml`: `npm run lint` e `npm run build`. Não existe script `test` nem suíte de UI configurada. Um framework futuro permanece **Pending Decision** se necessário à tarefa; isso não bloqueia código testável nem verificações existentes.

## Rotas, componentes e contratos

| Fonte em `frontend/src/` | Uso como referência |
|---|---|
| `app/layout.tsx`, `app/globals.css` | Header único, navegação, idioma `pt-BR`, fontes, tokens e foco |
| `app/page.tsx`, `app/not-found.tsx` | Entrada pública e ausência de rota |
| `app/professores/page.tsx`, `app/disciplinas/page.tsx` | Busca no cliente; debounce de 300 ms, mínimo de duas letras, estados e descarte de respostas obsoletas |
| `app/professores/[id]/page.tsx` | Detalhe no servidor, `params: Promise`, 404; consulta sequencial intencional |
| `app/disciplinas/[id]/page.tsx` | Comparação no servidor e grade responsiva |
| `app/professores/[id]/disciplinas/[disciplinaId]/page.tsx` | Agregados por professor/disciplina |
| `app/cadastro/page.tsx`, `app/login/page.tsx` | Formulários interativos com serviços de autenticação |
| `app/confirmar-email/page.tsx`, `app/confirmar-email/confirmation-client.tsx` | `PageProps`, `searchParams` assíncrono, separação servidor/cliente |
| `lib/services/`, `lib/types/`, `lib/hooks/` | Transporte, contratos e comportamento reutilizável |

Não há diretório compartilhado de componentes no retrato atual; não presumir shadcn/ui, biblioteca de ícones, gerenciador de estado ou cliente de consultas instalado. Colocar componentes específicos junto da rota conforme o precedente de confirmação, extraindo compartilhados somente quando houver uso concreto.

`lib/services/api-client.ts` distingue `NEXT_PUBLIC_API_URL` no navegador e `API_INTERNAL_URL` no servidor, com fallback público; mantém `credentials: "include"`. Isso não encaminha automaticamente cookies recebidos pelo servidor Next.js: em telas autenticadas no servidor, verificar explicitamente o contrato antes de reutilizar o cliente. Não expor segredos em `NEXT_PUBLIC_*` nem guardar sessão em localStorage.

`lib/services/avaliacoes.ts` adapta o formato HTTP; `lib/types/avaliacao.ts` modela a união discriminada por `dadosSuficientes`. Refinar essa união antes de acessar critérios, sem fabricar zero para ausência. Reutilizar `ApiError` de `lib/services/http-error.ts`.

## Visual e responsividade

Fonte primária: seção **Padrão visual básico — Issue #31** de `frontend/README.md`, conferida contra `globals.css` e `layout.tsx`. Ler a tabela completa de paleta, tipografia e espaçamentos antes de gerar uma tela.

- Aplicar os tokens semânticos `background`, `foreground`, `accent` e opacidades documentadas, mantendo o azul sobre base neutra. Evitar cores literais no novo JSX.
- Herdar Geist Sans e Geist Mono carregadas via `next/font`; não carregar fontes por página.
- Buscas/detalhes usam contêiner `max-w-2xl`, `gap-6 px-4 py-10`; comparação usa `max-w-5xl`. Não duplicar header nem tornar sua altura fixa.
- Respeitar os papéis tipográficos, cartões, campos e foco definidos no README. Preservar um `h1`, hierarquia de títulos, rótulos e mensagens de erro além da cor; regiões assíncronas podem usar `aria-live="polite"` conforme as buscas existentes.
- Tema segue `prefers-color-scheme` e `color-scheme` em `globals.css`. Não introduzir seletor de tema, provider ou classe `.dark`; usar `dark:` quando necessário, conforme a configuração vigente.
- **320/768/1280 px são larguras de inspeção**, não uma configuração personalizada. Layout móvel usa classes sem prefixo; as grades existentes passam a duas colunas em `sm` (640 px). Sem sobrescrita local, `md` corresponde a 768 px e `xl` a 1280 px. Não criar breakpoint de 320 px.

## Produto e arquitetura

Ler `docs/requisitos.md` (seções de consulta, comparação, critérios, restrições e decisões) e `docs/arquitetura.md` (ADRs pertinentes). Regras a conferir para telas de avaliação:

- Consulta pública; registro depende de autenticação e e-mail confirmado. Não coletar matrícula, CPF ou histórico acadêmico.
- Mostrar contagem das avaliações. Com menos de três, comunicar insuficiência sem critérios; ausência não significa nota negativa.
- Consumir agregados do backend, incluindo estado conflitante; não recalcular negócio no JSX. Ordenação usa recomendação e desempates definidos no contrato, sem nota composta.
- Dificuldade e Chamada são neutras: sem vermelho/verde, alertas de valor ou ranking por esses critérios.
- Não adicionar comentários livres de avaliação ou moderação da Release 2 a uma tela da Release 1. Isso não proíbe os campos de busca, nome e e-mail já previstos.

ADR 02 aprova Next.js/Tailwind; ADR 08 registra servidor Next.js e standalone condicional para Docker. Não introduzir export estático nem acoplar esta skill à Vercel. O backend FastAPI conserva contratos, agregação e persistência.

## Divergências e limites conhecidos

- A tabela de pendências de `docs/requisitos.md` e a visão ainda mencionam execução/deploy do frontend pendente; ADR 08 registra aprovação da execução em 19/09/2026 e o código a implementa. Registrar a divergência, preservar a implementação ao gerar telas e não decidir nova infraestrutura de produção nem corrigir documentação fora do escopo.
- O texto de navegação no README enumera professores/disciplinas, enquanto o layout atual também inclui entrar/criar conta. Herdar o layout evita apagar ou duplicar links.
- `docs/agent-skills.md` é inventário datado: a descoberta atual ocorre pelo bootstrap `AGENTS.md` e leitura dos arquivos em `skills/`. Não prometer registro nativo ou comando `$...` sem verificar integração. É possível pedir leitura desta skill pelo caminho canônico.
- `docs/figma.md` aponta a um board de requisitos; seu conteúdo remoto não foi inspecionado nesta configuração. Não declarar fidelidade a um mockup Figma.
- As evidências em `docs/estudos/` descrevem execuções históricas e limites; não equivalem a testes da próxima tela.
