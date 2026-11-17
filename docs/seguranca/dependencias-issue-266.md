> Registro historico de 16/11/2026. Para o estado da entrega #266 apos os blocos,
> consultar [validacoes pendentes](validacoes-pendentes-266.md) e
> [evidencias do Bloco 7](evidencias/issue-266/bloco-7/resultados.json).
> Patches de source-map-js/zod foram implementados posteriormente; isso nao elimina
> os avisos residuais nem comprova aplicabilidade ou seguranca em producao.

# Dependências auditadas — #266

Base `d99916e`, consulta em 16/11/2026. Complementa o
[relatório técnico](revisao-sessoes-abuso-logs-issue-266.md). Não houve atualização de
dependências do produto, execução de payloads de advisories ou inspeção de produção.

## Inventário e reprodução

Backend: nove declarações de runtime em `backend/requirements.txt`, **sem versões fixadas
ou lockfile**. `requirements-dev.txt` fixa Ruff 0.17.3 e httpx 0.28.1; cobertura/docs são
declaradas à parte. A venv antiga da cópia principal tem outras versões e não foi usada
como evidência da produção. Foi criada venv isolada, Python **3.14.7 no Windows**; CI/Docker
especificam 3.12. Diferenças de plataforma e resolução permanecem limitações relevantes.

O [snapshot Python](evidencias/issue-266/python-resolvido.json) registra os 35 pacotes
alcançáveis pelos requisitos de runtime e extras aplicáveis à plataforma local. Inclui
FastAPI 0.163.1, Starlette 1.10.0, Pydantic 2.14.3/core 2.50.4, SQLAlchemy 2.1.8,
Alembic 1.20.1, Uvicorn 0.54.0, pwdlib 0.4.2/Argon2 25.1.0 e Resend 2.53.2.
Isso **não fixa** nem identifica as versões do serviço hospedado. Linux pode incluir
outros pacotes opcionais, como uvloop. Bibliotecas nativas e imagens do sistema não
receberam inventário por digest/SBOM nesta revisão.

Frontend: `package-lock.json` v3, 478 entradas; Next/eslint-config-next 16.3.5,
React/react-dom diretos 19.2.8; há entradas transitivas/peer 19.3.0 no lock. sharp 0.35.4,
glob 13.0.6, minimatch 3.1.5 e 10.2.6, source-map-js 1.2.1 e zod 4.6.5.
[Inventário completo](evidencias/issue-266/frontend-resolvido.json) distingue dev/opcional.
`npm ci --ignore-scripts --no-audit --no-fund` instalou o lock sem alteração. Node
24.21.0/npm 11.19.0 locais; CI usa Node 22 e Docker Node 24. ESLint 9.39.5 emitiu aviso
de fim de suporte, sem que esse aviso por si só constitua advisory de vulnerabilidade.

Os [hashes dos manifests](evidencias/issue-266/hashes-fontes.json) permitem verificar a
versão consultada. O script `inventariar_dependencias.py` nesta pasta de evidências gera
os snapshots; executar com a venv da revisão. `python-resolvido.txt` é entrada de auditoria,
**não** lock aprovado para instalação do projeto.

```text
python -m pip_audit -r docs/seguranca/evidencias/issue-266/python-resolvido.txt --no-deps --disable-pip -f json -o docs/seguranca/evidencias/issue-266/python-audit.json --progress-spinner off
cd frontend
npm audit --package-lock-only --ignore-scripts --json
```

`pip-audit` 2.10.1 consultou a base de advisories do PyPI e retornou zero advisories
conhecidos para esse snapshot. [Resultado](evidencias/issue-266/python-audit.json).
A instalação inicial dentro do sandbox falhou por bloqueio de socket; instalação e
consultas foram repetidas com acesso de rede autorizado, sem usar segredos do projeto.

`npm audit` retornou **14 nós afetados** (1 crítico, 3 altos, 10 moderados na contagem
agregada do npm), correspondendo a **16 advisories distintos**, incluindo dependentes
afetados indiretamente. Não somar nós a advisories. [Resultado npm](evidencias/issue-266/npm-audit.json).
Cada advisory foi conferido na API oficial `api.github.com/advisories/{GHSA}`;
[metadados primários](evidencias/issue-266/advisories-npm.json) preservam classificação,
data, intervalo afetado e primeira versão corrigida. O GitHub usa `medium` onde a
interface chama `moderate`; não foi recalculada gravidade própria.

## Achados por versão e condições

Cada linha confirma correspondência de versão; **não comprova exploração**. A coluna
de aplicabilidade registra inferência do código e suas limitações, sem reproduções.

