# Tela de exemplo consumindo API real — Issue #30

**Situação:** os três critérios de aceite da #30 já são atendidos pelas telas de produto
entregues nas #44/#45, sem precisar de uma tela descartável adicional. Este documento
registra a evidência, em vez de duplicar código só para fechar a issue formalmente.

## Por que não construir a tela de exemplo separada

A #30 existe para provar, **antes** de construir as telas definitivas, que a separação
frontend/backend funciona na prática — seu próprio objetivo diz isso: "antes de construir
as telas definitivas de produto". As telas definitivas (`/professores`, `/disciplinas` e
`/professores/[id]/disciplinas/[disciplinaId]`) já existem e já fazem exatamente o que a
#30 pede, só que com dado de produto real em vez de `/health`. Construir uma tela de exemplo
agora seria construir depois do que ela deveria preceder — trabalho redundante, não
verificação adicional.

## Evidência — os três critérios, com arquivo e linha

| Critério da #30 | Onde | Evidência |
|---|---|---|
| Requisição real via `fetch()` a um endpoint do backend | `frontend/src/lib/services/api-client.ts` | `fetch(url)` sem mock, usado por toda chamada de serviço (`listarProfessores`, `listarDisciplinas`, `consultarAvaliacaoAgregada`) |
| Dados retornados são exibidos na tela | `frontend/src/app/professores/page.tsx` | Bloco `resultados.map(...)` renderiza o array retornado pela API |
| Erros de requisição tratados de forma visível | `frontend/src/app/professores/page.tsx` | `.catch(() => setErro("Não foi possível buscar professores agora..."))`, renderizado em `{erro && <p>{erro}</p>}` |

Testado com backend rodando localmente de verdade (não mock) — ver
`docs/estudos/verificacao-busca-professor-disciplina.md`, que documenta exatamente esse
fluxo com dado real do SIGAA.

## Recomendação

Fechar a #30 referenciando este documento, em vez de mantê-la aberta esperando uma tela que
não agrega verificação nova sobre o que as #44/#45/#43 já provam.
