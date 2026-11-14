# Apresentação de conta e avaliação — #237

Fonte: [Issue #237](https://github.com/unb-mds/2026-02-UnDb/issues/237), revisão do PO relacionada à #211 / PR #233. Ajuste de apresentação sobre os contratos existentes; não altera requisitos, autenticação, autorização, critérios ou persistência.

## Estados apresentados

| Contexto | Apresentação |
| --- | --- |
| `/login`, sessão ativa | Minha conta, indicação de sessão ativa e Sair; sem abas ou convite de cadastro |
| `/login`, visitante verificado | Entrar, formulário e acesso ao cadastro |
| Sem sessão previamente verificada, consulta em andamento ou com erro | Mensagem neutra; erro oferece nova verificação, sem afirmar logout ou sessão ativa |
| Avaliação, visitante | Orientação e link Entrar para avaliar, preservando `returnTo` |
| Avaliação, autenticado com confirmação pendente | Orientação para confirmar o e-mail e verificar novamente |
| Avaliação, autenticado confirmado | Indicação de que pode enviar a avaliação |

`GET /api/auth/sessao` continua retornando somente `autenticado`. A confirmação é reconhecida pela consulta **já existente** a `GET /api/comentarios/meu`: sucesso exige e-mail confirmado; 403 indica confirmação pendente após sessão autenticada; 401 indica acesso ausente/expirado. Fonte: [especificação desse endpoint](../../specs.md#acompanhamento-pelo-autor). Outras falhas ficam como erro de verificação. Nenhum campo de confirmação foi acrescentado ao contrato. O envio mantém a verificação e as rejeições da API existentes.

O cadastro acrescenta o aviso de senha exclusiva junto ao campo, associado por `aria-describedby`, mantendo os limites de 8–128 caracteres. A avaliação remove somente a instância de `FundoParticulas`; fundo líquido da conta, mapa da home e demais animações permanecem.

A revalidação de um visitante já verificado preserva formulário, preenchimento e foco até receber a resposta. Se a consulta falhar, apresenta o erro neutro. A revalidação de conta ativa não mantém a indicação de sessão ativa durante a consulta.

## Evidências visuais reproduzíveis

Capturas em Edge headless via CDP já usado no projeto, com HTTP controlado e dados sintéticos. Antes: `develop` em `9732096`. Depois: alterações da #237. Viewports de 1440, 768, 390 e 320 px, altura inicial 900 px, escala 1 e página completa. São larguras emuladas, não testes em aparelhos físicos. As partículas e o fundo líquido não ficam na mesma posição entre capturas por serem animados.

Cada célula reúne as cinco telas: conta ativa, cadastro, avaliação visitante, pendente e confirmada.

| Largura | Antes | Depois |
| --- | --- | --- |
| 1440 | [Conta](capturas/issue-237/antes/minha-conta-1440.png), [cadastro](capturas/issue-237/antes/senha-cadastro-1440.png), [visitante](capturas/issue-237/antes/avaliacao-visitante-1440.png), [pendente](capturas/issue-237/antes/avaliacao-pendente-1440.png), [confirmado](capturas/issue-237/antes/avaliacao-confirmado-1440.png) | [Conta](capturas/issue-237/depois/minha-conta-1440.png), [cadastro](capturas/issue-237/depois/senha-cadastro-1440.png), [visitante](capturas/issue-237/depois/avaliacao-visitante-1440.png), [pendente](capturas/issue-237/depois/avaliacao-pendente-1440.png), [confirmado](capturas/issue-237/depois/avaliacao-confirmado-1440.png) |
| 768 | [Conta](capturas/issue-237/antes/minha-conta-768.png), [cadastro](capturas/issue-237/antes/senha-cadastro-768.png), [visitante](capturas/issue-237/antes/avaliacao-visitante-768.png), [pendente](capturas/issue-237/antes/avaliacao-pendente-768.png), [confirmado](capturas/issue-237/antes/avaliacao-confirmado-768.png) | [Conta](capturas/issue-237/depois/minha-conta-768.png), [cadastro](capturas/issue-237/depois/senha-cadastro-768.png), [visitante](capturas/issue-237/depois/avaliacao-visitante-768.png), [pendente](capturas/issue-237/depois/avaliacao-pendente-768.png), [confirmado](capturas/issue-237/depois/avaliacao-confirmado-768.png) |
| 390 | [Conta](capturas/issue-237/antes/minha-conta-390.png), [cadastro](capturas/issue-237/antes/senha-cadastro-390.png), [visitante](capturas/issue-237/antes/avaliacao-visitante-390.png), [pendente](capturas/issue-237/antes/avaliacao-pendente-390.png), [confirmado](capturas/issue-237/antes/avaliacao-confirmado-390.png) | [Conta](capturas/issue-237/depois/minha-conta-390.png), [cadastro](capturas/issue-237/depois/senha-cadastro-390.png), [visitante](capturas/issue-237/depois/avaliacao-visitante-390.png), [pendente](capturas/issue-237/depois/avaliacao-pendente-390.png), [confirmado](capturas/issue-237/depois/avaliacao-confirmado-390.png) |
| 320 | [Conta](capturas/issue-237/antes/minha-conta-320.png), [cadastro](capturas/issue-237/antes/senha-cadastro-320.png), [visitante](capturas/issue-237/antes/avaliacao-visitante-320.png), [pendente](capturas/issue-237/antes/avaliacao-pendente-320.png), [confirmado](capturas/issue-237/antes/avaliacao-confirmado-320.png) | [Conta](capturas/issue-237/depois/minha-conta-320.png), [cadastro](capturas/issue-237/depois/senha-cadastro-320.png), [visitante](capturas/issue-237/depois/avaliacao-visitante-320.png), [pendente](capturas/issue-237/depois/avaliacao-pendente-320.png), [confirmado](capturas/issue-237/depois/avaliacao-confirmado-320.png) |

O teste `tests/conta-avaliacao-sessao-browser.mjs` integra `npm run test:browser`. `UI237_CAPTURAS=docs/capturas/issue-237` grava capturas; `UI237_ANTES=1 UI237_FRONTEND=<frontend anterior compilado>` permite registrar a base sem afirmar aprovação das correções nessa versão. Usa o navegador definido por `BROWSER_PATH` ou o Edge padrão do driver existente, sem instalar ferramentas.

## Validação local

- `npm run lint`, `npm run typecheck` e `npm run build`: passaram com Node Linux 24.14.1 localizado fora do PATH padrão.
- `npm run test:coverage`: 77 testes passaram, sem falhas. Cobertura de linhas/statements 18,79%, branches 75,31%, funções 49,12%; não é cobertura completa da interface.
- Os oito runners de `test:browser` passaram com execução direta pelo Node Windows: avaliação, moderação, denúncias, comentários, cabeçalho, identidades, transições e conta/avaliação da #237. O teste de comentários foi repetido após atualizar seu helper, que ainda aguardava o texto Entrar em conta ativa. Foram mantidas as asserções funcionais de troca de sessão e retorno.
- Verificador local dos links relativos deste relatório: 41 caminhos existentes, nenhum inexistente. `git diff --check`: sem erros.

O npm inicialmente encontrado era um shim Windows executado em caminho UNC, causando falhas de resolução de comandos. A tentativa de build Windows encontrou dependências nativas Linux incompatíveis. As dependências Linux preservadas foram restauradas e os comandos acima executados com o Node correspondente, sem mudar versões ou lockfile. Os testes de navegador usam Node Windows 24.14.1 e Edge existentes, com os mesmos arquivos do script `test:browser`, para manter servidor HTTP e navegador no mesmo ambiente.

Esta verificação técnica não conclui homologação integrada nem o reteste com alunos da #166. O merge permanece sujeito à revisão humana.
