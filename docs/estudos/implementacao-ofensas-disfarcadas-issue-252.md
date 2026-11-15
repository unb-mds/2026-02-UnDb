# Detecção complementar de ofensas — primeira etapa da #252

Registro da primeira etapa, preservado no commit `b383ea8`. A
[ampliação numérica posterior](implementacao-substituicoes-issue-252.md) foi solicitada
explicitamente nesta sessão e tem configuração, versão e resultados próprios.
As exclusões numéricas e hashes abaixo descrevem a primeira etapa.

**Data:** 15/11/2026. **Estado:** implementação local autorizada e executada;
homologação humana, avaliação adicional e ativação em produção pendentes.
Branch: `feature/252-deteccao-ofensas`, base remota atualizada
`7b0bd73f18815b337249a56901e272e2723d6718` (integração do estudo #258).
O checkout original e as branches anteriores foram preservados.

## Autorização e atendimento à revisão

A [PR #258](https://github.com/unb-mds/2026-02-UnDb/pull/258) integrou exclusivamente o
estudo/documentação. Seu aceite não foi interpretado como autorização funcional.
Foram consultados corpo, comentários, pareceres e conversa resolvida da revisão.

Depois dessa consulta, o solicitante esclareceu que Gabriel tem a mesma autoridade de
decisão de Nicolas e que os pontos sem decisão explícita lhe foram confiados. Em seguida,
aprovou nesta sessão o escopo inicial e os critérios descritos e autorizou implementar
agora com rótulos exploratórios, mantendo homologação e ativação pendentes. O
[registro da decisão](evidencias/issue-252/autorizacao-etapa1.json) distingue essa autorização
do aceite documental anterior. Os requisitos foram atualizados antes do código e propagados
para `specs.md` e o [guia operacional](../moderacao-ia.md).

O [parecer de Gabriel](https://github.com/unb-mds/2026-02-UnDb/pull/258#pullrequestreview-5912949613)
exigia não substituir o filtro anterior: `me\uFE0Frda` e `me\u034Frda`, usando os caracteres
efetivos, já são detectados por ele e se perdiam nos candidatos da bancada. Ambos foram
acrescentados como P33/P34 ao corpus e a testes locais/HTTP. A implementação faz a união
das categorias anteriores com as novas. Testes percorrem todos os termos da lista com
essas marcas; uma categoria antiga não pode desaparecer.

## Implementação e limites aprovados

`backend/app/domain/filtro_moderacao.py` contém o complemento, separado do filtro vigente,
da integração com a IA e da decisão de publicação. Não foi alterada a lista `239-proposta-2`.

- NFKD, remoção de marcas com classe combinante diferente de zero e casefold, sobre cópia.
  É a técnica estudada na #251; espaços são preservados para não apagar o limite de separadores.
- Remoção explícita de U+200B/U+200C/U+200D/U+FEFF/U+2060. Não remove indiscriminadamente `Cf`.
- Mapa somente dos caracteres cirílicos `а→a`, `е→e`, `о→o`, `і→i`, `с→c`.
  Não é implementação de UTS #39 nem cobertura geral de outras escritas.
- Regex pré-compiladas da lista versionada: fronteiras Unicode de palavra, até três
  espaços/pontos/hífens/sublinhados/asteriscos entre letras e até quatro repetições
  **contíguas** por posição. Entre palavras, um a três separadores. O hífen literal de
  `foda-se` permanece obrigatório e limitado, sem acumular os separadores opcionais adjacentes.
- A união preserva as regras anteriores mesmo quando elas aceitam algo fora desses limites
  novos, como espaços consecutivos entre palavras de uma expressão explícita.
- **Sem substituições numéricas**. `m3rda`, `m4rda` e variantes leet continuam dependendo
  da IA/revisão ou de uma etapa futura; não foram declaradas resolvidas.

`MODERACAO_DISFARCES_ATIVO=False` é a nova configuração, propagada pelo Compose com o
mesmo padrão. Os serviços automático e sob demanda usam a união quando o filtro principal
está ativo. O complemento sozinho não habilita a triagem/publicação. Sinais continuam
pendentes; falhas não se tornam resultado limpo. No apoio, uma falha do filtro retorna
`INDISPONIVEL`, sem erro bruto nem chamada à IA.

Texto armazenado e payload externo permanecem originais. Não mudaram endpoint, schema,
modelo, provedor, orçamento de chamadas, permissões, privacidade, retenção ou critérios.
Substituto sinalizado preserva a versão anterior; retirar/suspender não é contornado.
Publicação automática registra no motivo privado da auditoria a versão efetiva:
`252-disfarces-v1` ou `239-lexical-v1`; não guarda cópia adicional do texto.

## Resultados antes/depois por camada

O [corpus atual](evidencias/issue-252/casos.json) tem **64 casos**: 34 positivos, 24 negativos,
seis contextuais. Os dois casos acrescentados são da revisão; os rótulos globais continuam
propostos. A execução original de 62 casos foi preservada em `resultados.json`/`resultados.md`.
Os novos [resultados por caso](evidencias/issue-252/resultados-etapa1.md) e
[dados completos](evidencias/issue-252/resultados-etapa1.json) incluem fontes/hashes,
data, modelo configurado, texto escapado, decisões esperadas/obtidas e FP/FN por camada.

| Camada local, mesmos 64 casos | TP / 34 | FN / 34 | FP / 24 | TN / 24 |
|---|---:|---:|---:|---:|
| Filtro anterior / complemento desligado | 10 | 24 | 0 | 24 |
| Candidato isolado do estudo até separadores/repetições | 22 | 12 | 0 | 24 |
| União implementada, complemento ligado | 24 | 10 | 0 | 24 |

A cobertura exploratória dos positivos passou de 29,4% para 70,6%, com os dois casos
da revisão preservados e sem sinais adicionais nos 24 negativos atuais. A meta de 90%
do estudo não foi adotada para esta etapa. Zero em 24 controles não certifica uma taxa
populacional de FP zero, e a amostra não é independente de desenvolvimento/calibração.

P07–P10/P24/P25/P28 (números), P29 (repetição acima do limite), P30 (homoglifo fora do mapa)
e P32 (pontuação acima do limite) continuam sem sinal local. C01–C03/C05 continuam
sinalizados para revisão; citação/negação/anatomia não são prova definitiva de ofensa.
O contexto semântico de identificadores técnicos e citações precisa de homologação humana.

**IA real:** zero chamadas; modelo efetivo retornado inexistente; TP/FN/FP não medidos.
Modelo configurado permanece `omni-moderation-latest`. Não há comparação de qualidade
real da triagem combinada sem essa medição.

**Fluxo combinado controlado:** 384 execuções do serviço real com IA/repositórios simulados
(64 × três cenários × flag desligada/ligada), sem banco ou publicação de avaliações:

| Resposta simulada da IA | Antes: positivos pendentes / passaram | Depois: positivos pendentes / passaram | Negativos pendentes antes/depois |
|---|---|---|---|
| Sem sinais | 10 / 24 | 24 / 10 | 0 / 0 |
| Sinal | 34 / 0 | 34 / 0 | 24 / 24 |
| Falha | 34 / 0 | 34 / 0 | 24 / 24 |

No cenário sem sinais, a chamada ao mock caiu de 50 para 36 entre os 64 casos, porque
os novos sinais locais interrompem o fluxo automático antes da IA. Os casos com sinal/falha
externa verificam encaminhamento, não medem FP da API. Os seis contextuais não entram em
TP/FN/FP/TN. Não houve envio de comentários reais, publicação ou alteração em dados reais.

## Desempenho, custos e reversão

`medir_limites.py` mede seis entradas sintéticas com 500 caracteres, incluindo repetições,
quase termos, crítica, termo detectável e expansão NFKD. São três aquecimentos e 61
amostras por entrada/flag, sequenciais, sem HTTP ou banco. As amostras e p50/p95/máximo
estão em [desempenho-etapa1.json](evidencias/issue-252/desempenho-etapa1.json).
Na rodada final, p95 do complemento ligado variou de 0,689 a 13,804 ms entre essas
seis sondas; a maior foi a expansão de 500 caracteres U+FDFA. Os valores não são gates de CI.
É uma medição local de Python 3.14/Windows, sem meta de latência aprovada ou extrapolação
para carga/produção; entradas Unicode podem aumentar o tamanho da cópia normalizada.
Não há custo de API neste ensaio. O complemento consome CPU/memória existentes e pode
aumentar a fila humana; esse custo operacional em produção não foi medido.

Para desativar somente a melhoria: definir `MODERACAO_DISFARCES_ATIVO=False` e reiniciar
o backend pelo procedimento operacional vigente. Filtro anterior, IA e publicação vigente
continuam ativos conforme suas flags. Não há migração ou dados a desfazer, nem reprocessamento
automático das pendências. Não usar `MODERACAO_FILTRO_ATIVO=False` para esse rollback,
pois isso impediria novas publicações automáticas.

**Nenhuma configuração de produção foi alterada.** Homologação dos rótulos e avaliação
adicional, inclusive conjunto independente, permanecem condições antes de uma ativação
explicitamente autorizada. Não se tratou a autorização de implementar como autorização de ativar.

## Reprodução e validação

Com o venv e as dependências já declaradas, na raiz:

```powershell
$env:PYTHONUTF8 = '1'
python docs/estudos/evidencias/issue-252/avaliar.py
python docs/estudos/evidencias/issue-252/medir_limites.py
python -m unittest discover -s docs/estudos/evidencias/issue-252 -p test_avaliacao.py -v
```

Esses scripts forçam configuração sintética sem rede/banco; os arquivos históricos do
estudo não são sobrescritos. Hashes usam UTF-8/LF; o HEAD é a base mais o diff identificado
pelos hashes quando executado antes do commit. O runner de limites pode ter tempos diferentes.

Para testes backend, usar `DATABASE_URL`/`MIGRATION_DATABASE_URL=sqlite+pysqlite:///:memory:`,
`SECRET_KEY` sintética, chave OpenAI vazia e flags de moderação False. Os próprios testes
habilitam flags/mocks só no processo de teste. Nunca usar banco compartilhado para estes comandos.

```powershell
cd backend
python -m unittest tests.test_ofensas_disfarcadas tests.test_triagem tests.test_moderacao_automatica tests.test_moderacao tests.test_comentario tests.test_denuncia -v
python -m unittest discover -s tests -v
python -m ruff check .
python -m ruff format --check .
python -m compileall -q app alembic
```

Também verificar Ruff dos três scripts do estudo com `--config backend/pyproject.toml`,
MkDocs estrito e `git diff --check`.

| Verificação local final | Resultado |
|---|---|
| Triagem, disfarces, moderação, comentários e denúncias | 80 testes aprovados |
| Bancada offline | Quatro testes aprovados; 384 controles do serviço concluídos |
| Backend completo | 300 testes: 296 aprovados, dois erros de cleanup SQLite, dois ignorados |
| Ruff backend | Lint aprovado; 148 arquivos formatados |
| Ruff dos três scripts | Lint e formatação aprovados |
| Compilação app/Alembic | Aprovada |
| MkDocs estrito | Aprovado |
| Compose com `--env-file backend/.env.example config --quiet` | Aprovado, sem iniciar serviços |
| `git diff --check` | Aprovado |

Os dois erros são os já reproduzidos no estudo anterior, em
`tests.test_migration_connection`: cleanup de `TemporaryDirectory` com
`PermissionError [WinError 32]` em `migration%170.db` e `runtime.db`, depois das asserções.
Não foram corrigidos fora do escopo e a suíte completa **não** foi declarada aprovada.
Os dois testes ignorados exigem contenção real em PostgreSQL descartável.

O ambiente local usa Python 3.14.7/SQLAlchemy 2.1.8/Ruff 0.17.3; o CI usa Python 3.12.
Docker está sem daemon e não foi provisionado PostgreSQL descartável; não foram executados
ensaios de banco nativo/migrações/e2e de navegador, nem API real. Frontend e contratos não
mudaram; TypeScript não foi executado e não há verificação de tipos Python configurada.

Revisão local do diff: união das categorias, default desligado, reversão, payload original,
falhas, auditoria e fronteiras/limites conferidos, sem finding pendente no escopo aprovado.
Isso não substitui revisão humana, homologação do corpus ou avaliação real da IA.
