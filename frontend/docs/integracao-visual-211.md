# Integração visual — #211

Base: PR #230, commit `3d24a46`. A revisão preserva os contratos reais e não copia as
rotas temporárias `/simulacao`, a conta demonstrativa ou sessionStorage para o produto.

- Home com título animado e degradê azul/verde, busca existente e conteúdo secundário
  compacto; destaques reais por quantidade de avaliações, sem nota geral da disciplina.
- `GET /api/disciplinas/destaques`: até seis disciplinas com avaliações, em quantidade
  decrescente, desempate por nome e ID. Consulta agrupada, sem migration ou escrita.
  A home complementa com no máximo seis consultas agregadas existentes. Falha dessa
  seção não impede a busca ou o catálogo institucional. Critérios abaixo de três
  avaliações permanecem ocultos.
- Comparação: cartão inteiro seleciona professor; ações de avaliar e abrir perfil
  acompanham a seleção. Comentários usam os serviços reais, com cancelamento da
  consulta anterior ao trocar o professor. Contexto de busca preservado.
- Perfil mantém disciplinas agrupadas; consulta do professor na disciplina com avatar
  retangular, ações, critérios, comentários e professores relacionados.
- Conteúdo usa largura máxima de 1600 px e margens responsivas. Seta do select possui
  recuo e desenho próprios, preservando o controle HTML nativo e teclado.
- Sobre: seis integrantes conforme README, avatares públicos do GitHub armazenados
  localmente; LinkedIns fornecidos pelo usuário. Perfis faltantes não geram links.
  URLs consultadas: `https://api.github.com/users/{login}` e `/social_accounts`.
- Moderação: link oculto inicialmente, para visitantes, em erro e após logout;
  somente aparece após autenticação e sucesso da rota de moderação protegida.
  Nenhuma permissão é concedida pelo cliente. A sessão atual não expõe papel;
  por isso usa a consulta existente da fila, sem exibir seu conteúdo no rodapé.

A falha do CI da PR #230 em `prototipo-browser.mjs:252` procurava um ring/box-shadow
no próprio input. O novo rádio desenha o foco no rótulo adjacente com outline.
A regressão foi ajustada para verificar o foco visível no elemento renderizado,
sem remover a verificação de teclado ou a espessura mínima de 2 px.

Fotos e links podem ser atualizados em `src/app/sobre/equipe.ts` e `public/equipe/`.
Não foram alterados importadores, migrations, configuração local ou bancos reais.

## Validação local

- Build de produção e TypeScript aprovados; lint sem avisos.
- 77 testes unitários de frontend aprovados.
- 224 testes determinísticos de backend aprovados (2 ignorados), em SQLite isolado.
- Navegador Brave/Chromium: avaliação, busca, catálogo, identidade visual, conta,
  protótipo, moderação, denúncia, comentários, cabeçalho, identidades e perfil aprovados.
- Regressão da PR #230 confirmada: foco dos rádios no rótulo e protótipo sem API.
- Regressão de moderação cobre estudante sem permissão, moderador e logout.
- Integrações PostgreSQL não foram reexecutadas localmente para preservar a importação.
