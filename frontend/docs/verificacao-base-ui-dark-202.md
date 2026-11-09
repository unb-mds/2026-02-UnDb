# Verificação da base visual — #202

Data: 06/11/2026. Base: `1435ef746065d9bdbb08d39e2f88337b4a804d94` (`develop`, após PR #200).

## Escopo entregue

Tokens dark, foco, botões, painéis, cabeçalho/rodapé, busca compartilhada e breadcrumbs nas páginas funcionais. Removida a barra numerada e o convite da home para a experiência antiga. A rota histórica `/prototipo` foi preservada sem ser incorporada à jornada. Fontes e capturas de referência disponibilizadas em `docs/referencias/ui-dark` para as próximas issues.

## Verificações executadas

Ambiente local: Windows, Node 24.22.1, dependências compatíveis com o lockfile (cópia independente do ambiente isolado, sem junction ou modificação do pacote). O executável `npm` não estava disponível no PATH desta sessão; os comandos equivalentes dos scripts existentes foram executados diretamente:

```sh
node node_modules/eslint/bin/eslint.js .
node node_modules/next/dist/bin/next typegen
node node_modules/typescript/bin/tsc --noEmit
node tests/run-tests.mjs
node node_modules/next/dist/bin/next build --webpack
```

Todos aprovados; 61 testes passaram. O build usa webpack como alternativa já disponível no Next para o ambiente Windows; scripts, lockfile e workflow do projeto foram preservados. O CI executa a configuração oficial na PR.

Inspeção em Edge headless usando Node/CDP e a infraestrutura `tests/browser-session.mjs` já existente, sem dependência nova:

- Home, resultados de professor, perfil, comparação, avaliação e login a 320/390/768/1440 px: 24 combinações sem transbordamento horizontal.
- Tema dark e rodapé presentes; nenhuma barra de etapas numeradas nas telas funcionais.
- Campo de busca com raio de 10 px e padding lateral de pelo menos 12 px, incluindo celular; lupa em área própria na entrada.
- Breadcrumb do perfil preserva termo e ordenação da busca; links de login/cadastro preservam a combinação professor/disciplina e contexto da avaliação.
- Primeira navegação por Tab alcança o link de pular para o conteúdo, com foco visível.
- Envio pela home encaminha professor/Ajax; envio pelo cabeçalho troca para disciplina/FGA0312. Valores do cabeçalho acompanham a navegação.
- Inspeção visual de capturas desktop e celular; `git diff --check` aprovado.

As consultas de dados foram somente leitura do catálogo público local. Na porta temporária 3100, as requisições de busca do navegador ficaram sujeitas ao CORS do backend já em execução; foi conferida também a apresentação de falha, sem alterar a configuração dos serviços existentes. Esta verificação da base não certifica uma nova integração de API, mutações de avaliação/moderação ou todo o conteúdo de resultados.

## Correções após o primeiro CI

Os primeiros jobs de Frontend, Evaluation end to end e Moderation end to end identificaram seletores que assumiam um único formulário/seletor/botão de envio no documento. A busca do cabeçalho passou a ser encontrada no lugar dos controles da página. Os cenários agora selecionam `main form`, `main select`, o botão principal ou o botão do diálogo de denúncia. As validações de autorização, motivo obrigatório, critérios, persistência e estados foram preservadas. O roteiro histórico do protótipo acessa sua rota diretamente e verifica que a home funcional não o incorpora.

A integração real de acesso também identificou um retorno indevido no cabeçalho da confirmação de e-mail com token inválido/usado. Foi preservado o comportamento anterior: o cabeçalho repassa `returnTo` entre login/cadastro e na própria avaliação; a página de confirmação decide quando oferecer a continuação após validar o token. A asserção original de token de uso único foi mantida.

Reprodução local de `avaliacao-browser.mjs` aprovada com as fixtures HTTP existentes: avaliação, busca/histórico/ordenação sem consultas extras, recuperação de erro, acesso e regressões de interface, além das 72 combinações do protótipo histórico. Para preservar o serviço local da porta 8000, o build temporário e somente a execução local dos testes usaram 8112; o código da aplicação, os scripts e o CI mantêm suas configurações oficiais.

Também passaram localmente `moderacao-browser.mjs` (fila, estados, seis ações, motivo e erros), `denuncia-browser.mjs` (denúncia/agradecimentos e consumo após visibilidade) e `comentarios-browser.mjs` (permissões, publicação, substituição e retirada). Os cenários com PostgreSQL real permanecem sob verificação nos jobs remotos; não foram executadas mutações no banco local do usuário.

O histórico da PR foi consolidado a pedido do PO. A versão final depende dos checks remotos e da revisão exigida pelo ruleset; os resultados antigos com falha não representam a versão corrigida.

## Correção de contraste após revisão

A revisão encontrou cores de texto destinadas ao tema claro sobre o fundo dark fixo: as variantes `dark:` ainda dependiam da preferência do sistema. O layout agora marca `html` com `.dark`, e `globals.css` vincula essas variantes à classe. A correção mantém os componentes e fluxos existentes, sem antecipar o redesenho das issues #205/#206.

No Edge headless, com preferência de sistema clara, o contraste da confirmação incompleta/inválida e do botão Denunciar passou de 4,02:1 para 6,64:1; o sucesso da denúncia passou de 3,40:1 para 12,01:1. Com preferência escura, os valores finais são os mesmos. A medição usa cores renderizadas convertidas para sRGB e compõe os fundos transparentes. Como controle negativo, remover `.dark` somente no DOM de teste com sistema claro reproduziu 4,02:1; restaurar a classe recuperou o contraste adequado.

Foram acrescentadas asserções de contraste mínimo de 4,5:1 nos cenários existentes de confirmação com token inválido e de denúncia (botão e sucesso), em ambas as preferências de sistema; a denúncia cobre também desktop/celular. Nenhuma asserção de negócio foi removida.

Validação da correção em worktree isolado, Windows, Node 24.21.0 e dependências locais: ESLint, `next typegen`, `tsc --noEmit`, 61 testes, build `next build --webpack` e as quatro suítes de `npm run test:browser` aprovados. Os cenários de navegador usaram fixtures HTTP controladas, sem mutações em PostgreSQL real. `git diff --check` aprovado.

## Limites e continuidade

Não houve mudança de backend, dados, cookies, infraestrutura, serviços de API, política de cobertura ou checks. Home/resultados completos (#203), perfil/comparação (#204), conta/avaliação (#205) e comentários/moderação (#206) seguem abertos. O [contrato compartilhado](ui-dark.md) orienta essas entregas; a cópia visual anterior fica apenas como referência.

Inspeção do diff contra o escopo #202: nenhum finding confirmado pendente nos componentes compartilhados após as verificações acima. Isso não substitui a revisão humana exigida em `CONTRIBUTING.md`, nem o reteste com alunos da #166.
