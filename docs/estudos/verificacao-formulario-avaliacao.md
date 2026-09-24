# Verificação do formulário de avaliação — Issues #42 e #116

## Escopo e base

As descrições completas e os critérios de aceite das issues
[#42](https://github.com/unb-mds/2026-02-UnDb/issues/42) e
[#116](https://github.com/unb-mds/2026-02-UnDb/issues/116) foram lidos diretamente no GitHub.
A base `develop` foi sincronizada com `git pull --ff-only origin develop` em 23/09/2026:
`5e073377131d4918a25f642e71c648c424b7e8fd`, igual a `origin/develop` naquele momento.
Branch de trabalho: `feature/42-116-avaliacao-integrada`.

A #42 entrega a UI; a #116 conclui sessão, envio e persistência. As regras de produto e
as escalas de `specs.md` permanecem preservadas. O bloqueio temporário de envio foi
retirado na entrega integrada, verificada com formulário, API e PostgreSQL reais.

## Comportamento implementado

- Cinco critérios obrigatórios, sem respostas iniciais, labels associados, foco visível e
  controles nativos acessíveis pelo teclado.
- Sem comentário livre, histórico acadêmico ou comprovação de disciplina cursada.
  Dificuldade e Chamada mantêm apresentação neutra.
- Envio real para `POST /api/avaliacoes`, com cookie de sessão. O backend resolve o usuário
  pela sessão armazenada no servidor; o schema rejeita `usuario_id` e outros extras.
- Sessão ausente, inválida ou expirada: 401; conta não confirmada: 403; entradas inválidas:
  422. A interface orienta a correção e conserva as respostas, também em falhas de rede/5xx.
- Sucesso somente após confirmação da API. A abertura do login em outra aba evita perder
  o formulário preenchido durante a autenticação.
- Upsert atômico por `INSERT ... ON CONFLICT (usuario_id, professor_id, disciplina_id)
  DO UPDATE`, apoiado na constraint existente `uq_avaliacao_usuario_professor_disciplina`.
  Preserva `id`/`created_at`, substitui todos os critérios e atualiza `updated_at`.
  Não foi necessário alterar o schema nem criar migration.

## Correções de interface verificadas

| Problema | Correção |
|---|---|
| Indisponibilidade da API derrubava detalhes/comparação | Error boundary em português, preservando layout/navegação, com nova tentativa |
| Identificador malformado produzia erro genérico | Validação explícita de UUID antes da consulta nas quatro rotas de detalhe/formulário |
| Erro estruturado aparecia como objeto ou era descartado | Normalização de mensagens HTTP, mantendo detalhes e status originais |
| Domínio institucional em maiúsculas era rejeitado | Pattern case-insensitive e normalização no cadastro; domínio permitido preservado |
| Nome apenas com espaços produzia orientação enganosa | Trim, validação local, foco no campo e mensagem associada; 422 orienta correção |
| Confirmação confundia rede com token inválido | Distinção 400/422 versus falhas transitórias e botão de nova tentativa |
| Botões perdiam contraste no tema escuro | Token de texto sobre accent separado para os dois temas |

## Verificações locais

Ambiente: Windows, Node 24.21.0, Python 3.14, Edge headless e PostgreSQL 16 em container
isolado. O CI está configurado com Python 3.12, Node 22 e PostgreSQL 16.

- Backend: `python -m unittest discover -s tests -q` — 88 testes aprovados.
- PostgreSQL: `alembic upgrade head` e `alembic check` — migrations aplicadas; nenhuma
  diferença de schema detectada.
- Frontend: `npm test`, `npm run lint`, `npm run build` e `npm run test:browser`.
- Integração: `python -m tests.integration_avaliacao` usa Uvicorn e a aplicação sem
  dependency overrides, banco migrado e o build de produção do Next.
- O teste HTTP rejeita sessão ausente/inválida/expirada, e-mail não confirmado, identidade
  forjada, comentário, campos ausentes e valores fora das escalas sem gravar avaliação.
- Oito requisições simultâneas, com sessões distintas do mesmo usuário, produzem um único
  ID e uma única linha. Usar sessões distintas evita serialização artificial pela renovação
  de uma única sessão. Novo envio preserva ID/criação e substitui todos os critérios.
- O navegador executa criação e substituição e consulta o PostgreSQL por conexão separada
  para conferir ID, quantidade, identidade, critérios e datas. Login e confirmação por token
  usam os endpoints reais. Fixtures contêm apenas dados fictícios; não há envio de e-mail.
- Rejeição 422 usa corpo intencionalmente inválido e resposta da API real; falha de rede
  é induzida bloqueando o POST no navegador. Nenhuma resposta falsa comprova persistência.
- A suíte controlada verifica erros, recuperação, cadastro, confirmação e contraste.
  A UI é exercitada em 320/768/1280 px nos temas claro/escuro e com navegação por Tab.

## Reprodução e limites

Siga a seção de integração do `frontend/README.md`. O runner exige PostgreSQL de testes
migrado, `UNDB_INTEGRATION_TEST=1`, portas livres e Edge/Chrome. Ele cria e remove apenas
suas fixtures, sem criar schema nem apagar dados preexistentes. `--api-only` omite a UI.

O job `avaliacao-integrada` foi preparado no workflow, mas não executado remotamente:
esta entrega não inclui commit, push, PR, merge ou fechamento das issues.
A validação local não comprova implantação de produção, TLS, envio de e-mail externo,
Safari/Firefox, leitor de tela ou comportamento em carga de produção.
