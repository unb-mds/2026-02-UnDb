# Interface de comentários — Issue #159

**Estado:** fluxos RF20 implementados para revisão e aceite; merge e homologação da #163 pendentes.
**Base da revisão:** `b9f0416` (PR #197), sobre `develop` em `78dfa46`.
**Fontes:** [RF20 e decisões R2-DEC](../requisitos.md),
[contratos das APIs](alinhamento-denuncias-issues-160-161.md) e [Issue #159](https://github.com/unb-mds/2026-02-UnDb/issues/159).

## Entrega e correções

- A rota `/professores/[id]/disciplinas/[disciplinaId]/avaliar` permite enviar texto
  opcional junto dos critérios. Novo texto/substituto sempre aguarda aprovação humana.
  Campo vazio omite o comentário e mantém o anterior. Texto inválido não bloqueia os
  critérios válidos: a interface trata `comentario_erro` e informa o sucesso parcial.
- O acompanhamento aceita os sete estados reais, incluindo `REJEITADO`, e apresenta
  texto descartado (`null`) sem recuperar conteúdo apagado. Compartilha o enum existente
  da PR #192. O substituto pendente não é anunciado como publicado nem restaura suspensos.
- Consulta privada com cookie, `no-store`, cancelamento e filtros opcionais UUID
  `professor_id`/`disciplina_id`. O servidor aplica os filtros junto da autoria da sessão.
  O GET sem filtros preserva a listagem anterior; UUID inválido retorna 422. O complemento
  técnico está em `specs.md`; não houve migration, mudança de modelo ou de requisito.
- Login/logout, foco e visibilidade invalidam dados privados anteriores. Respostas
  atrasadas ou posteriores à desmontagem/troca de sessão não reaparecem. Carregamento,
  vazio, acesso negado e falha de consulta têm estados distintos, com recuperação.
- Retirada explícita com confirmação usa `PATCH /api/comentarios/{id}/retirar`, sem
  reenviar critérios. Somente estados ativos oferecem a ação; autorização/estado são
  conferidos novamente na API. A lista é reconsultada após confirmação, refletindo também
  o cancelamento de eventual substituto. Falha HTTP não simula sucesso.
- Leitura pública e denúncia da #193 são preservadas, com projeção apenas de `id`,
  `texto`, `created_at`. Não há identidade pública, Web Storage, nova dependência,
  alteração de agregação ou decisão automática sobre procedência de texto.
- Textos longos quebram linha. O navegador temporário da fila é encerrado por CDP;
  os cenários passavam, mas a limpeza do processo ficava bloqueada no Windows.

## Evidências desta correção

Ambiente: Windows, Node 24.22.1, Edge/Chromium headless; Python 3.12 e PostgreSQL 16
em containers descartáveis exclusivos, com migrations até `20261101_03`.

| Verificação | Alcance |
|---|---|
| `node tests/run-tests.mjs` | 58 testes aprovados: estados, texto nulo, projeção pública/privada, contexto, cookie, no-store, cancelamento, PATCH e confirmação inválida, falhas HTTP e sucesso parcial de avaliação |
| ESLint, TypeScript e `next build --webpack` | Aprovados; usado o compilador suportado que funciona neste Windows, sem alterar o script padrão do projeto |
| `python -m unittest discover -s tests -q` | 159 testes aprovados, incluindo filtro de contexto/autoria, compatibilidade sem filtros, UUID inválido e limites do texto |
| `python -m tests.integration_moderacao` | PostgreSQL real: HTTP, limiar 49/50, concorrência, privacidade, ações, retenção e agradecimentos aprovados |
| Runners de avaliação/busca/protótipo, moderação, denúncia e comentários | Cenários aprovados; fila reexecutada após corrigir o encerramento do navegador de teste |
| `node tests/comentarios-browser.mjs` | HTTP controlado: permissões, sete estados, descarte, texto longo/escape, envio, substituição/retirada, erros/recuperação, vazio e resposta obsoleta após invalidar sessão |
| Mesmo runner com `COMENTARIOS_FIXTURE_FILE` | Sessões/API/PostgreSQL reais: acesso confirmado, texto opcional/inválido, substituto pendente, rejeição humana com descarte sem alterar versão publicada e retirada cancelando substituto |
| Conferência no PostgreSQL após navegador real | Uma avaliação e cinco critérios preservados após retirada: didática 4, dificuldade MEDIO, chamada verdadeira, material BOM e recomendação verdadeira |
| `mkdocs build --strict --site-dir /tmp/undb-rf20-site` | Documentação construída sem falhas em container temporário Python 3.12 |

O runner `comentarios-browser.mjs` integra `npm run test:browser` e também pode ser
executado por `npm run test:comentarios`. Usa Node/CDP como os runners existentes,
sem framework adicional. O backend de produto recebeu apenas filtros opcionais na
consulta existente, mantendo a identidade derivada do cookie.

## Rastreabilidade e limitações

| Critério | Evidência |
|---|---|
| AC20-01/02 | Texto opcional, validação 1/500 e 0/501, moderação prévia e critérios preservados quando texto é recusado |
| AC20-03 | Projeção pública sem identidade; leitura e denúncia existentes preservadas |
| AC20-04 | Substituto pendente e rejeição real com descarte; versão publicada anterior preservada |
| AC20-05 | Reenvio sem texto mantém comentário; retirada cancela pendente e preserva critérios, conferidos no banco |
| AC20-06 | Política visível na tela e julgamento humano; nenhum filtro/IA ou rejeição automática por discordância |

Foram verificadas seis combinações de largura emulada (320/768/1280 px) e tema
claro/escuro. Não houve smartphone físico, leitor de tela ou teste com usuários.
As evidências da #159 não substituem aceite humano nem homologação global RF20–RF22
na #163. Não se declara esta issue encerrada antes do merge e aceite.

## Reprodução com API/PostgreSQL reais

Use somente banco descartável, migrations aplicadas, API na porta 8000 com
`CORS_ORIGINS=http://localhost:3100` e `UNDB_INTEGRATION_TEST=1`. A fixture existente
na #193 cria contas e dados sintéticos; gere outra a cada execução, pois o cenário
rejeita textos e retira comentários. `undb-teste-api` abaixo representa seu container
isolado com `backend/` montado em `/app`.

```powershell
$fixtureRF20 = Join-Path $env:TEMP 'undb-rf20-fixture.json'
docker exec undb-teste-api python -m tests.denuncia_browser_fixture | Set-Content -Encoding utf8 $fixtureRF20
$env:COMENTARIOS_FIXTURE_FILE = $fixtureRF20
Push-Location frontend
npm ci
npm run build
npm run test:comentarios
Pop-Location
Remove-Item Env:COMENTARIOS_FIXTURE_FILE
Remove-Item -LiteralPath $fixtureRF20
```

Neste Windows, o build foi `node node_modules/next/dist/bin/next build --webpack`.
Remova somente seus containers/banco de teste ao terminar. Para HTTP controlado,
libere a porta 8000 e omita `COMENTARIOS_FIXTURE_FILE`. `BROWSER_PATH` pode selecionar
outro Edge/Chromium instalado; o runner usa portas 3100/9228 livres e perfil temporário.
