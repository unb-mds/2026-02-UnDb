# Template de ADR

Copie o modelo abaixo para `docs/adrs/NN-descricao.md` e siga o
[guia de manutenção](index.md). Este arquivo é um modelo, não uma decisão aprovada.
O histórico de versões do template é mantido pelo Git.

```markdown
# ADR NN — <título da decisão>

| Campo | Valor |
|---|---|
| Estado | Proposed |
| Data de preparação | AAAA-MM-DD |
| Autoria / responsável pela proposta | <pessoa ou referência> |
| Origem | <issue, requisito, restrição ou solicitação autorizada> |
| Base inspecionada | <commit e arquivos, quando houver diagnóstico da implementação> |
| Aprovação | Não aprovada; responsável, data e referência ainda não registrados |
| Substitui | Nenhum / ADR NN (proposta de substituição enquanto não aprovada) |
| Substituído por | Nenhum |

## Contexto

<Problema, requisitos e restrições com fontes. Separe fatos de hipóteses.>

## Alternativas consideradas

| Alternativa | Vantagens | Custos, riscos e limites |
|---|---|---|
| <opção> | <benefícios ligados ao problema> | <consequências> |

## Decisão proposta ou aprovada

<Escolha e alcance. Use "proposta" até haver aprovação humana explícita.
Distinga decisão autorizada de configuração implementada e de trabalho futuro.>

## Justificativa

<Por que a escolha atende às fontes melhor que as alternativas relevantes.>

## Consequências

<Benefícios, custos, riscos, impactos e limites da decisão.>

## Pendências e limites de aprovação

<Decisões Pending Decision, evidências ausentes e partes fora do escopo.
Se não houver pendências conhecidas, declare isso sem inventar aprovações.>

## Evidências e referências

<Links para origem, aprovação, ADRs relacionados, implementação e verificações.
Informe comandos, ambiente, resultados e limitações das verificações realizadas.>

## Histórico

| Data | Alteração | Referência |
|---|---|---|
| AAAA-MM-DD | Proposta inicial | <issue / PR / registro> |
```
