# Revisão da PR #233

Revisão de 13/11/2026, sobre `28af48b`, por solicitação do PO.

## Correções dos checks

- O teste da rota de destaques passa a enviar uma requisição ASGI real e conferir
  HTTP 200/lista vazia, em vez de inspecionar `app.routes`, cuja representação
  interna mudou no FastAPI. Usa os mecanismos ASGI já adotados na suíte, sem nova
  dependência ou alteração do endpoint.
- O teste de mostrar/ocultar senha seleciona o controle dentro de `main`, evitando
  confundi-lo com o botão do menu, que também usa `aria-controls`.
- O menu recolhido passa a cobrir tablets até 1023 px. Os testes abrem o menu antes
  de conferir a visibilidade e o foco do acesso à conta e verificam seu fechamento.
- O fundo decorativo dos títulos internos fica limitado à largura do título,
  evitando transbordamento na busca e nas unidades. As verificações de overflow
  permanecem e passam a informar rota, largura e elementos excedentes.
- A espera pelo catálogo usa o conteúdo do título, sem depender da conversão visual
  para maiúsculas introduzida pelo CSS dos cartões.

## Direção visual confirmada pelo PO

- Campo da busca inicial escuro; atalhos redundantes continuam removidos.
- Ajuda opcional “Primeira vez por aqui?” restaurada.
- Comparação preserva o painel maior e o fundo animado líquido da main.
- Cartões de professores compartilham um degradê escuro discreto, sem cores
  distintas que possam sugerir classificação de qualidade.
- Ordenação acima dos cartões; avaliar e perfil ficam na consulta do professor
  selecionado. Trocar o cartão mantém os destinos correspondentes.

Dados fictícios e a API local usados para a prévia ficam fora do repositório e
não entram no produto. Não foram executadas importação, reconciliação ou escrita
no banco público. As integrações PostgreSQL são verificadas pelo CI isolado.

## Verificação local

- ESLint e build de produção (Webpack/TypeScript): aprovados.
- Frontend: 77 testes unitários aprovados.
- Backend: 226 testes executados em SQLite isolado, 2 ignorados; Ruff e formatação aprovados.
- Navegador Brave/Chromium: avaliação, busca, catálogo progressivo, identidade,
  conta, protótipo (72 cenários), cabeçalho, moderação, denúncia, comentários,
  identidades e perfil/comparação aprovados.
- Perfil/comparação verificados em 320, 390, 768 e 1440 px.
- Integrações PostgreSQL ficam a cargo dos jobs isolados da PR; não foram usadas
  conexões ou dados da importação em andamento.

## Animações aprovadas pelo PO

- Pílula de seleção Disciplina/Professor desliza em 200 ms, mantendo rádios nativos,
  teclado e formulário GET funcional antes da hidratação.
- Botão da busca mostra “Buscando…” durante a navegação real do Next.
- Chegada à rota usa fade e deslocamento de 8 px em 240 ms, sem esperar para navegar,
  sem remontar os filhos e sem acrescentar dependências.
- Movimento reduzido desativa a pílula e a transição de página; alteração dessa
  preferência durante a animação cancela o movimento em curso.
- Lint, build/TypeScript, 77 testes unitários e regressão principal de navegador
  aprovados. `npm run test:transicoes` valida navegação sem recarga, consulta preservada,
  conclusão da entrada e ausência de animação com movimento reduzido.

O PO aprovou a prévia e autorizou o envio em um único commit em 13/11/2026.
O CI aprovado na correção intermediária `9cc772f` corresponde à base anterior às
animações; o commit consolidado exige seus próprios checks.

## Cartões e página inicial aprovados

- “Explore as disciplinas” passa a mostrar as mais avaliadas do site, por volume
  de respostas, usando a consulta real de destaques e grade de até três colunas.
- Cartões preservam nomes completos, código, quantidade e resumo de até dois
  professores; o limiar de privacidade continua sendo respeitado.
- A galeria expansível do catálogo deixa de ser usada na home. A navegação por
  unidades permanece, sem duplicar a listagem alfabética de disciplinas.
- Busca de professores usa cartões com o mesmo topo azul/verde das disciplinas,
  iniciais, nome e unidade; as matérias e ações permanecem agrupadas por identidade.
  Não foram inventadas fotos ou novas propriedades da API.
- Catálogo por unidade compartilha o topo em degradê, sem alternância de cores sólidas.
- Regressão de busca/navegação e as novas grades aprovadas em 320/390/768/1280/1440 px.

Os dados, nomes e contagens fictícios usados para mostrar a prévia continuam em
um servidor local fora do repositório. Não foram enviados ao banco público.