| Pacote local / advisory primário | Gravidade da fonte | Correção informada | Condição e impacto no projeto / recomendação |
|---|---|---|---|
| next 16.3.5 — [GHSA-vcvr-r3jv-pc5j](https://github.com/advisories/GHSA-vcvr-r3jv-pc5j) | Critical | 16.3.6 | ImageResponse Node com SVG influenciado por entrada externa. Não foi localizado uso de next/og/ImageResponse em src; não reproduzido. Atualização direcionada recomendada. |
| next 16.3.5 — [GHSA-2464-fhr4-w9xw](https://github.com/advisories/GHSA-2464-fhr4-w9xw) | Critical | 16.4.1; sharp ≥0.35.5 como mitigação indicada | Otimização de SVG em Linux glibc; projeto usa next/image e Docker Debian. Entradas externas controladas por usuário não foram demonstradas. Priorizar revisão/correção do runtime e conferir o provedor; não assumir Windows local como proteção do deploy. |
| next 16.3.5 — [GHSA-673q-mjm6-r5xr](https://github.com/advisories/GHSA-673q-mjm6-r5xr) | Critical | 16.4.1 | Cache Components com função use cache retornando typed arrays. Não foram localizadas essas diretivas no src. Mantenedor recomenda atualização mesmo sem esse uso; não foi executada migração de versão nesta revisão. |
| next 16.3.5 — [GHSA-p3m5-59mp-jv5r](https://github.com/advisories/GHSA-p3m5-59mp-jv5r) | High | 16.4.1 | App Router com Server Action; impacto de disponibilidade. Não foram localizadas diretivas use server. Recomendar correção antes de introduzir esse recurso; não testar em público. |
| next 16.3.5 — [GHSA-cjq9-62q9-8jv4](https://github.com/advisories/GHSA-cjq9-62q9-8jv4) | High | 16.3.8 | URLs remotas permitidas em remotePatterns e DNS não confiável. Não há remotePatterns na configuração versionada; fonte declara não afetada a aplicação sem essa configuração. Revalidar ao mudar imagens/hosting. |
| next 16.3.5 — [GHSA-39w2-rjm5-chcv](https://github.com/advisories/GHSA-39w2-rjm5-chcv) | Low | 16.3.8 | Endpoint MCP do servidor de desenvolvimento; não expor next dev à internet. Publicação documentada usa build/start/plataforma. Exposição efetiva de dev não foi inspecionada. |
| next 16.3.5 — [GHSA-f87g-xv8r-7p7x](https://github.com/advisories/GHSA-f87g-xv8r-7p7x) | Medium | 16.3.8 | Rotas de imagem de metadados com Webpack/dynamicParams. Não foi identificada restrição privada sustentada por esse mecanismo nas rotas atuais. Revalidar ao introduzir geração dinâmica e corrigir versão. |
| next 16.3.5 — [GHSA-3w37-wq28-93x7](https://github.com/advisories/GHSA-3w37-wq28-93x7) | Medium | 16.3.8 | Combinação de Draft Mode e use cache pode misturar conteúdo. Esses usos não foram localizados no src; revisar caches na #265 e atualizar em tarefa direcionada. |
| next 16.3.5 — [GHSA-h694-7cp9-m8p3](https://github.com/advisories/GHSA-h694-7cp9-m8p3) | Medium | 16.3.8 | Cache aninhado e parâmetros de raiz. Não localizado use cache; não inferir problema atual nas respostas do backend. Atualizar/revalidar caches. |
| next 16.3.5 — [GHSA-4jqv-mc3x-m676](https://github.com/advisories/GHSA-4jqv-mc3x-m676) | Medium | 16.3.8 | Pages Router, SSG/ISR e self hosting; fonte exclui Vercel. Projeto usa App Router e publicação histórica na Vercel. Condições não demonstradas; conservar registro para mudanças de infraestrutura. |
| next 16.3.5 — [GHSA-mcj8-r9mp-w47p](https://github.com/advisories/GHSA-mcj8-r9mp-w47p) | Medium | 16.3.8 | Substituição de conteúdo em cache SSG/ISR. Condições de cache/provedor exigem revisão específica; nenhuma mistura entre contas foi demonstrada. #265 deve consumir este insumo. |
| sharp 0.35.4 — [GHSA-wq5f-xc86-pv6w](https://github.com/advisories/GHSA-wq5f-xc86-pv6w), CVE-2026-96889 | High | 0.35.5 | Biblioteca nativa librsvg e decodificação de SVG; depende do binário/sistema. Ligado ao aviso Next acima, sem contagem como dois incidentes. Conferir runtime Linux e priorizar atualização compatível. |
| glob 13.0.6 — [GHSA-3g3m-2fjr-6pw4](https://github.com/advisories/GHSA-3g3m-2fjr-6pw4) | Medium | 14.0.2 | Cancelamento por AbortSignal pode não limitar percurso de arquivos. Cadeia de ferramentas dev; não localizada chamada de aplicação exposta ao usuário. Atualizar ferramenta ascendente compatível, sem override de major arbitrário. |
| minimatch 10.2.6 — [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249) | Medium | 11.0.1 | Amplificação de padrões glob. Cadeias dev/lint; padrões HTTP não são usados diretamente pelo código de aplicação. A entrada 3.1.5 está fora do intervalo deste aviso específico; isso não a certifica. Atualizar upstream compatível. |
| source-map-js 1.2.1 — [GHSA-68fv-2mgg-jv7q](https://github.com/advisories/GHSA-68fv-2mgg-jv7q) | High | 1.2.2 | Processamento de source maps não confiáveis pode afetar disponibilidade. Cadeia de build CSS/dev; não há upload de source map no produto. Recomendar atualização compatível do lock em correção dedicada. |
| zod 4.6.5 — [GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5) | High | 4.6.6 | Coleções excessivas na validação; dependência de ferramentas dev, não importada por src. Recomendar atualização compatível e preservar contratos. |

## Decisão e continuação

Não foi executado `npm audit fix`, override global, mudança de major ou alteração de
serviços. Existem correções disponíveis; uma atualização direcionada deve testar Next,
eslint-config-next, sharp e seus lockfiles em conjunto, incluindo build, imagens,
metadados, páginas públicas, formulários e navegação. A referência 16.4.1 é a primeira
correção dos avisos mais recentes consultados, **não** declaração de versão final aprovada
ou de ausência de avisos posteriores. Consultar novamente na implementação.

Destino e responsável dessa correção precisam ser confirmados pelo PO no épico #272;
não foi criada issue ou atribuído trabalho por suposição. A #266 permanece com esse
risco rastreável e sem aceite integral. Mesmo um scanner sem resultados não comprova
ausência de vulnerabilidades; faltam versões de produção, dependências nativas,
imagens por digest e validação de condições do provedor.

## Continuidade — nova consulta de 16/11/2026

Preservado o inventário histórico acima. A conciliação com `develop@757b12c` não mudou
os quatro manifests/lockfiles inventariados: hashes conferidos novamente. O novo
snapshot foi produzido em **Python 3.12.16/Windows**, a partir dos mesmos requirements
sem pins: 35 pacotes de runtime, SQLAlchemy **2.1.9** em lugar de 2.1.8. As demais
versões do inventário de runtime permaneceram iguais; não representa produção nem
resolve a falta de lock Python. `pip-audit` 2.10.1 retornou zero advisories conhecidos
também para esse snapshot. Ferramentas de auditoria/uv/coverage ficaram em venvs
descartáveis, sem inclusão nos requirements do produto.

O lock npm continua com 478 entradas. Nova consulta `npm audit` retornou 14 nós
afetados (1 crítico, 3 altos, 10 moderados), mas agora **17 advisories distintos**.
Todos foram reconsultados na API oficial do GitHub: os 16 anteriores mantiveram os
metadados registrados; um advisory foi publicado na base hoje.

| Pacote/versão | Advisory e gravidade da fonte | Correção e recomendação | Aplicabilidade, risco e validação necessária |
|---|---|---|---|
| next 16.3.5 | [GHSA-mfr8-8qww-v76h / CVE-2026-119790](https://github.com/advisories/GHSA-mfr8-8qww-v76h), Medium | Primeira correção **16.4.5**; considerar Next e eslint-config-next 16.4.5 em atualização dirigida, sujeita a nova consulta/compatibilidade | Intervalo afetado ≥16.3.0 e ≤16.4.4. Exige combinação de `use cache`, `unstable_cache()` e root params; nenhuma dessas diretivas/chamadas foi localizada no código versionado atual. Risco de divulgação entre contextos de cache descrito pelo mantenedor; ocorrência no UnDb não demonstrada. Testar build, metadados, imagens, navegação e ausência de mistura entre sessões/caches. |

A recomendação anterior de 16.4.1 era histórica: **não cobre esse novo advisory**.
Não aplicar `audit fix` indiscriminado. Para os demais pacotes, continuam os candidatos
do quadro anterior: sharp 0.35.4 → 0.35.5, source-map-js 1.2.1 → 1.2.2,
zod 4.6.5 → 4.6.6; glob 13.0.6 → 14.0.2 e minimatch 10.2.6 → 11.0.1 precisam
de atualização do ascendente compatível, com atenção à mudança de major. Os três
últimos grupos são de ferramentas/dev conforme o lock; conferir cadeia com `npm explain`,
lint, 83 testes, tipos e build, sem forçar overrides que violem a faixa do ascendente.
A classificação e condições individuais dos 16 advisories anteriores continuam no
quadro histórico, não foram substituídas por uma conclusão genérica do scanner.

**Recomendado, aguardando aprovação/encaminhamento:** o feedback atual não define
destino e responsável da atualização dirigida. Nenhuma versão de produto foi alterada
nesta retomada. O PO deve confirmar esse encaminhamento e quem fará a revisão antes
da atualização, com prioridade para Next/sharp no runtime Linux. Não se afirma que o
runtime hospedado seja igual ao lock nem que uma condição não localizada seja impossível.

Evidências preservadas em [continuidade](evidencias/issue-266/continuidade/README.md):
inventários Python/npm, resultados brutos dos scanners sem dados de usuários, metadados
primários sem instruções de exploração e hashes dos manifests. A consulta não audita
imagem base, binários de produção, sistema operacional, configuração privada ou todos
os problemas ainda sem advisory. Ausência de achado Python não certifica segurança.
