# Registro de uso de IA — UnDb

Atualizado em 17/11/2026, para a [#241](https://github.com/unb-mds/2026-02-UnDb/issues/241).
O registro cobre os usos sustentados pelas fontes abaixo; não representa um inventário
completo do uso passado de toda a equipe.

Estrutura inspirada no [registro do Cerradinho indicado por Nicolas](https://github.com/unb-mds/2026-2-Cerradinho-API/blob/13b071aa7afa3e085ab05ea362f1370ee5eb1131/AI-USAGE.md):
data/período, pessoa, ferramenta, atividade e tratamento da saída. Os registros pessoais
do outro projeto não foram reutilizados. A fonte original da política da disciplina não
foi fornecida; este arquivo não atribui à professora autoria ou validação deste conteúdo.

## Registros

### Release 1 — histórico ainda não levantado

Não há evidência suficiente nesta consolidação para atribuir ferramentas, modelos,
datas ou atividades a integrantes durante a R1. Existência de código, commits ou arquivos
de instrução não comprova uso de uma IA. Os integrantes podem acrescentar seus relatos
com referência ao artefato e às alterações aceitas, ajustadas ou rejeitadas.

### Release 2

| Data/período | Pessoa / origem | Ferramenta e modelo | O que foi pedido/feito | Aceito, ajustado, rejeitado ou pendente |
|---|---|---|---|---|
| 15/11/2026 | Nicolas relatou exercício com Gabriel e sugestões de Tiago | GPT, conforme relato; versão/interface não informadas | Apoio na elaboração de cenários de continuidade operacional | Exercícios reportados como realizados; sem resultado individual verificável de cada cenário. Não equivale a teste real de recuperação. Fonte: `docs/continuidade-operacional.md`, seção 7 |
| 16–17/11/2026, nesta sessão | Nicolas | Codex; modelo exato não registrado | Consulta das issues, análise da consolidação #263/#269 e correção das referências em #267/#278 | Nicolas solicitou as correções; somente referências foram atualizadas, sem novo aceite de entrega |
| 17/11/2026 | Nicolas | Codex; modelo exato não registrado | Implementar #269: inventário, Privacidade, Termos, ciência no cadastro, inclusão de “sem fins lucrativos” e verificações | Ajustado para preservar contas antigas, separar ciência de consentimento genérico e explicitar limites operacionais. Nicolas autorizou publicação em um commit; PR #281 integrada em 17/11, conforme GitHub consultado nesta sessão; integração não comprova deploy |
| 17/11/2026 | Nicolas | Codex; modelo exato não registrado | Preparar #241: atas retrospectivas, organização documental, README e registros de IA | Ajustado por Nicolas: corrigiu “entre R1 e R2”, forneceu semanas, ausências e exemplo de registro. Datas não lembradas ficaram como intervalos; issues foram usadas como contexto, sem inventar decisões. Revisão final da entrega segue pela PR |

### Fontes das entradas

- [Continuidade operacional](docs/continuidade-operacional.md).
- [PR #281 — implementação da #269](https://github.com/unb-mds/2026-02-UnDb/pull/281).
- [#267](https://github.com/unb-mds/2026-02-UnDb/issues/267) e [#278](https://github.com/unb-mds/2026-02-UnDb/issues/278): referências corrigidas nesta sessão.
- [Atas consolidadas](docs/atas/README.md) e [orientações relatadas](docs/orientacoes-2026-11-17.md).
- [Implementando com IA](docs/implementando-com-ia.md): funcionamento do fluxo com requisitos, specs e skills; descrição não equivale a prova de uso de cada ferramenta por toda a equipe.

## IA no desenvolvimento e IA dentro do produto

Este arquivo registra assistência no desenvolvimento, na documentação e nas verificações.
A triagem de comentários usa uma integração distinta, descrita em
[Moderação com IA](docs/moderacao-ia.md), relacionada à #239. A existência ou ativação
dessa integração não identifica qual assistente escreveu cada parte do sistema, nem
substitui o registro de desenvolvimento por pessoa.

## Como complementar

Acrescentar data/período efetivamente conhecido, pessoa que utilizou a ferramenta,
ferramenta/modelo quando conhecido, objetivo, arquivos/issue/PR e o que foi aceito,
rejeitado ou ajustado. Se não souber o modelo ou a data exata, indicar isso. Referenciar
resumos e evidências públicas, sem colar conversas privadas, credenciais ou dados reais
de avaliadores. Não registrar aceite humano, revisão ou teste que ainda não ocorreu.

A revisão de código, as verificações e as autorizações seguem as regras canônicas em
`skills/` e o fluxo de `CONTRIBUTING.md`. Este documento é um registro de uso e não cria
regras novas de avaliação individual ou governança.
