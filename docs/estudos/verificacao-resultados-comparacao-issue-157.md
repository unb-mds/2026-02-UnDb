# Verificação das rotas reais de resultados e comparação — Issue #157

Execução em 26/10/2026. Correções locais na branch `feature/157-resultados-comparacao`,
sobre `e04122a6e115639d33e86a047a2d4ab67296f745`, da
[PR #183](https://github.com/unb-mds/2026-02-UnDb/pull/183).

## Escopo e fontes

A [issue #157](https://github.com/unb-mds/2026-02-UnDb/issues/157) pede disciplinas
agrupadas por professor nos resultados, identidade por ID, rótulos claros, ações
de comparar/avaliar e verificação das rotas reais em desktop/celular e claro/escuro.
O [mapa do protótipo](ajustes-prototipo-jornada-issue-153.md) e o
[reteste](resultados-reteste-jornada-issue-153.md) explicam essa apresentação.
[RF05–RF13 e RNF02](../requisitos.md) e os ADRs 05/07 em
[arquitetura](../arquitetura.md) sustentam consulta pública, identidade, ordenação
por recomendação e ocultação dos critérios abaixo de três avaliações.

Foram alterados somente a apresentação dos resultados por professor e o componente
de disciplinas reutilizado pelo detalhe. Busca, debounce, ordenação das listagens,
serviços HTTP, autenticação, agregação e schema foram preservados. O trabalho de
busca/retorno da #155 e o formulário da #158 continuam com seus escopos próprios.

## Implementação

- `frontend/src/app/professores/professor-resultado.tsx` consulta disciplinas pelo
  ID do professor e trata carregamento, sucesso e falha de forma independente.
  O resultado permanece visível quando a consulta complementar falha. Respostas
  de componentes desmontados são descartadas.
- `frontend/src/components/disciplinas-professor.tsx` apresenta nome, código,
  unidade e ações de consulta/comparação/avaliação. É usado na busca e no detalhe,
  preservando IDs nos links e permitindo quebra de texto e das ações em 320 px.
- A API existente fornece as disciplinas ativas sem duplicar a matéria quando
  o professor possui mais de uma turma. Nomes iguais não são usados como chave.

## Ambiente e dados

Windows, Node.js 24.18.0, Next.js 16.3.5, React 19.2.8 e Edge 156.0.4314.42 headless.
Backend em Python 3.12.14 na imagem local existente, com o código desta branch
montado somente para leitura. PostgreSQL 16.15 em projeto Docker isolado `undb-pr183`, com migrations
Alembic até `20260921_01`. A API recebeu requisições HTTP reais em `localhost:8000`;
o frontend foi servido pelo build de produção em `localhost:3100`.

`backend/tests/seed_resultados.py` exige `UNDB_INTEGRATION_TEST=1`, PostgreSQL e
banco vazio. Prepara sete professores, incluindo duas Anas com IDs/unidades
distintos e um professor sem turma ativa; duas disciplinas de nomes longos;
oito turmas e quatro contas sintéticas sem login. Os agregados da primeira
disciplina têm contagens 4/3/3/4/2/0, percentuais 100/100/100/50 e conflito factual.
Todos os valores apresentados são calculados pela API a partir das avaliações
persistidas, sem respostas simuladas no navegador.

## Resultados

| Verificação | Resultado observado |
|---|---|
| `npm run lint` | Passou. |
| `npm test` | 19 testes passaram. |
| `npm run build` | Inconclusivo para o produto: primeiro falhou na rede das fontes Geist; com rede liberada, Turbopack falhou ao iniciar o processo de CSS. |
| `npm run build -- --webpack` | Passou: compilação, TypeScript, geração de rotas e build de produção. |
| `python -m unittest discover -s tests -v` no backend | 99 testes passaram. |
| `node tests/resultados-browser.mjs` | Passou: 48 combinações, navegação e cenários adicionais abaixo. |
| `npm run test:browser` | Falhou em duas execuções com `Timeout: cadastro`, no cenário existente de scripts de hidratação bloqueados. A suíte geral não foi declarada aprovada. |

Uma execução adicional de diagnóstico, sem alteração permanente do runner,
mostrou `/cadastro` com `document.readyState = "loading"`, apenas um script no
DOM e sem o campo `nome`, enquanto o cenário mantinha os scripts bloqueados.
O HTML gerado pelo build contém o formulário. Não foi estabelecida relação causal
com a correção dos resultados nem confirmado defeito no cadastro; esse cenário
permanece não verificado no ambiente local Edge/Webpack. O cadastro, seu layout
e o runner existente foram preservados.

O runner verificou oito telas/estados × larguras 320/768/1280 px × temas claro/escuro:
busca de professores, busca de disciplinas, detalhe do professor, comparação,
agregado suficiente, agregado insuficiente, ausência de avaliações e ausência de turmas.

- Os sete professores permanecem separados; as duas Anas mantêm seus conjuntos
  de disciplinas. A Ana com duas turmas da mesma matéria a mostra uma só vez.
- Código e unidade aparecem com rótulos; os links preservam professor e disciplina.
  Os atalhos Avaliar e Comparar foram acionados e chegaram às rotas esperadas.
- Comparação preserva recomendação, desempate por quantidade e nome. A ordem
  recebida da API corresponde à exibida; conflito e contagens permanecem visíveis.
- Com duas ou zero avaliações, não aparecem percentuais nem critérios, tanto na
  comparação quanto na consulta agregada.
- Nenhuma combinação apresentou rolagem horizontal. A comparação tem uma coluna
  em 320 px e duas em 768/1280 px. Os atalhos Avaliar na busca e no detalhe foram
  alcançados por Tab com foco visível.
- Uma falha de transporte foi induzida em uma consulta de disciplinas usando o
  bloqueio de rede do navegador, sem fabricar resposta HTTP: o professor continua
  visível com mensagem de erro e os demais cartões carregam normalmente.
- A busca sem correspondência informa ausência de resultado. Nenhuma exceção de
  execução foi registrada pelo navegador durante o teste.

## Evidências

O [resultado estruturado](evidencias/issue-157/resultado.json) lista as 48 combinações.
Foram salvas 16 capturas, em desktop claro e celular escuro, cobrindo os oito estados.
As seguintes capturas foram inspecionadas visualmente quanto à legibilidade e quebra
de texto, além das verificações automáticas de largura e foco:

- [Busca de professores, celular escuro](evidencias/issue-157/busca-professores-dark-320.png).
- [Busca de disciplinas, celular escuro](evidencias/issue-157/busca-disciplinas-dark-320.png).
- [Detalhe do professor, celular escuro](evidencias/issue-157/detalhe-professor-dark-320.png).
- [Agregado, celular escuro](evidencias/issue-157/agregado-dark-320.png).
- [Comparação, celular escuro](evidencias/issue-157/comparacao-dark-320.png).
- [Comparação, desktop claro](evidencias/issue-157/comparacao-light-1280.png).

## Reprodução

Use exclusivamente um PostgreSQL vazio de testes com as migrations aplicadas.
Não execute a preparação na base de desenvolvimento com dados institucionais.
A API precisa usar esse mesmo banco e aceitar CORS de `http://localhost:3100`.

Exemplo em PowerShell, a partir da raiz, após iniciar o banco/API isolados. O
container `undb-pr183-api` deve usar o código atual de `backend/` em `/app`,
incluindo `tests/`. `fixture.json` é um artefato local que contém somente os IDs
e textos sintéticos para o runner; mantenha-o fora dos arquivos versionados.

```powershell
$taskFixture = Join-Path $env:TEMP 'undb-pr183-fixture.json'
docker exec -e UNDB_INTEGRATION_TEST=1 undb-pr183-api python -m tests.seed_resultados |
  Set-Content -Encoding utf8 $taskFixture
if ($LASTEXITCODE -ne 0) { throw 'A preparação da base de testes falhou.' }

Set-Location frontend
npm.cmd run lint
npm.cmd test
npm.cmd run build -- --webpack
$env:RESULTADOS_FIXTURE_FILE = $taskFixture
$env:PREVIEW_DIR = Join-Path $PWD '../docs/estudos/evidencias/issue-157'
node tests/resultados-browser.mjs
```

O runner inicia e encerra seu próprio Next.js/Edge, recusa portas ocupadas e remove
apenas seu perfil temporário. Para repetir, reutilize o manifesto e a base
preparada; o seed recusa banco não vazio. Encerre somente os containers e volume
descartáveis criados para essa execução ao terminar.

## Limites

A evidência é de rotas reais com FastAPI/PostgreSQL e dados sintéticos persistidos;
não é uma nova coleta do SIGAA nem validação qualitativa com alunos ou dispositivos
físicos. O viewport móvel é emulado. Na verificação da #157, não foram feitos envios
de avaliação, login ou confirmação de e-mail: o teste chega ao formulário da versão
da #183, preservando a separação da #184. Leitura por leitor de tela não foi testada.

As lacunas específicas de agrupamento e evidências de API identificadas na revisão
foram tratadas localmente. A validação das rotas da #157 passou; a suíte geral
permanece com o timeout documentado acima. A publicação dessas alterações e a
aprovação humana da PR são etapas posteriores. Os containers e o volume de
testes `undb-pr183` foram removidos após a coleta das evidências.
