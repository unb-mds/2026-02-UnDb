# Auditoria de commits, pendências e documentação — PR #248

## Escopo e fontes

Auditoria iniciada com checkout limpo em `feature/247-telas-conta-confirmacao-moderacao`,
HEAD local/remoto `3d04b907205c4d1404174db7bd04fd47bda7b2d2`, base `develop`
`18c04c445bed813948a6ed64f0fbcdc8a33c4bb7`. Após `git fetch origin`: **0/0** em relação
à branch remota e **8/0** em relação à base. A PR estava aberta, em Draft e sem merge.

Fontes consultadas:

- [Issue #247](https://github.com/unb-mds/2026-02-UnDb/issues/247), descrição e comentários
  (nenhum comentário na issue no momento da consulta).
- [PR #248](https://github.com/unb-mds/2026-02-UnDb/pull/248), descrição, discussão,
  revisões e eventos, incluindo o force-push de Nicolas.
- [Solicitação de Nicolas para o preview](https://github.com/unb-mds/2026-02-UnDb/pull/248#issuecomment-6887546724)
  e [registro do envio da implementação](https://github.com/unb-mds/2026-02-UnDb/pull/248#issuecomment-6887638249).
- [Guia das seis telas](../referencias/telas-jornada-247/README.md),
  [roteiro do preview](../referencias/preview-compartilhamento/README.md), diffs,
  objetos Git, reflog remoto e resolução de conflitos de `3d04b90`.
- [Execução de Documentation Pages que falhou](https://github.com/unb-mds/2026-02-UnDb/actions/runs/43665548670),
  job `132663980966`, e workflow `.github/workflows/pages.yml`.

O conector forneceu descrições, discussões/revisões e logs do Actions. Como não expõe
os eventos de force-push com o hash anterior, a timeline REST/GraphQL foi consultada
por `gh api`, somente em leitura. Comentários dos commits `0ff2591`, `d8e13aa` e
`51a7317` estavam vazios. Não foram encontradas outras solicitações atribuíveis a
Nicolas nessas fontes, nem uma revisão humana publicada da implementação.

## Histórico e preservação

Horários abaixo em America/Sao_Paulo, 14/11/2026. Ordem por data de autoria; a ordem
do grafo difere porque houve desenvolvimento local paralelo e consolidação remota.

| Commit | Autor / horário | Conteúdo e situação |
| --- | --- | --- |
| `0ff2591` | Nicolas, 18:53:51 | Guia das seis telas, seis PNGs originais e link no README do frontend. Presente no histórico atual. |
| `211d982` | Vinicius, 22:44:16 | Login/cadastro e componentes de conta. Presente. |
| `ec5aff9` | Vinicius, 22:44:19 | Confirmação e resultado contextual da avaliação. Presente. |
| `852137a` | Vinicius, 22:44:22 | 404 e moderação. Presente. |
| `24def2b` | Vinicius, 22:44:24 | LinkedIn somente no registro de Vinicius. Presente. |
| `f0c8f1c` | Vinicius, 22:45:48 | Runner, relatório e 36 capturas. Presente. |
| `d8e13aa` | Nicolas, 22:49:51 | PNG e roteiro do preview, filho de `0ff2591`. Commit substituído na consolidação; árvore preservada integralmente. |
| `51a7317` | Nicolas, 22:51:44 | Consolidação dos dois commits documentais. Force-push registrado às 22:51:57. Presente. |
| `3d04b90` | Vinicius, 22:58:03 | Concilia `f0c8f1c` e `51a7317`, preservando ambos os históricos. Presente. |

O evento GraphQL `HeadRefForcePushedEvent` identificou `d8e13aa8b8bb535a0fcdbf250faecb177c5026ad`
como o head anterior e `51a7317d6160f971c54b214ed5ee2a2d75a6c811` como o posterior.
O commit anterior foi buscado individualmente, sem alterar branches. A comparação
`git diff --exit-code d8e13aa 51a7317` passou: ambas as árvores têm ID
`cbbb176a568bb0f93e8d4ea645f67df0be927d54`. A ausência de `d8e13aa` na ancestralidade
atual, portanto, **não significa perda de conteúdo**.

Também foram verificadas as seguintes propriedades:

- `git diff 0ff2591 51a7317` lista somente os dois arquivos de preview acrescentados.
- `git diff f0c8f1c 3d04b90` lista somente esses mesmos dois arquivos. Não há alteração
  de código do frontend ou dos cinco commits de implementação causada pela conciliação.
- Os seis PNGs de referência têm blobs Git idênticos em `0ff2591`, `51a7317` e `3d04b90`.
- O guia e o PNG do preview são idênticos entre `51a7317` e `3d04b90`.
- `git show --remerge-diff 3d04b90` confirma conflitos apenas em
  `docs/referencias/telas-jornada-247/README.md` e `frontend/README.md`. A resolução
  preservou as atualizações de implementação de `f0c8f1c`, em lugar do texto anterior
  que dizia haver somente documentação. As referências e instruções técnicas foram mantidas.
- Não há arquivos removidos no diff original da PR contra `develop`, nem commits da
  base ou da branch remota atual aguardando integração no início desta auditoria.

**Conclusão sobre perda:** nenhuma perda de código, arte ou orientação de Nicolas
foi comprovada. Nenhuma funcionalidade precisou ser recuperada de um commit antigo.
O preview era uma **pendência explícita**, não uma implementação apagada pelo merge.

## Pedidos e critérios: classificação

| Categoria | Pedido / resultado encontrado | Evidência e encaminhamento |
| --- | --- | --- |
| Concluído, verificação local | Seis telas, estados reais, retorno seguro, confirmação sem sessão automática e sucesso após API | Código dos cinco commits de Vinicius e regressões de navegador. O aceite visual humano não é inferido desses testes. |
| Concluído | Preservar logo oficial, capturas e arte final | Blobs das seis referências e do PNG preservados; ícones e bytes da imagem pública verificados no teste novo. |
| Concluído | Conciliar o histórico antes do envio | `3d04b90` contém `51a7317` e `f0c8f1c`; nenhum force-push feito pela continuidade. |
| Concluído nesta tarefa, localmente | Disponibilizar PNG e configurar Open Graph/Twitter Card | Solicitação de Nicolas no comentário e roteiro de `51a7317`. Antes da auditoria não havia `frontend/public/undb-preview.png`, `metadataBase`, `openGraph` ou `twitter` no layout. Agora implementados e verificados no HTML inicial. |
| Pendente | PNG público por HTTPS, HTML após deploy e compartilhamento real no WhatsApp com captura | Exige publicação da versão e teste externo posterior. Não foi realizado deploy nem envio de mensagem nesta auditoria. |
| Pendente | Integração real FastAPI/PostgreSQL e confirmação institucional | Já registrada na PR e no relatório anterior. Os runners HTTP controlados não comprovam persistência nem entrega de e-mail. |
| Pendente, humano | Aceite visual do PO, revisão técnica independente e reteste com alunos da #166 | Não há evidência suficiente para marcar esses itens como aceitos. Nenhuma aprovação/revisão da PR foi publicada por esta tarefa. |
| Pendente, humano | Avaliação das skills de segurança/incidentes da #240 | O guia pede avaliação humana. Metadados permanecem `proposed`; nenhuma promoção foi realizada. |
| Possível perda/regressão investigada: não confirmada | Commit `d8e13aa` ausente do grafo atual | A árvore é idêntica a `51a7317`; nenhum arquivo a recuperar. |
| Problema documental confirmado e corrigido | Links quebrados no site MkDocs | Cinco destinos fora de `docs/` já no guia de `0ff2591`; o link do relatório foi acrescentado em `f0c8f1c`, totalizando seis. Todos existem no Git, mas não no conjunto publicado pelo MkDocs. |

Os critérios visuais foram implementados como adaptações funcionais: o contrato da
moderação não fornece professor/disciplina por item nem ação manual de suspensão.
Esses elementos ilustrativos não foram inventados; operações, permissões e privacidade
existentes foram preservadas. Recuperação de senha continua fora do escopo.

## Correção do MkDocs

`mkdocs.yml` não sobrescreve `docs_dir`; a configuração carregada resolve para `docs/`.
O CI executa `mkdocs build --strict --site-dir site` em Documentation Pages, não na
checagem da nomenclatura de branches do Gitflow. O log remoto termina com
`Aborted with 6 warnings in strict mode!`. A mesma falha foi reproduzida localmente
antes de alterar os links.

Todos os seis destinos existem no repositório. O erro ocorre porque os caminhos
relativos sobem para fora de `docs/`, e MkDocs só resolve links locais entre arquivos
do conjunto documental. Não é uma perda causada pela consolidação dos commits.

Correções limitadas ao guia das telas:

- `frontend/docs/jornada-247.md`: link GitHub fixado no commit `f0c8f1c`, que contém o
  relatório e as 36 evidências daquela implementação.
- `specs.md` e as quatro skills: links GitHub em `blob/develop`, conforme as convenções
  já usadas em `docs/visao.md`, `docs/adrs/index.md`, `docs/adrs/09-estrategia-qualidade.md`
  e estudos. A existência dos destinos nessa ref foi conferida com `git cat-file -e`.
- Requisitos e capturas dentro de `docs/` continuam com links relativos.

Nenhuma referência foi removida, nenhum documento fictício/cópia foi criado para
contornar a validação. Não foram alterados `mkdocs.yml`, o workflow ou
`requirements-docs.txt`. O arquivo público de preview é a cópia expressamente pedida
por Nicolas para o frontend, não uma duplicação para o MkDocs.

As 24 páginas originalmente fora do `nav` foram identificadas por caminho e título: estudos de
execuções específicas e referências de design/implementação, incluindo snapshots.
Não foi encontrada orientação para promovê-las à navegação principal. Continuam
geradas e acessíveis por links/busca; o novo relatório é ligado pelos guias pertinentes.
O `nav` foi preservado. A mensagem de fim de vida do Material e a lista de páginas
fora da navegação são avisos informativos distintos dos seis warnings de links.
`NO_MKDOCS_2_WARNING` não foi configurada.

## Preview implementado

- Arte copiada byte a byte para `frontend/public/undb-preview.png`.
- SHA-256 original/público: `e9db6db9d01444dbac392c7a684b7f136103228f52fc1876b32ffd31652f1610`.
- Metadados compartilhados tipados em `frontend/src/lib/metadados-compartilhamento.ts`,
  reutilizados por layout, home e Sobre. `metadataBase`, textos solicitados, imagem
  absoluta, dimensões, tipo, alt, locale, siteName e `summary_large_image` configurados.
- `og:url` da home fica somente em sua página; Sobre usa sua URL e seus próprios título
  e descrição. Outra rota não herda a URL da home. Os títulos e `robots` de moderação,
  logo/favicon e dados da equipe não foram alterados.
- Novo runner `frontend/tests/preview-compartilhamento-browser.mjs`, integrado ao
  `test:browser`: verifica o HTML inicial sem executar scripts da página, URLs,
  duplicatas, imagem HTTP 200/image/png, dimensões, bytes originais, títulos específicos,
  robots e ícones. Usa o servidor de produção e o mecanismo Node/CDP já disponível.

## Verificações e limites

Ambiente local: Windows, Python 3.14, Node 24.21.0, Edge headless. O CI usa Python
3.12. Foram instaladas apenas as dependências documentais já previstas, em ambiente
virtual ignorado, sem alterar arquivos de requisitos: MkDocs 1.6.1 e Material 9.8.1,
mesmas versões principais observadas no log remoto.

| Verificação | Resultado observado |
| --- | --- |
| `mkdocs build --strict --site-dir site` antes | Falhou com os mesmos seis warnings do CI. |
| Mesmo comando após corrigir os links | Passou sem warnings de links; EOL e páginas fora do nav continuam visíveis. |
| `npm run lint` | Passou. |
| `npm run typecheck` | Passou. |
| `npm run test:coverage` | 79/79 testes, sem falhas. |
| `npm run build` | Passou, produção com Turbopack. |
| `node tests/preview-compartilhamento-browser.mjs` | Passou: HTML inicial e PNG reais do servidor local, sem mocks de metadados. |
| `npm run test:browser` | Os dez runners passaram: avaliação/busca/catálogo/protótipo, moderação, denúncia, comentários, cabeçalho, identidades, transições, #237, #247 e preview. |

O teste novo inicialmente esperava uma barra final literal em `og:url`; o Next
normaliza a origem para `https://undb.app.br`. A asserção foi corrigida para comparar
URLs normalizadas, mantendo caminho/query e exigindo uma única tag. Não houve
alteração de teste anterior nem ocultação de falha do produto.

Não existe script de formatação no frontend; não foi introduzido formatador. A suíte
de cobertura mede linhas/statements **18,77%**, branches **74,34%** e funções **48,87%**,
sem representar cobertura completa da UI. A produção HTTPS, o WhatsApp e a integração
FastAPI/PostgreSQL não foram validados nesta tarefa. Não foram solicitados novos checks
remotos sobre commits que ainda não foram enviados.

## Entrega e autorização

Somente novos commits locais, separados entre correção documental, implementação do
preview e registro da auditoria. Histórico/autoria existentes preservados. Nenhum
reset, rebase, force-push, novo merge, push, nova PR, mudança de base, fechamento da
issue ou retirada de Draft realizado nesta tarefa. Publicação dos novos commits
depende de autorização explícita do solicitante.

- `d59993e` — corrige exclusivamente os seis links fora de `docs/`, sem alterar o nav ou o workflow.
- `dae2393` — implementa o preview com a arte original, metadados reutilizáveis e teste do HTML inicial, integrado ao script existente.
- Commit documental final — este relatório, a ligação pelos guias e a atualização do estado de implementação do preview.
