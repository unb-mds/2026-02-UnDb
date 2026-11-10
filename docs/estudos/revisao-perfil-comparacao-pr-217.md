# Revisão de perfil e comparação — PR #217

Revisão de 10/11/2026, sobre `29f2ac2`, comparada com `develop` (`b3a7990`).
Escopo: os seis arquivos da PR; fontes: critérios da issue #204, seu guia em
`docs/referencias/ui-dark/issues/204.md`, contrato `frontend/docs/ui-dark.md`,
serviços e contratos atuais, `CONTRIBUTING.md` e skills de governança, revisão,
implementação e testes.

## Problemas corrigidos

- A comparação reordenava empates de recomendação/quantidade com `localeCompare`
  em pt-BR, enquanto a API usa `nome.casefold()`. Por exemplo, Zélia precede Álvaro
  na API, mas o cliente invertia os nomes. A ordem padrão agora preserva a resposta
  e a ordem crescente altera somente a recomendação, mantendo os desempates e os
  registros insuficientes ao final.
- A falha da consulta complementar de comparação era convertida em “Nenhum outro
  professor cadastrado”. Agora há aviso de indisponibilidade separado do vazio
  confirmado; os critérios e comentários continuam independentes dessa consulta.

## Verificação

Ambiente: Windows, Node 24.22.1, Next.js 16.3.5, Edge headless. Dependências
reutilizadas de instalação local com `package-lock.json` idêntico, sem mudança de
versões. npm não disponível no PATH; executados os comandos Node equivalentes aos
scripts, a partir de `frontend/`:

| Comando | Resultado |
| --- | --- |
| `node node_modules/eslint/bin/eslint.js` | Aprovado |
| `node node_modules/next/dist/bin/next typegen` e `node node_modules/typescript/bin/tsc --noEmit` | Aprovados |
| `node tests/run-tests.mjs` | 71 testes aprovados |
| `node node_modules/next/dist/bin/next build --webpack` | Build aprovado |
| `node tests/perfil-browser.mjs` (`npm run test:perfil`) | Aprovado em 320, 390, 768 e 1440 px |
| `git diff --check` | Aprovado |

A nova suíte verifica ordem recebida com acentos e empates, ordem crescente via
Enter e foco visível, homônimos separados por turma, contexto nos links, cartões
dos cinco critérios, ausência dos cartões abaixo de três avaliações, conflito,
rolagem contida e ausência de overflow da página. Também diferencia falha HTTP
503 de lista vazia e verifica que a falha complementar preserva os critérios.
As respostas são sintéticas e a suíte usa as rotas oficiais, sem alterar dados
reais. Não houve inspeção visual de capturas ou reteste com alunos.

Os seletores de `tests/resultados-browser.mjs` foram adaptados de cartões para
tabela, mantendo a verificação da ordem e da ausência de critérios insuficientes.
Essa suíte com FastAPI/PostgreSQL reais não foi executada nesta revisão.

O build padrão com Turbopack falhou no ambiente: no sandbox, acesso às fontes
Google; fora dele, inicialização do subprocesso de CSS. Webpack foi usado como
alternativa já registrada no projeto, sem alterar o script ou configuração de
build. O build padrão permanece não validado localmente.

Revisão técnica concluída para o escopo descrito. Não equivale a aprovação humana
da PR ou ao reteste com alunos da #166.
