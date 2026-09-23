# Pesquisa e decisão de adaptação

## Resultado — 22/09/2026

**CREATE no sistema local, por adaptação seletiva de uma skill existente.** Nenhuma skill local inspecionada reunia geração de páginas Next.js, Tailwind e os padrões do UnDb. Estender `implementation` misturaria procedimento geral e regras específicas de framework.

Foram consultados os `SKILL.md` das quatro categorias do projeto, o catálogo disponível nesta sessão, a árvore pessoal de skills e o cache de plugins acessível. Os templates locais de apresentação/documentos não são geradores de páginas Next.js.

O diretório de plugins retornou **Vercel**, disponível e não instalado, na busca por Next.js/Tailwind/frontend. Não foi necessário conectar conta, instalar plugin ou habilitar deploy: o material público basta para a adaptação local.

## Fonte externa selecionada

[Skill nextjs do plugin Vercel no repositório openai/plugins](https://github.com/openai/plugins/blob/main/plugins/vercel/skills/nextjs/SKILL.md), cujo [arquivo bruto](https://raw.githubusercontent.com/openai/plugins/main/plugins/vercel/skills/nextjs/SKILL.md) foi lido.

A adaptação retém o enfoque em fronteiras servidor/cliente, parâmetros assíncronos, convenções de rotas e consulta de documentação. Foi redigida em português, com procedimento próprio e referências locais, sem copiar o pacote ou depender de suas ferramentas. Foram excluídas orientações de deploy, migração e otimizações sem demanda local. As referências externas `rsc-boundaries.md` e `async-patterns.md` não puderam ser recuperadas nesta consulta; as orientações foram conferidas nos guias distribuídos com o Next.js instalado e no código do projeto.

Fontes complementares consultadas:

- [Tailwind: responsividade](https://tailwindcss.com/docs/responsive-design): distinção entre base móvel, breakpoints e larguras de inspeção.
- [Tailwind: tema escuro](https://tailwindcss.com/docs/dark-mode): comportamento por preferência do sistema; configuração local conferida em `globals.css`.
- Guias locais `frontend/node_modules/next/dist/docs/01-app/01-getting-started/03-layouts-and-pages.md` e `05-server-and-client-components.md`: trechos de convenções de páginas, layouts e fronteiras de execução.

Resultados de busca também apontaram skills comunitárias de App Router e desenvolvimento React/Next.js. Não foram importadas nem consideradas validadas somente por aparecerem na busca. Esta investigação cobre fontes acessíveis, não demonstra ausência de alternativas em todo o ecossistema.

## Estado e manutenção

Nome solicitado: **Gerador_Paginas_Next_Tailwind**. Identificador e diretório: `gerador-paginas-next-tailwind`, conforme naming portátil do projeto.

Preparada na versão `0.1.0`, estado **proposed**, mantido por solicitação explícita do responsável. A aprovação será solicitada a outro integrante na futura PR; criação de Issue e abertura de PR foram adiadas pelo responsável. A adaptação não muda skills existentes, regras de governança, stack ou configuração da aplicação.

Na configuração inicial não houve geração de páginas. Posteriormente, um teste descartável de Perfil de Estudante foi autorizado e apresentado exclusivamente na conversa, com dados fictícios e botão de edição desabilitado. Nenhum arquivo de página foi criado ou integrado. O exemplo foi revisado por leitura, sem lint, build ou inspeção em navegador; não comprova execução visual ou funcional. A revisão posterior esclareceu a exceção de teste autorizado e as saídas e verificações de cada modo de uso.

Os padrões locais ficam rastreáveis em [Contexto do repositório](contexto-repositorio.md); reler as fontes atuais ao usar a skill. O procedimento pode ser carregado pelo caminho canônico através do bootstrap existente, sem um adapter específico de agente.
