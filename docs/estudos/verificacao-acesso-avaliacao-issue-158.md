# Acesso real e retorno à avaliação — Issue #158

Verificação em 26/10/2026, com alterações locais na branch
`feature/158-formulario-acesso-avaliacao`, sobre
`bf010d7c87c72abbc616928d4388204106e52b19` da
[PR #184](https://github.com/unb-mds/2026-02-UnDb/pull/184).

O commit remoto `bf010d7`, publicado durante o trabalho local, foi integrado antes
da entrega. Foi mantida sua passagem pelo login após confirmar o e-mail e seus
cenários adicionais de retorno/envio, adaptando o contexto compartilhado à
preservação independente por link. A jornada real e o build foram repetidos
depois dessa integração.

## Objetivo e fontes

Corrigir a perda/troca do retorno à avaliação entre abas e verificar pelas telas
reais o percurso cadastro → confirmação → login → avaliação, conforme a
[issue #158](https://github.com/unb-mds/2026-02-UnDb/issues/158), RF01/RF02/RF14
em [requisitos](../requisitos.md), ADR 03 em [arquitetura](../arquitetura.md) e
o contrato de autenticação em [specs.md](../../specs.md).

A chave única `undb:retorno-avaliacao` de `localStorage` permitia que outra aba
apagasse ou substituísse o destino de uma confirmação em andamento. A correção
transporta o contexto em cada link: login/cadastro recebem `returnTo`, o cadastro
envia o campo opcional `return_to` e o backend o inclui no link de confirmação.
O frontend valida novamente o destino antes de apresentar a ação de retorno.

Somente `/professores/{UUID}/disciplinas/{UUID}/avaliar` é aceito, sem origem,
query ou fragmento. A chave antiga não é mais lida ou gravada. Não houve alteração
do modelo de dados, das escalas, dos tokens, do contrato de sessão nem armazenamento
de respostas entre rotas. Cadastros sem destino e links antigos continuam válidos.

## Ambiente e execução

- Windows, Node.js 24.18.0 e Edge 156.0.4314.42 headless.
- Next.js 16.3.5/React 19.2.8, build de produção com Webpack, servido em
  `http://localhost:3100`.
- FastAPI/Python 3.12.14 em container com o código atual montado somente para
  leitura, API em `http://localhost:8000`, CORS para a origem do frontend.
- PostgreSQL 16.15 isolado pelo projeto Docker `undb-pr184`, com migrations
  Alembic até `20260921_01`.
- `EMAIL_BACKEND=console` e `FRONTEND_URL=http://localhost:3100`, conforme o
  modo de confirmação local já previsto. Não houve envio externo de e-mail.

`backend/tests/integration_acesso.py` preparou somente dois professores, uma
disciplina, unidade e turmas sintéticas, sem criar usuários. Os dois usuários
foram cadastrados pelas telas e pela API. O navegador leu os links efetivamente
emitidos pelo adaptador console; não gerou tokens, não marcou contas confirmadas
diretamente e não substituiu respostas HTTP.

## Resultados

| Verificação | Resultado observado |
|---|---|
| `npm run lint` | Passou. |
| `npm test` | 20 testes passaram, incluindo retorno interno válido e rejeição de destinos inválidos. |
| `python -m unittest discover -s tests -q` | 101 testes passaram; incluem validação do destino e link real do serviço sem criação automática de sessão. |
| `npm run build` | Falhou no ambiente local: Turbopack não conseguiu iniciar o processo de CSS. |
| `npm run build -- --webpack` | Passou, incluindo TypeScript e geração das rotas. |
| `node tests/acesso-browser.mjs` | Passou: jornada real completa, dois contextos independentes, persistência e 36 combinações visuais. |
| `npm run test:browser` | Falhou com `Timeout: cadastro` no cenário existente que bloqueia os scripts de hidratação. A suíte geral com API controlada não foi declarada aprovada no ambiente local Edge/Webpack. |

A primeira execução da jornada parou em um timeout de captura de tela. O runner
passou a ativar explicitamente a aba antes de navegar/capturar e aguardar a pintura
após trocar o viewport. Com novas fixtures, a execução completa passou. Esse ajuste
afeta apenas o controle do navegador de testes.

O [resultado estruturado](evidencias/issue-158/resultado.json) contém as combinações
e os cenários aprovados, sem credenciais ou tokens. Foram verificados:

1. Entrada na avaliação A → link de login → link de cadastro, preservando o destino.
2. Dois cadastros reais em abas distintas. Cada link de confirmação contém o
   destino do respectivo cadastro. Uma visita genérica a `/login` em outra aba
   não modifica o link nem o retorno de A.
3. Após cadastro, os dois usuários existem sem confirmação, sem sessão e sem
   avaliações. Login com senha incorreta não cria sessão.
4. Login real da conta A ainda não confirmada retorna a A. O cookie recebido é
   `HttpOnly` e `SameSite=Lax`. O envio antes da confirmação é rejeitado com a
   orientação correspondente e mantém as respostas, sem gravar avaliação.
5. Abertura do link real de A confirma somente A. B continua pendente. A ação
   “Continuar para a avaliação” passa pelo login com o destino de A; a sessão
   existente retorna ao professor/disciplina de A sem pedir a senha novamente.
6. Avaliação A confirmada é enviada e gravada. Acesso ao login com sessão ativa
   retorna diretamente à avaliação. Logout invalida a sessão.
7. O link de B funciona em outra aba e sem sessão. Depois da confirmação, a ação
   de continuar abre o login com o destino de B, exige suas credenciais e retorna
   a B, permitindo registrar sua avaliação.
8. O PostgreSQL contém exatamente duas avaliações desses usuários, cada uma no
   destino correto, com Didática 2, Chamada/Material/Recomendação negativas. Os
   dois tokens estão consumidos e os dois e-mails confirmados.
9. Reabrir o token consumido informa link inválido/expirado e não oferece a ação
   de continuar para a avaliação.
10. Didática inicia sem seleção; setas selecionam a nota e Tab alcança Dificuldade
    com foco visível. Login, cadastro, e-mail pendente, confirmação, formulário e
    sucesso foram verificados em 320/768/1280 px e temas claro/escuro, sem rolagem
    horizontal: seis telas/estados × três larguras × dois temas = 36 combinações.

## Capturas e inspeção visual

Foram salvas 12 capturas, uma versão desktop clara e uma móvel escura de cada
tela/estado. Foram inspecionadas visualmente, além das verificações automáticas:

- [Login móvel](evidencias/issue-158/login-dark-320.png).
- [Cadastro móvel](evidencias/issue-158/cadastro-dark-320.png).
- [Confirmação móvel](evidencias/issue-158/confirmacao-dark-320.png).
- [Formulário móvel com foco](evidencias/issue-158/formulario-dark-320.png).

As capturas mostram as rotas reais e dados sintéticos. O viewport móvel é emulado;
não houve validação qualitativa com alunos, dispositivos físicos nem leitor de tela.
O adaptador console é o modo de e-mail local previsto; entrega em caixa postal real
permanece fora dessa verificação. A retenção de rascunhos entre rotas continua fora
do escopo, conforme a issue.

O timeout da suíte geral não ocorreu na jornada real acima: cadastro, confirmação
e login foram exercitados com a API real e passaram. O cenário separado de
hidratação artificialmente atrasada permanece inconclusivo para esse ambiente;
não foi alterado para contornar o bloqueio. Os resultados do CI da nova versão
ainda precisam ser observados depois da publicação.

## Reprodução e CI

Com as dependências instaladas, configure um banco PostgreSQL exclusivo de testes,
`SECRET_KEY` e `DATABASE_URL`; aplique as migrations e gere o build de produção em
`frontend/`. Tenha Node 22+ e Edge/Chromium acessíveis, com `BROWSER_PATH` definido
quando necessário. As portas 8000/3100/9225 devem estar livres.

Em `backend/`:

```powershell
$env:UNDB_INTEGRATION_TEST = '1'
$env:PREVIEW_DIR = Join-Path $PWD '../docs/estudos/evidencias/issue-158'
python -m tests.integration_acesso
```

O driver prepara seus próprios dados, inicia a API real com o adaptador console,
invoca `frontend/tests/acesso-browser.mjs` e encerra API/Next.js/navegador ao final.
O Node inspeciona o banco por `--inspect`; a limpeza remove somente as fixtures.
Sem `PREVIEW_DIR`, as verificações continuam sem salvar capturas.

Na execução local com Docker foram usados os modos `--prepare`, `--inspect` e
`--cleanup`, `E2E_ACESSO_CONTAINER=undb-pr184-api` e
`E2E_ACESSO_FIXTURE_FILE` apontando para um manifesto temporário fora do Git. O
mesmo código de preparação e inspeção é usado pelo driver completo do CI.

O workflow existente `Evaluation end to end (PostgreSQL)` passa a executar
`python -m tests.integration_acesso` depois da integração de avaliações. Essa
alteração será exercitada remotamente quando publicada. A limpeza local foi
verificada com usuários/avaliações vazios; os containers, rede e volume
descartáveis `undb-pr184` foram removidos após a coleta das evidências.
