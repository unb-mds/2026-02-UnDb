# Protótipo das telas principais — Issue #152

Verificação local em 13/10/2026. Proposta visual para revisão humana, vinculada à
[Issue #152](https://github.com/unb-mds/2026-02-UnDb/issues/152) e à
[Epic #144](https://github.com/unb-mds/2026-02-UnDb/issues/144).
Não representa validação com alunos, aceite do PO ou conclusão da Epic.

## Escopo e fontes

Foram consultados a descrição completa das duas issues, `docs/requisitos.md`, os
ADRs 02/08 em `docs/arquitetura.md`, `CONTRIBUTING.md`, as instruções de agentes,
as skills de implementação, páginas Next/Tailwind, testes, revisão e governança,
as rotas/serviços/tipos e as verificações existentes do frontend.

O checkout inicial estava em `develop`, sem mudanças locais, no commit `07fed88`.
Após `git fetch origin develop`, `HEAD...origin/develop` tinha divergência `0 0`
antes dos commits desta entrega. Trabalho em `feature/152-prototipo-jornada-ux`,
com futura PR destinada a `develop`. Não houve push, criação de PR ou merge.

## Implementação e jornada

A página inicial oferece acesso a `/prototipo`. As cinco etapas são representadas
pela mesma rota com parâmetros de URL, preservando contexto, recarga e navegação
pelo histórico. O layout e os tokens visuais existentes são herdados.

1. **Entrada:** escolha entre professor e disciplina; explicação da consulta pública.
2. **Busca:** nome parcial de professor ou nome/código de disciplina, sem filtro por
   curso/departamento, ignorando caixa e acentos. O mínimo de dois caracteres segue
   a interface existente e não altera requisitos.
3. **Resultados:** cartões identificam nome, departamento e código quando pertinente.
   Busca por professor exige escolher sua disciplina antes da comparação.
4. **Comparação:** apenas docentes da mesma disciplina; cinco critérios, contagem,
   conflito factual, insuficiência e ausência explícita de avaliações. Uma ação
   apresenta a fixture na ordem de recomendação aprovada, mantendo insuficientes no final.
5. **Avaliação:** identificação do professor e disciplina, cinco campos obrigatórios,
   sem respostas predefinidas nem texto livre. A ação confere a prévia sem envio.

O componente `CriteriosAvaliacao` foi extraído do formulário existente para uso real
e demonstrativo. O formulário real mantém sessão, envio, erros e persistência via
serviços existentes; somente seus campos passam a usar o componente compartilhado.
As opções e a validação vêm de `src/lib/avaliacao-formulario.ts`, sem nova escala.

Dados fictícios ficam exclusivamente em `src/app/prototipo/dados.ts`, tipados pelos
contratos institucionais/agregados existentes. São retratos preparados, não resultados
de um serviço fictício. Não há endpoints, integrações, nova biblioteca, fórmula de
agregação ou acesso ao banco. Carregamento e erro são exemplos visuais acionados
explicitamente, sem simular tráfego ou atraso de API.

## Reprodução e prévia visual

Em `frontend/`, execute `npm ci` e `npm run dev`; abra
`http://localhost:3000/prototipo`. O protótipo não exige backend. Alternativamente,
use `npm run build` e `npm run start`. Os links do header levam ao sistema real.

Roteiros:

- **Disciplina:** buscar “Algoritmos” → selecionar resultado → ordenar por recomendação
  → avaliar Ana → selecionar os cinco critérios → conferir prévia.
- **Professor:** buscar “Ana” → selecionar professor → selecionar Algoritmos
  → comparação → formulário.
- **Outro departamento/ausência:** buscar “MAT-DEMO” → Cálculo → ausência de dados
  suficientes → avaliar Elisa.
- **Estados:** nos resultados, usar Busca vazia, Sem resultados, Ver carregamento e
  Ver erro; neste último, Tentar novamente conserva o termo e recupera os resultados.

Capturas geradas no Edge headless e inspecionadas visualmente:

| Tela | Captura |
|---|---|
| Entrada | [Desktop claro](evidencias/issue-152/01-entrada.png) |
| Busca | [Desktop claro](evidencias/issue-152/02-busca.png) |
| Resultados | [Desktop claro](evidencias/issue-152/03-resultados.png) |
| Comparação | [Desktop claro](evidencias/issue-152/04-comparacao.png) |
| Formulário | [Desktop claro](evidencias/issue-152/05-avaliacao.png) |
| Comparação móvel | [320 px, tema escuro](evidencias/issue-152/06-comparacao-mobile-escuro.png) |

## Rastreabilidade de requisitos

| Fonte | Representação e verificação |
|---|---|
| RF04 | Entrada, busca e comparação públicas; sem sessão ou API no protótipo |
| RF05–RF07 | Nome parcial de professor, nome/código de disciplina e dois departamentos; casos com caixa/acentos verificados |
| RF08–RF09 | Cinco critérios agregados preparados; nenhuma avaliação individual; contagem em todos os cartões |
| RF10 | Zero avaliações separado de avaliação negativa; busca sem correspondência explícita |
| RF11 | Chamada e Material conflitantes na fixture de Bruno, sem conclusão artificial |
| RF12–RF13 | Comparação lado a lado da mesma disciplina; apresentação por recomendação decrescente; nenhuma nota composta |
| RF14 | Cinco selects obrigatórios nas escalas aprovadas; texto explica sessão e e-mail confirmado no envio real |
| RNF02 | Cartões com 0/2 avaliações mostram contagem/insuficiência, sem valores dos critérios ou percentuais |
| Seções 6, 8 e 11 | Didática 1–5, Fácil/Médio/Difícil, Sim/Não, Material Não disponibiliza/Ruim/Médio/Bom; critérios neutros; sem campo livre |

Nenhuma regra, escala ou requisito foi alterado. A ordenação usa fixtures previamente
preparadas; agregação e desempates reais continuam responsabilidade do backend.

## Comandos e resultados

Ambiente: Windows, PowerShell, Node `v24.21.0`, npm `11.19.0`, Next `16.3.5`, React
`19.2.8`, TypeScript estrito, Tailwind 4 e Edge instalado no caminho padrão.

| Comando em `frontend/` | Resultado |
|---|---|
| `npm ci` | 358 pacotes instalados; lockfile preservado |
| `npm test` | 19 testes aprovados; escalas, validação e clientes HTTP existentes |
| `npm run lint` | Aprovado, sem diagnósticos |
| `npm run build` | Aprovado, incluindo TypeScript e nova rota; erro inicial de tipagem corrigido antes do build final |
| `npm run test:browser` | Aprovado no Edge fora do sandbox; suíte existente e nova verificação do protótipo |
| `git diff --check` na raiz | Sem erros de whitespace |

A primeira execução do navegador no sandbox falhou em `Page.enable`, antes de testar
telas. A execução fora do sandbox passou; o build final também foi verificado no
navegador após o ajuste da ordem inicial das fixtures.

Para reproduzir capturas no PowerShell, a partir de `frontend/`:

```powershell
$env:PREVIEW_DIR = Join-Path (Get-Location) '../docs/estudos/evidencias/issue-152'
npm run test:browser
```

O runner existente mantém controle das portas/processos e limpeza do perfil temporário.
Os novos testes verificam duas entradas da jornada, acesso à avaliação com dados
insuficientes, recarga/histórico, validação obrigatória, escalas exatas, teclado/foco,
estados alternativos, recuperação, IDs demonstrativos inválidos e ausência de chamadas
à API no navegador. São 9 telas/estados × 2 temas × 3 larguras = 54 combinações,
com um `h1`, indicação da etapa atual e ausência de rolagem horizontal em cada uma.

## Revisão e limitações

O diff foi revisado contra o escopo da issue, os requisitos e os padrões existentes.
Não foram incluídos arquivos de dependências, `.env`, segredos, artefatos de build,
backend, migrations ou mudanças de governança. A revisão não encontrou problemas
pendentes no escopo inspecionado; não equivale à aprovação humana.

- A entrega é um protótipo visual, não a aplicação da proposta às buscas e comparações
  reais. Os serviços existentes continuam disponíveis nas rotas originais.
- Conferir prévia não autentica nem registra avaliação. As regras de acesso são
  representadas em texto e o envio real segue o formulário existente.
- As verificações do formulário real usaram respostas controladas do runner existente.
  Não foi executada integração com FastAPI/PostgreSQL reais nesta tarefa.
- Não houve teste com alunos, leitor de tela ou auditoria completa de acessibilidade.
  A validação da jornada com alunos exigida pela Epic permanece trabalho separado.
- Carregamento/erro são estados visuais demonstrativos; não comprovam resiliência de
  rede do backend. Desempates são descritos, não exercitados por estas fixtures.

## Prévia da Pull Request

**Título:** `feat: prototipar jornada da entrada à avaliação (#152)`

**Origem:** `feature/152-prototipo-jornada-ux` · **Destino:** `develop`

### Objetivo

Adiciona um protótipo navegável em `/prototipo`, acessível pela página inicial,
para revisar entrada, busca, resultados, comparação e formulário antes da integração
da proposta às telas reais. Inclui buscas por professor/disciplina, estados vazios,
conflito, insuficiência, carregamento/erro e acesso à avaliação.

Reutiliza os cinco campos do formulário real e as escalas existentes. Dados
demonstrativos são identificados; a prévia não consulta a API nem envia avaliações.
Mantém RNF02, contagens, neutralidade e ordenação por recomendação sem alterar negócio.

Closes #152

Relacionado à Epic #144; esta PR não conclui a validação da Epic com alunos.

### Tipo de mudança

- [x] Feature
- [x] Documentação

### Validação

`npm test` (19 aprovados), `npm run lint`, `npm run build`, `npm run test:browser`
(suíte existente e jornada em 54 combinações) e `git diff --check` aprovados.
Seis capturas e instruções de reprodução em
`docs/estudos/verificacao-prototipo-jornada-issue-152.md`.
Sem execução de integração real com FastAPI/PostgreSQL ou validação com alunos.

### Checklist

- [x] Branch e destino seguem `CONTRIBUTING.md`.
- [x] Mudança limitada à Issue #152.
- [x] Documentação afetada atualizada.
- [x] Sem segredos, credenciais ou `.env`.
- [x] Mudanças aplicáveis verificadas localmente.
- [x] Nenhuma alteração de requisito, arquitetura ou governança.

A descrição acima é uma proposta local; publicação depende da confirmação do usuário.

## Correções após a revisão da PR #179

Preparadas localmente em resposta ao timeout do job Frontend e aos ajustes pedidos
na revisão técnica. A publicação original ocorreu após autorização do usuário;
esta rodada de correções aguarda uma nova confirmação antes de push/atualização da PR.

**Causa reproduzida do timeout.** O teste de cadastro aguardava somente a presença
do campo Nome no HTML e clicava imediatamente no botão. Next.js apresenta HTML
antes de hidratar os handlers React. Ao reter os scripts do cadastro em uma reprodução
local, o clique original causou navegação nativa GET, sem executar a validação de nome,
e terminou com o mesmo `Timeout: Informe seu nome`. O script temporário de diagnóstico
foi removido. Não há evidência de que a diferença entre Node 22 e 24 seja a causa.

**Correção.** O runner aguarda uma resposta observável da validação local usando
eventos sintéticos de submit com dados inválidos. Sem hidratação esses eventos não
provocam navegação; com hidratação a validação produz a mensagem esperada. O mesmo
procedimento é aplicado aos formulários real e demonstrativo de avaliação. Não foram
aumentados timeouts nem alteradas regras de cadastro, sessão ou envio.

O cenário de regressão retém scripts até que o HTML esteja disponível, comprova que
a validação React ainda não funciona, libera os scripts e verifica mensagem/foco,
permanência em `/cadastro` sem query e zero cadastros enviados para nome em branco.
Depois verifica que apenas as tentativas válidas de 422/202 chegam à API controlada.

**Revisão visual e navegação.** `CriteriosAvaliacao` remove `outline-none` e adiciona
`focus-visible:ring-2 focus-visible:ring-accent`. O contorno global já existente
permanece; o anel de 2 px na cor de destaque agora está explícito no componente.
O navegador verifica o foco por Tab e seu estilo nos dois temas e nas três larguras.
`href` omite parâmetros de valor vazio sem remover o contexto preenchido; os testes
verificam os links das 54 combinações da jornada, incluindo estados alternativos.

**Rastreabilidade da PR.** A descrição remota consultada já possui `Closes #152`
e referência à Epic #144, sem referência à #32. Não precisou ser corrigida e não
foi alterada nesta rodada.

**Validação desta rodada.** `npm test` (19 aprovados), `npm run lint`,
`npm run build` (incluindo TypeScript), `npm run test:browser` (Edge, cenário de
hidratação controlada, suíte existente e protótipo em 54 combinações) e
`git diff --check` passaram. Execução local com Node `v24.21.0`; o CI reportou
Node `v22.23.3`. A nova execução remota só poderá ocorrer após a publicação autorizada.
