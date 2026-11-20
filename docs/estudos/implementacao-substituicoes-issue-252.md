# Ampliação numérica da moderação — #252

**Data:** 15/11/2026. **Estado:** implementada localmente por solicitação explícita;
homologação dos rótulos e ativação em produção pendentes. Branch `feature/252-deteccao-ofensas`.

## Autorização e implementação

Após autorizar a primeira etapa, o solicitante pediu nesta sessão:
“Faça um pouco mais a implementação e inclua o tratamento para m3rda, p0rra e entre outros”.
Essa solicitação autoriza a ampliação funcional local, substituindo a exclusão numérica do
escopo anterior. Requisitos foram atualizados antes do código e sincronizados com specs e
[guia operacional](../moderacao-ia.md). Não autoriza ativação, uso de dados reais ou merge.

O módulo `backend/app/domain/filtro_moderacao.py` acrescenta regex pré-compiladas com
alternativas **por posição do termo conhecido**: `a4`, `e3`, `i1`, `o0`, `s5`, `t7`.
Reconhece `m3rda`, `p0rra`, `p0rr4`, `b4b4c4`, `1d10t4`, `0t4r10`, expressões e combinações
com as técnicas da primeira etapa. Não substitui números no comentário inteiro, não usa
substring/similaridade e não amplia a lista. Não foi adicionada a exceção `4→e` para `m4rda`.

Preserva fronteiras, os limites de separadores/repetições e todas as categorias anteriores,
incluindo U+FE0F/U+034F. Os dois serviços usam o mesmo agregador. Texto armazenado e enviado
à IA permanecem originais. Sinais/falhas continuam humanos, sem rejeição automática e sem
alterar critérios, privacidade, permissões, substituições, retenção, modelo ou contratos.

Configuração nova: `MODERACAO_SUBSTITUICOES_ATIVAS=False`, também exigindo
`MODERACAO_DISFARCES_ATIVO=True` e o filtro principal ativo. Flags e exemplos/Compose
permanecem desligados. A auditoria privada usa `252-disfarces-leet-v2` quando as duas
melhorias estão ativas. Desligar somente substituições restaura `252-disfarces-v1`;
desligar também disfarces restaura `239-lexical-v1`. Reiniciar pelo procedimento vigente;
não há migração, reprocessamento automático ou exclusão de dados.

## Comparação e limitações

Os 64 casos da primeira etapa foram preservados. A extensão
[casos-leet.json](evidencias/issue-252/casos-leet.json) tem 12 positivos e 12 negativos,
incluindo os exemplos solicitados e controles técnicos difíceis. Total: **88 casos**,
46 positivos, 36 negativos e seis contextuais. Rótulos permanecem exploratórios.

| Camada nos mesmos 88 casos | TP | FN | FP | TN |
|---|---:|---:|---:|---:|
| Filtro original #239 | 10 | 36 | 0 | 36 |
| Primeira etapa, números desligados | 24 | 22 | 0 | 36 |
| Primeira etapa + números | 42 | 4 | 3 | 33 |

Os quatro FN restantes são `m4rda`, repetição acima do limite, homoglifos fora do mapa
e pontuação acima do limite. A amostra foi construída para essas técnicas e não é um
conjunto independente de homologação; 42/46 não certifica precisão em produção nem
adota a antiga meta de 90% como aceite estatístico.

**Falsos positivos registrados, sem ocultá-los:** N20 (variável `m3rda`), LN01 (variável
`p0rra`) e LN02 (identificador `1d10ta`). O filtro lexical não distingue a mesma grafia em
uma ofensa de um nome técnico isolado. Não foram criadas exceções por aparecerem palavras
como “variável”, que poderiam dispensar indevidamente a revisão. Não são rejeições:
ficam pendentes para interpretação humana. Identificadores maiores como `p0rra_total`,
`prefixo_m3rda_sufixo`, códigos acadêmicos e números comuns dos controles não ganharam sinais.

O critério de zero sinais adicionais nos negativos da **primeira etapa** continua verificado
com números desligados. A ampliação tem o custo adicional medido acima; não foi declarada
homologada ou adequada à ativação. É necessário revisar os rótulos e aceitar/ajustar esse
comportamento antes de autorizar produção.

**API real:** zero chamadas; nenhum modelo efetivo retornado, FP/FN de IA não medidos.
Modelo configurado preservado: `omni-moderation-latest`. Foram executados **528 controles**
do serviço real com IA/repositórios simulados (88 × três respostas × números desligados/ligados),
sem banco nem publicação. Sinal/falha externa manteve pendência; sem sinal externo, os
encaminhamentos acompanham os sinais locais acima. Não confundir isso com eficácia da IA real.

Os [resultados por caso](evidencias/issue-252/resultados-leet.md) e
[dados completos](evidencias/issue-252/resultados-leet.json) incluem categorias, TP/FN/FP/TN,
decisão esperada proposta, estados obtidos nos controles, data, versão e hashes UTF-8/LF.
Também incluem tempos de 31 amostras após três aquecimentos em três entradas de 500
caracteres (números, quase termo e expansão NFKD), sequenciais, sem HTTP/banco.
Não se estabeleceu gate de latência nem previsão de carga/produção. Há custo adicional de
CPU/fila humana, sem nova dependência/serviço ou custo de API no ensaio.

## Reprodução e validação

Na raiz, com dependências já declaradas e venv de teste:

```powershell
$env:PYTHONUTF8 = '1'
python docs/estudos/evidencias/issue-252/avaliar_leet.py
```

O runner força banco/chave/flags sintéticos antes de importar módulos; não consulta a API,
não abre banco e grava somente `resultados-leet.json`/`resultados-leet.md`.
Resultados históricos da primeira etapa não foram sobrescritos; podem ser reproduzidos
exatamente no commit `b383ea8`. O HEAD e hashes identificam a versão medida mais o diff.

Testes cobrem exemplos numéricos, combinações, fronteiras, números acadêmicos, limites,
preservação das categorias, dependência/reversão das flags, falhas de regra, encaminhamento
humano, preservação do texto/substituído e versão na auditoria. A API é simulada.
Validação local final em Python 3.14.7, SQLAlchemy 2.1.8 e Ruff 0.17.3:

- 90 testes específicos de moderação/triagem/disfarces/comentários/denúncias aprovados.
- Quatro testes da bancada aprovados; 528 controles comparativos concluídos.
- Backend completo: 310 testes, **306 aprovados, dois erros e dois ignorados**.
  Repetiram-se os erros anteriores de cleanup em `tests.test_migration_connection`,
  `PermissionError [WinError 32]` nos arquivos SQLite temporários `migration%170.db` e
  `runtime.db`, após as asserções. Os dois ignorados exigem PostgreSQL descartável.
  A suíte completa não foi declarada aprovada.
- Ruff backend: lint aprovado, 148 arquivos formatados; lint/formatação dos runners aprovados.
- Compilação app/Alembic, MkDocs estrito, configuração Compose com o arquivo de exemplo e
  `git diff --check`: aprovados, sem iniciar serviços.

Docker sem daemon; não foram executados PostgreSQL nativo, migrações/e2e de navegador ou
API real. Frontend/contratos não mudaram; TypeScript não foi executado. O CI usa Python 3.12.
Nenhuma configuração de produção foi alterada. Os commits locais separam implementação
com regressões da documentação/evidências; não houve push, PR ou merge nesta ampliação.
