# Verificação da interface de busca — #203

Data: 09/11/2026. Branch local: `feature/203-home-busca-unidades`. Base: `72227cc` de `origin/develop`, com a #202 integrada. Build webpack: `hU_GlBvQDXVKzVGS1Bbsk`. Ambiente: Windows, Node 24.18.0, Next 16.3.5, React 19.2.8 e dependências existentes do lockfile.

O [contrato da entrega](ui-busca-203.md) descreve componentes, rotas e integração com a #204. Fontes da verificação: critérios da #203, guia de referência versionado, contrato da #202, RF04–RF07 e continuidade da busca da #155.

## Checks

| Verificação | Resultado |
| --- | --- |
| `npm run lint` | Aprovado, sem avisos |
| `npm run typecheck` | Aprovado |
| `npm test` | 65 testes aprovados |
| `npm run test:coverage` | 65 testes aprovados; relatórios em `frontend/coverage/` |
| `npm run build` | Bloqueado por falha de ambiente do Turbopack; detalhes abaixo |
| `npm run build -- --webpack` | Aprovado, incluindo TypeScript e geração das rotas |
| `npm run test:browser` | Aprovado nas quatro suítes: avaliação/busca/protótipo, moderação, denúncias/agradecimentos e comentários |
| `git diff --check` | Aprovado |

No sandbox, o build padrão não conseguiu baixar Geist/Geist Mono. A execução com rede permitida ultrapassou esse ponto e encontrou falha interna do Turbopack ao criar o processo de transformação de CSS (`node process exited before we could connect to it`). O build webpack, alternativa já usada na verificação da #202, passou com as mesmas dependências e configurações. Não foram alterados scripts, fontes, lockfile ou CI para contornar o ambiente. O compilador padrão ainda depende de confirmação no CI.

## Cenários da área

`tests/busca-browser.mjs`, integrado ao runner de avaliação existente, verifica:

- envio direto da home nas duas modalidades, inclusive com scripts bloqueados, preservando caracteres especiais no termo;
- ordenação local por nome/unidade sem nova requisição, histórico, consulta, retorno e recarga com `q`, modalidade e `ordem`;
- estados inicial, carregando, termo inexistente, erro e nova tentativa; resposta antiga não substitui a pesquisa atual;
- catálogo da home e unidades vindos da API, filtro por unidade na URL, recarga, voltar/avançar e unidade inexistente;
- catálogo vazio, indisponível e recuperação, tanto na home quanto em `/departamentos`;
- dois professores homônimos com IDs e unidades distintos, disciplinas e links Consultar/Avaliar vinculados a cada ID;
- recuperação de erro ao carregar disciplinas de um professor;
- foco visível por Tab nos controles de busca, além das regressões existentes de acesso e senha;
- 320, 390, 768, 1280 e 1440 px, com ambas as preferências de tema do sistema e a aplicação em dark fixo; ausência de transbordamento horizontal.

Os testes nativos também verificam o endpoint público sem filtros para o catálogo, preservação de disciplinas homônimas por ID, nomes institucionais sem fusão por aproximação, ordem e codificação reversível da URL de unidade.

A execução completa também aprovou as 72 combinações do protótipo histórico, os estados e ações de moderação, permissões de denúncia/agradecimentos e publicação/substituição/retirada de comentários. As capturas da área foram produzidas pelo build final identificado acima.

## Ajustes dos testes existentes

A grade acompanha a apresentação autorizada: professores em uma coluna, disciplinas em uma/duas/três colunas. O teste de teclado da consulta real passa pelo novo botão Consultar antes de Avaliar; mantém a asserção de foco visível na avaliação. O código da disciplina conserva o rótulo explícito usado nas verificações de integração.

Foi reproduzido e isolado um timeout do cenário de cadastro antes da hidratação: a interceptação de todos os scripts também atrasava um script inserido pelo antivírus local, bloqueando o parser antes de existir `body`. A interceptação agora se limita a `http://localhost:3100/_next/*`. As asserções de ausência de validação/envio antes da hidratação, nome em branco e recuperação continuam presentes. O cenário isolado completo passou após esse ajuste. O arquivo temporário de diagnóstico foi removido.

## Evidências visuais e limites

As capturas foram geradas com `PREVIEW_DIR` apontando para um diretório de artefatos fora do repositório. Padrões: `155-203-entrada-*`, `155-203-professores-*`, `155-203-disciplinas-*` e `155-203-unidades-*`. Home, resultados de professor e unidade selecionada foram inspecionados visualmente em 320 e 1440 px; os resultados de disciplina também em 320 px. Os dados das capturas são fixtures HTTP identificadas como teste; não representam opiniões ou estatísticas de docentes reais.

Quatro evidências do build final estão versionadas para revisão no PR:

| Tela com dados de teste | Desktop (1440 px) | Celular (320 px) |
| --- | --- | --- |
| Home | [Captura](capturas/issue-203/home-1440.png) | [Captura](capturas/issue-203/home-320.png) |
| Resultados de professor | [Captura](capturas/issue-203/professores-1440.png) | [Captura](capturas/issue-203/professores-320.png) |

Os testes de navegador usam API controlada e viewport emulado. A integração FastAPI/PostgreSQL real e o reteste com alunos da #166 não foram executados nesta tarefa. `tests/resultados-browser.mjs` foi adaptado à nova sequência de foco e validado sintaticamente; seu runner com banco isolado permanece não executado. Não houve alteração de backend, modelo de dados, autenticação, permissões ou infraestrutura de produção.

A revisão local confrontou o diff e os componentes novos com as fontes acima e os contratos existentes, sem findings confirmados pendentes no escopo inspecionado. A integração em `develop` depende dos checks remotos e da revisão humana exigida em `CONTRIBUTING.md`.
