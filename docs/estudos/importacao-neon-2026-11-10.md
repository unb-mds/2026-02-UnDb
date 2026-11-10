# Importação manual no Neon — graduação 2026.2

**Fonte do resultado:** resumo final fornecido por Nicolas em 10/11/2026 nesta
revisão da [PR #213](https://github.com/unb-mds/2026-02-UnDb/pull/213).
**Rastreabilidade:** [#164](https://github.com/unb-mds/2026-02-UnDb/issues/164),
[operação SIGAA](../operacao-importacao-sigaa.md) e [hospedagem](../hospedagem.md).
O relatório consolida evidências da sessão; não afirma nova importação executada
pelo revisor ou auditoria independente do histórico privado no Neon.

[Extrato do resumo fornecido, sem credenciais](../assets/evidencias/2026-11-10/importacao-resumo.json).

## Resultado final

| Campo do resumo | Resultado |
|---|---|
| `status` / `resultado.sucesso` | `sucesso` / `true` |
| Período | `2026.2`, nível `G — GRADUAÇÃO` |
| `iniciada_em` | `2026-11-10T00:11:57.177921+00:00` |
| `finalizada_em` | `2026-11-10T03:53:17.975093+00:00` |
| Duração do registro | 3h41min20,797s |
| Ofertas extraídas | 6.571 |
| Ofertas processadas | 6.571 |
| `erro` | `null` |

Em Brasília, de **09/11 às 21h11min57s** a **10/11 às 00h53min18s**. O início
interno da coleta (`resultado.inicio`) foi `00:12:29.464713+00:00`, distinto da
criação do registro de execução. O detalhe fornecido apresenta unidades com
ofertas e unidades sem oferta, com sucesso e listas de erros vazias. Exemplos:
CIC 108, Gama 229, Ceilândia 548, Química 201; Centro Integrado de Ordenamento
Territorial 0. Zero ofertas é um resultado válido, não falha.

Na consulta pública suplementar de **10/11/2026, 01h01, Brasília**, a API retornou:

| Medida | Quantidade |
|---|---|
| Disciplinas (`GET /api/disciplinas`) | 3.485 |
| Registros docentes (`GET /api/professores`) | 8.267 |
| Códigos de unidade distintos nas disciplinas | 69 |
| Health | `{"status":"ok"}` |

Os 8.267 registros não representam pessoas únicas: identidades provisórias podem
se repetir por ocorrência; reconciliação é a [#207](https://github.com/unb-mds/2026-02-UnDb/issues/207).
As 6.571 ofertas são os contadores do importador, **não uma contagem SQL de
turmas únicas**. Uma turma pode aparecer em mais de uma linha da fonte. Também
não são 6.571 novas inserções: reimportação pode atualizar registros existentes.

## Escopo e cobertura

O comando usado foi `python -m app.commands.importar_sigaa_agendado
--todas-unidades --ano 2026 --periodo 2`, a partir de `backend/`, com conexão
direta Neon/TLS recebida de forma oculta por um wrapper PowerShell local.
O wrapper da sessão não faz parte do repositório: para reprodução usar o comando
versionado e configurar o ambiente privado, conforme o guia de operação.

A enumeração observada antes da execução continha **211 opções de unidade** no
formulário público. Incluía programas de pós-graduação e órgãos administrativos,
mas **cada consulta usou graduação**. O nome da unidade não muda o nível
consultado; opções sem turmas também precisam ser verificadas para distinguir
ausência de oferta de unidade não visitada. O formulário é dinâmico: não fixar
211 como uma constante de produto.

O resumo informa sucesso integral da execução configurada. Para a comparação
auditável entre opções esperadas e processadas da #164, preservar o resultado
completo do histórico e conferir a lista/códigos, não apenas o total público de
69 unidades com disciplinas. Esta documentação não arquiva a lista integral nem
infere sua cardinalidade pelo número de cartões do catálogo.

O [relatório R1 de 24/09](validacao-release-1-sigaa-2026-09-24.md) é uma coleta
de outra data, com 6.555 linhas e 6.554 turmas únicas. Não é um denominador exato
para novembro. Estimativas de progresso dadas durante a sessão foram superadas
pelo resultado final; não se mantém uma porcentagem estimada de pendência.

## Lentidão e diagnóstico

A execução visita unidades sequencialmente e persiste por unidade, com savepoint
por oferta. Muitas operações SQL pequenas contra banco remoto acumulam latência.
Timeouts/retries de HTTP também podem acrescentar espera; não houve medição que
atribuísse toda a duração ao Neon ou ao SIGAA. `idle`/`ClientRead` apenas mostra
que PostgreSQL espera o cliente; não comprova bloqueio nem término. Não cancelar
sessões ou repetir a carga completa com base somente nessa observação.

Os erros iniciais de encoding do rótulo CIC e passagem da opção
`--todas-unidades` no wrapper foram corrigidos antes desta execução concluída.
O resultado final não deve ser confundido com essas tentativas falhas.

## Consultas de conferência no Neon

Executar como leitura no SQL Editor do banco correto, sem compartilhar conexão:

```sql
SELECT id, status, ano, periodo, iniciada_em, finalizada_em,
       ofertas_extraidas, ofertas_processadas, erro,
       jsonb_array_length(resultado_json::jsonb -> 'departamentos') AS unidades_processadas
FROM importacao_execucoes
ORDER BY iniciada_em DESC LIMIT 1;

SELECT COUNT(*) AS turmas_ativas_unicas
FROM turmas WHERE fonte = 'SIGAA' AND semestre = '2026.2' AND ativa;
```

Conferir ainda no `resultado_json` os códigos esperados, duplicados, unidades sem
ofertas e erros. O comando já registra sucesso/falha, e falhas parciais não
autorizam inativar ausências de uma coleta incompleta. Repetir apenas o escopo
necessário após diagnóstico; importação não restaura avaliações ou contas.

**Limites restantes:** esta é uma carga manual. Agendamento instalado, execução
subsequente e recuperação operacional continuam na #164; backup/restauração na
#170. O nome institucional na interface é correção da PR #215 e precisa da
promoção conjunta de API/frontend: na consulta de 01h01 a API pública ainda não
retornava `departamento_nome`. Isso não significa nome ausente no banco.
