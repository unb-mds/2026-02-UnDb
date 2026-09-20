# Tela de exemplo consumindo API real — Issue #30

**Avaliação técnica:** os três critérios de aceite da #30 estão implementados nas telas de
produto entregues pelas #44/#45. Esta conclusão registra o estado do código e dos contratos
HTTP atuais; a decisão de considerar essa evidência suficiente para fechar ou reclassificar
a issue continua pertencendo ao Product Owner.

## Por que não construir uma tela de exemplo separada

A #30 foi criada para provar, **antes** das telas definitivas, que a separação
frontend/backend funcionaria na prática. As telas integradas de busca de professores e de
disciplinas (`/professores` e `/disciplinas`) já exercitam o mesmo fluxo com dados do produto.
Uma tela descartável adicional repetiria esse comportamento, sem ampliar a cobertura técnica.

## Evidência dos três critérios

As referências abaixo correspondem ao `develop` após a integração da #96 no commit
`d39ee44`:

| Critério da #30 | Evidência no frontend |
|---|---|
| Requisição real via `fetch()` a um endpoint do backend | `frontend/src/app/professores/page.tsx:31` chama `listarProfessores`; `frontend/src/lib/services/professores.ts:44-46` encaminha a consulta a `/api/professores`; `frontend/src/lib/services/api-client.ts:17-26` monta a URL, executa `fetch(url)` e desserializa a resposta. |
| Dados retornados são exibidos na tela | `frontend/src/app/professores/page.tsx:91-103` percorre `resultados` e renderiza nome e departamento de cada professor retornado. |
| Erros de requisição são tratados de forma visível | `frontend/src/app/professores/page.tsx:35-40` limpa resultados anteriores e registra a mensagem de erro; `frontend/src/app/professores/page.tsx:71-82` mantém a região com `aria-live="polite"` e exibe essa mensagem ao usuário. |

O contrato correspondente existe no backend em
`backend/app/routers/professores.py:21-29`: `GET /api/professores`, com resposta tipada como
lista de professores. O mesmo padrão também é usado pela busca de disciplinas.

## Limite da evidência de execução

`docs/estudos/verificacao-busca-professor-disciplina.md` registra o backend e o frontend
executados contra dados reais do SIGAA e valida o contrato HTTP, inclusive CORS. Essa
verificação usou `curl` e não observou em navegador a interação client-side de digitar,
receber a lista ou provocar a mensagem de erro. Portanto, ela sustenta o contrato real e,
com a inspeção acima, confirma que os critérios estão implementados, mas não deve ser
apresentada como teste E2E de navegador já executado.

## Recomendação técnica

Submeter ao Product Owner a decisão de fechar ou reclassificar a #30 com base nesta
evidência. Se o processo exigir demonstração E2E observada, executar primeiro o fluxo de
sucesso e o de falha em um navegador com frontend e backend reais; isso complementa a
evidência existente sem exigir uma tela descartável.
