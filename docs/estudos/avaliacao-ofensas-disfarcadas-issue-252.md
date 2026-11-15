# Detecção de ofensas disfarçadas — avaliação da Issue #252

**Data:** 15/11/2026. **Estado:** avaliação exploratória executada; recomendação `Proposed`;
implementação, critérios e homologação humana `Pending Decision`.
**Produto:** Nicolas, [@nicolaszanin06](https://github.com/nicolaszanin06).
**Proponente/responsável pela apresentação:** Vinícius, [@ViniGvdo](https://github.com/ViniGvdo).

Nenhuma alteração funcional foi implementada. A investigação reproduziu limitações do
filtro local, sem medir a qualidade real da IA. Há candidatos promissores, mas a expansão
numérica também sinalizou controles técnicos legítimos. Recomenda-se ajustar e submeter
o corpus e a proposta a Nicolas antes de implementar. Não há aceite, ativação ou deploy.

## 1. Fontes, autorização e estado do Git

Consultados a [Issue #252](https://github.com/unb-mds/2026-02-UnDb/issues/252), seu histórico
de comentários, a [#239](https://github.com/unb-mds/2026-02-UnDb/issues/239), a
[PR #245](https://github.com/unb-mds/2026-02-UnDb/pull/245) e suas revisões/comentários,
a [#251](https://github.com/unb-mds/2026-02-UnDb/issues/251), requisitos, guia de IA e arquitetura.
Os retratos dos corpos, autores, estados e datas estão em
[fontes-github.json](evidencias/issue-252/fontes-github.json).

| Evidência observada | Alcance da autorização |
|---|---|
| #252 criada por Nicolas, aberta, sem comentários na consulta | Investigar; implementação expressamente condicionada a nova aprovação |
| #239 encerrada; #245 integrada em `develop` em 14/11 | Fluxo anterior autorizado, incluindo publicação automática sem sinais; não autoriza novas regras da #252 |
| #245: revisões de Tiago, sem decisão de Nicolas sobre os novos disfarces | Revisão da entrega anterior; não constitui aprovação da solução atual |
| Busca de PR por `252` e por `ofensas` sem resultados | Nenhuma PR destinada à #252 encontrada nessas buscas; não é prova de ausência de vínculos não indexados |
| Busca de issues por `disfarçadas` encontrou a #252 | Nenhuma decisão adicional encontrada nessa busca |
| Solicitante confirmou nesta sessão não haver revisão humana registrada do corpus | Homologação dos rótulos permanece pendente; agente não se declara revisor humano |

Não foi encontrada autorização suficientemente específica de Nicolas para a funcionalidade,
solução ou metas novas. Não se infere autorização da abertura da issue nem da entrega anterior.
Conversas externas não acessíveis não foram verificadas. As skills
`project-governance` (incluindo `HUMAN_APPROVAL_BOUNDARIES.md`), `testing` e `architecture`
orientaram a distinção entre observação, medição controlada e proposta.

Antes de modificar arquivos, `git status`, branches/worktrees e histórico mostraram:

- Checkout original em `develop`, `5e07337`, com dois caminhos não rastreados do estudo #251.
  Nenhuma alteração rastreada ou commit local exclusivo dessa branch; 308 commits atrás da base remota.
- `git fetch origin` concluído. Base correta pelo CONTRIBUTING e pela #245: `origin/develop`,
  **`4d5dabf5343e324c369cf70316e778eb50801a6e`**, já contendo o estudo #251 pela PR #253.
- `origin/main`: `17d9b62c720a8a4192adef86aff4b4ac8dd27989`; não foi presumido que esse SHA
  corresponde exatamente ao processo atualmente em execução em produção.
- Trabalho isolado em `.worktrees/issue-252-estudo`, branch `docs/252-avaliacao-ofensas`,
  criada da base remota. Checkout original e suas alterações foram preservados.
- Commits locais autorizados pela solicitação desta tarefa. Sem push, PR, merge ou encerramento de issue.

Há trechos históricos desatualizados em requisitos/arquitetura/guia que ainda dizem
"IA futura" ou "não ativada". As seções explícitas de evolução da #239 e os registros
remotos posteriores registram a autorização/ativação anterior. O estudo não altera essas
fontes para aprovar a #252 nem trata as flags padrão do código como estado de produção.

## 2. Diagnóstico da implementação vigente

| Camada / arquivo no backend | Responsabilidade observada |
|---|---|
| `app/domain/triagem_comentario.py` | NFD + casefold, remove marcas `Mn`; regex por palavra/expressão completa, sem substring; aceita espaços consecutivos entre palavras |
| `app/data/termos_moderacao.json` | Lista versionada `239-proposta-2`, ainda marcada `proposed`, com motivos/justificativas; não alterada |
| `contem_dados_sensiveis` no mesmo domínio | Barreira de dados reconhecíveis e partes do nome/e-mail do autor; não anonimiza todo texto |
| `app/services/openai_triagem.py` e `app/schemas/triagem.py` | REST fixo `/v1/moderations`, família `omni-moderation-*`, payload só texto/modelo, validação estrita de booleanos/categorias; integração `239-moderations-v1` |
| `app/services/triagem_service.py` | Apoio privado sob demanda; verifica permissão/impedimentos, flags, privacidade, cota e versão após chamada; devolve sinais, sem decidir publicação |
| `app/services/moderacao_automatica_service.py` | Novo/substituto pendente: exige todas as flags/chave; sinal local ou privacidade encerra a triagem **antes da IA**; só sem sinal chama IA |
| `app/services/avaliacao_service.py` e repositories de comentário/moderação | Confirma critérios/versão antes da chamada; depois bloqueia e revalida estado/texto/versão anterior; publica e audita como sistema apenas quando elegível |
| `app/services/moderacao_service.py`, routers/schemas | Revisão humana, permissões e impedimentos; auditoria privada e retenção de sete dias; sem novos contratos públicos |

No fluxo automático, `flagged=true` **ou qualquer categoria** mantém pendência.
Falha de normalização/triagem, falha de API, cota ou configuração incompleta mantém revisão
humana. Versão retirada ou alterada não é republicada; substituto sinalizado preserva o
anterior publicado. Suspensão/remoção/denúncia não é contornada pela edição. Critérios,
privacidade, descarte e identidade pública do autor permanecem independentes da análise textual.
Não existe rejeição automática. O apoio manual pode consultar IA mesmo havendo sinal lexical;
isso difere do curto-circuito da triagem automática.

Configuração observada no código, `.env.example` e Compose: flags de filtro/IA/dados/automática
desativadas por padrão, modelo `omni-moderation-latest`, timeout 10 s (restrito a 1–30),
5 chamadas/minuto e 100/24h, por processo. Há tetos de 30/minuto e 1.000/24h,
uma tentativa, sem redirecionamento, resposta até 32 KiB e texto até 500 caracteres.
O orçamento conta tentativas falhas, reinicia com o processo e multiplica com workers.
Não foram lidos segredos ou alteradas configurações de produção.

O filtro já detecta os explícitos, caixa/acentos e espaços entre palavras testados em
P01–P06/P27/P31. Não identifica P07–P26/P28–P30/P32, incluindo `m4rda`, `m3rda`,
letras separadas, repetições, invisíveis e homoglifos. Isso confirma a limitação lexical,
prevista na #239; **não prova** que a triagem com a API real publique esses textos.

## 3. Relação com a Issue #251

A #251 continua aberta e sem comentários, mas seu estudo foi integrado pela
[PR #253](https://github.com/unb-mds/2026-02-UnDb/pull/253). Não confundir avaliação
documental integrada com implementação das funcionalidades de busca, ainda condicionadas.
Consultados [relatório](avaliacao-busca-autocomplete-issue-251.md),
[resultados](evidencias/issue-251/resultados.md),
[reprodução](evidencias/issue-251/reproducao.md), `dataset.json`,
`preparar.py` e `medir.mjs` do estudo.

O ensaio anterior comparou 26 consultas sintéticas em busca atual/literal/pg_trgm,
acentos, nomes compostos, pontuação, erros e códigos; mediu PostgreSQL 18.6 WASM,
sem validar PostgreSQL 16 nativo. Recuperou grafias, mas introduziu resultado indevido;
um score de 0,6667 serviu tanto a acerto quanto a falso positivo. Meilisearch não foi medido.

| Técnica da #251 | Adequação à moderação / aproveitamento efetivo |
|---|---|
| `backend/app/domain/texto.py::normalizar_busca` (NFKD, marcas, casefold, espaços) | Reutilizada **somente na bancada**: 10/32 contra 8/32; ganho nos dois caracteres de compatibilidade P20/P21, sem novo sinal nos controles |
| Hífens como espaço e apóstrofos removidos na variante literal de `medir.mjs` | Ideia adaptada, sem copiar código SQL: separadores limitados **entre caracteres do termo conhecido**, preservando fronteiras; remoção indiscriminada não recomendada |
| Similaridade/trigramas, omissões e transposições | Não reutilizados: recuperação de alternativas tolera resultados indevidos; não há limiar validado para ofensa nem necessidade de extensão/serviço |
| Identidades, ranking, índices e infraestrutura | Não reutilizados; nenhuma tabela, dependência, serviço ou modelo adicional necessário ao ensaio |
| Invisíveis, homoglifos, leetspeak e repetição | Não avaliados pela #251. São experimentos novos da #252, sem atribuí-los ao estudo anterior |

NFKD resolve representações de compatibilidade, mas não toda semelhança visual.
A separação entre normalização e confusabilidade é consistente com
[unicodedata](https://docs.python.org/3.14/library/unicodedata.html) e
[UTS #39](https://www.unicode.org/reports/tr39/). O mapa reduzido ensaiado não implementa UTS #39.

## 4. Corpus, método e reprodutibilidade

[Corpus completo](evidencias/issue-252/casos.json): **62 exemplos**, 32 positivos,
24 negativos e seis contextuais. São dados sintéticos sem associação a docentes reais.
Os rótulos foram preparados pelo agente e **não revisados/homologados por humanos**.
A ausência de revisão foi confirmada pelo solicitante; os resultados abaixo são exploração,
não validação de produto. A revisão deverá registrar responsável, data e divergências.

Positivos incluem múltiplos termos e expressões, números, pontuação, espaços, repetições,
invisíveis, compatibilidade Unicode, cirílico misto, caixa e combinações. Negativos incluem
críticas sobre didática/provas/organização, substrings, números, referências, termos técnicos
e identificadores difíceis. Contextuais separam citação/negação/anatomia/ambiguidade.

Cada linha dos [dados de resultados](evidencias/issue-252/resultados.json) registra ID,
texto original e escapado (para inspeção dos invisíveis), grupo/categoria/decisão esperados
**propostos**, sinais de cada variante, TP/FN/FP/TN, barreira de privacidade, campos da IA real
e combinada real (nulos quando não executadas), e três controles de fluxo com decisões obtidas.
Há [tabela por caso](evidencias/issue-252/resultados.md) e
[comandos/validação](evidencias/issue-252/reproducao.md).

TP/FN contam presença/ausência de sinal nos 32 positivos, não quantidade de categorias;
FP/TN contam sinal/ausência nos 24 negativos. Os seis contextuais ficam fora desses
denominadores. C01–C03/C05 têm revisão humana esperada pela regra vigente de termos;
não são automaticamente falsos positivos de encaminhamento nem ofensas comprovadas.
C04/C06 não têm decisão esperada binária: falta julgamento contextual.
Já N20/N21 têm rótulo negativo **proposto**, permitindo expor o custo de regras numéricas.

Executado no Windows, Python 3.14.7, usando dependências já declaradas no backend,
em venv de avaliação. O CI usa Python 3.12; não se afirma paridade integral entre ambientes.
SHA-base, hashes de fontes/corpus/runner, Unicode DB e data UTC estão no JSON.
Nenhum banco compartilhado, publicação de comentário ou chamada externa foi realizado.

## 5. Resultados medidos por camada

### Filtro local e candidatos isolados

As variantes são cumulativas, salvo a baseline. São comparações **antes/candidato**,
não antes/depois de implementação: o backend continua idêntico à base.

| Variante | Positivos identificados / 32 | FN / 32 | Negativos sinalizados / 24 | TN / 24 |
|---|---:|---:|---:|---:|
| Atual, NFD e palavras completas | 8 | 24 | 0 | 24 |
| `busca_nfkd`, reutilização da #251 | 10 | 22 | 0 | 24 |
| + cinco invisíveis permitidos na bancada | 13 | 19 | 0 | 24 |
| + mapa reduzido de homoglifos (`unicode`) | 15 | 17 | 0 | 24 |
| + separadores e repetições limitados | 22 | 10 | 0 | 24 |
| + leetspeak condicionado à expressão | 28 | 4 | 1 | 23 |
| + hipótese específica `4` como `e` em `merda` | 29 | 3 | 2 | 22 |

O filtro atual teve cobertura 25% nesta seleção adversarial. O candidato mais amplo teve
90,6% e sinalizou 8,3% dos controles (2/24). Zero em 24 controles de variantes menores
não demonstra taxa populacional zero. O corpus foi construído para essas técnicas e não é
conjunto reservado independente; ajustar nele e anunciar generalização seria inadequado.

### OpenAI Moderation API real

**Não executada**: zero chamadas, 62 casos não analisados, modelo retornado inexistente.
TP/FN/FP e tipos perdidos são **não medidos**, não zero. O modelo configurado na base é
`omni-moderation-latest`, alias sujeito a evolução; nenhuma versão efetiva foi inventada.
Não há ambiente/chave de teste com autorização específica para esta rodada.
O guia da API não oferece categoria de palavrão genérico; sinalizações nativas não devem
ser confundidas com a lista local. [Fonte oficial](https://developers.openai.com/api/docs/guides/moderation).

### Triagem combinada

Qualidade real **não medida**, pois depende da API real. Executou-se o `processar` vigente
em **186 controles** (62 × três cenários), com repositórios e IA substituídos por mocks,
objetos somente em memória, sem banco nem persistência:

| Controle do fluxo atual | Positivos pendentes / passaram | Negativos pendentes | Alcance |
|---|---|---:|---|
| IA simulada sem sinal | 8 / 24 | 0 | Reproduz dependência da IA nos 24 casos perdidos pelo filtro; não afirma resposta real do modelo |
| IA simulada com assédio | 32 / 0 | 24 | Verifica encaminhamento quando há sinal; esses 24 não são FP medidos da API |
| IA simulada indisponível | 32 / 0 | 24 | Falha mantém revisão por regra, não conta como detecção nem FP semântico |

Os quatro contextuais com termo também ficaram pendentes antes da chamada. No cenário
sem sinal, 50 chamadas ao mock, 50 estados PUBLICADO em objeto e 12 pendências por sinal
local; não houve publicação de avaliações. Nenhuma barreira sensível foi acionada pelo corpus.
Os candidatos **não foram injetados** no fluxo nem simulados como mudança aprovada.

## 6. Técnicas, limitações e escolha recomendada

**Proposta para ajustar e validar**, sem escolher regra efetiva:

1. Priorizar cópia derivada de texto para análise, mantendo original para revisão/auditoria
   segundo a retenção existente. NFKD, conjunto explícito de invisíveis e regras entre letras
   de termos conhecidos têm evidência local favorável; não normalizar o texto armazenado ou
   o payload externo silenciosamente.
2. Separadores da POC são espaço, ponto, hífen, sublinhado e asterisco; até três entre letras,
   e até quatro repetições por posição. São limites experimentais, não aprovados nem
   calibrados. P29 (oito `e`) e P32 (quatro pontos) continuam passando, assim como P30
   (small capital `ᴍ`, fora do mapa). Não recomendar aumento ilimitado para cobrir esses casos.
3. O mapa `а/е/о/і/с` cirílico é pequeno; outras escritas, emojis, controles bidi, soft hyphen
   e várias combinações não estão cobertos. ZWJ/ZWNJ têm uso legítimo em outras línguas;
   não remover toda categoria `Cf` por padrão. Uma eventual regra precisa de negativos multilíngues.
4. Leetspeak usa classes por posição do termo (`a4`, `e3`, `i1`, `o0`, `s5`, `t7`),
   sem transformar todos os números do comentário. Ainda assim N20 (`m3rda` como variável)
   é sinalizado. Exigir aprovação específica dos casos técnicos e separar contexto lexical
   de contexto semântico; não recomendar a variante ampla como pronta para produção.
5. `m4rda` → `marda` com `4→a`. P07 só foi recuperado ao testar uma exceção `e34` no termo
   `merda`, que também sinalizou N21 (código técnico). Essa exceção não decorre da #251
   nem é prova da intenção do autor. Nicolas deve decidir seu tratamento explicitamente.
6. Preservar IA atual, filtro e revisão humana em conjunto. Não enviar versões adicionais
   normalizadas à API, ampliar a lista, mudar modelo/provedor ou ajustar limiar de scores
   sem decisão específica. Nenhuma necessidade de biblioteca/serviço/modelo novo foi demonstrada.

Não foram medidos desempenho sob carga, custo de compilação das regex ou entradas
adversariais de pior caso. A POC recompila padrões; eventual implementação aprovada
deverá validar limites/tempo e avaliar pré-compilação, sem prometer custo de CPU nulo.

Não se propõe rejeição automática. Uma ocorrência aproximada seria somente sinal para revisão;
normalização não publicaria/rejeitaria por conta própria. A recomendação preserva RF20–RF22,
R2-DEC-03/04/05/13/14 e o mínimo de agregação RNF02.

## 7. Decisões que dependem de Nicolas

| Decisão pendente | Material concreto para revisão |
|---|---|
| Aprovar, ajustar, adiar ou não implementar | Resultados das sete linhas da comparação; ainda sem versão funcional escolhida |
| Quais técnicas/termos e comportamento aceitar | Lista de invisíveis/mapa/separadores/repetições, leetspeak e exceção P07/N21; preservação das regras de publicação da #239 |
| Homologar corpus e negativos técnicos/contextuais | 62 casos, rótulos e decisões; registrar julgadores, data e divergências; sem usar Vinícius como substituto da autoridade do PO |
| Definir critérios de aceite e metas | Proposta: preservar todos os explícitos e críticas homologados, tratar P07/P08 conforme decisão; em corpus reservado revisar FN por técnica e FP por classe |
| Aprovar limites quantitativos | Ponto inicial **proposto**: ≥90% dos positivos e ≤1% dos negativos em amostra independente; zero novos sinais nas críticas acadêmicas críticas homologadas. Os 2/24 FP da variante ampla não atendem esse candidato a limite |
| Autorizar ensaio real em teste | Ambiente/operador/chave, envio sintético, máximo de chamadas, prazo, registro de modelo efetivo e tratamento de falhas; não usar credenciais de produção por conveniência |
| Autorizar implementação e eventual ativação separadamente | Atualizar requisitos aprovados primeiro se comportamento mudar; sincronizar specs/guia/contratos; nenhuma aprovação de ativação está implícita no estudo |

Para a próxima rodada, propõe-se dois julgadores e arbitragem registrada, separação prévia
de ajuste e validação, ao menos 100 positivos e 100 negativos adicionais (incluindo números,
nomes comuns, citações e outras escritas). Isso é plano proposto, não tamanho suficiente para
certificar taxa de 1%: apresentar denominadores e intervalos de incerteza, sem concluir por
meta populacional a partir de poucos erros observados. Rótulos contextuais precisam permitir abstenção.

## 8. Custos, operação e reversão

Este ensaio: zero chamadas à API e zero custo de API; execução local, sem infraestrutura ou
dependências de produção novas. O endpoint de moderação é documentado como gratuito na
[fonte oficial consultada em 15/11/2026](https://developers.openai.com/api/docs/guides/moderation).
Isso não elimina cotas, latência, CPU, operação da fila humana ou futura mudança de condições.
O aumento da fila por FP deve ser medido; não foi estimado em produção nesta tarefa.

**Plano proposto para avaliação real:** uma passagem dos 62 casos, no máximo 62 tentativas
externas, sem retentativas automáticas; 5/minuto e 100/24h da configuração padrão,
esperando a janela entre lotes. Reservar orçamento por execução, contando falhas, e parar
ao atingir o teto. Não elevar flags/cotas de produção para rodar o corpus. Avaliar a API
isoladamente inclusive nos casos lexicais e depois compor respeitando o curto-circuito;
não comparar apenas textos que o filtro deixou passar. Preservar a barreira de privacidade.
Só implementar/executar esse runner de rede após a autorização do ambiente e rótulos.

Reversão **atual**: não há regra ativa nova a desligar. Remover os arquivos do estudo e links
documentais não afeta a aplicação. Não é necessário tocar em flags, dados, migrações ou modelo.

Reversão **futura proposta**: normalizador separado, possibilidade de desligar somente a nova
detecção e voltar ao filtro `239-proposta-2`, mantendo IA/privacidade/triagem/revisão. Registrar
versão da regra na auditoria existente sem guardar cópia adicional do texto. Definir mecanismo
e configuração somente com a solução aprovada. Desligar `MODERACAO_FILTRO_ATIVO` hoje mantém
todos os envios pendentes pelo código atual; não equivale a retornar ao filtro anterior.
Não reprocessar automaticamente pendências ao reverter.

## 9. Entrega e validação

Alterados somente corpus, scripts/evidências e documentação. `backend/app`, lista, testes
da aplicação, modelo, dependências, requisitos e configuração de produção não foram alterados.
As rotinas experimentais ficam em `docs/estudos/evidencias/issue-252/`, fora do runtime/CI.

- 64 testes existentes de triagem/moderação/comentário/denúncia: aprovados.
- Bancada: quatro testes aprovados; 186 controles de fluxo sem rede/banco concluídos.
- Backend completo: 275 testes, **271 aprovados, dois erros e dois ignorados**.
  Erros reproduzidos isoladamente em `tests.test_migration_connection`: limpeza de SQLite
  por `TemporaryDirectory`, `PermissionError [WinError 32]` em `migration%170.db` e `runtime.db`.
  As asserções anteriores passaram; falhou o cleanup com handle aberto no Windows/Python 3.14.
  Nenhum arquivo do backend foi alterado; não corrigido fora do escopo nem declarado sucesso da suíte.
- Dois testes de contenção PostgreSQL ignorados pela própria suíte: sem PostgreSQL descartável.
- Ruff 0.17.3 do backend: lint aprovado, 142 arquivos já formatados; compilação app/Alembic aprovada.
- Ruff dos dois scripts do estudo: aprovado, com formatação verificada usando configuração do backend.
- Documentação MkDocs estrita e `git diff --check`: resultados na
  [reprodução/validação](evidencias/issue-252/reproducao.md).
- API real, PostgreSQL nativo/migrações/integração de navegador: não executados. Docker sem daemon;
  não há banco descartável provisionado. Frontend/lint TypeScript não executados: nenhum arquivo
  frontend/contrato alterado; não há verificação de tipos Python configurada no projeto.

O estudo está pronto para revisão técnica e de produto, com homologação e decisão funcional
explicitamente pendentes. Os hashes dos commits locais e a branch são informados na entrega;
não existe commit de implementação funcional.
