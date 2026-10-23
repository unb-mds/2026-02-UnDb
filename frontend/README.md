# Frontend

Scaffold do frontend do UnDb com Next.js 16, TypeScript e Tailwind CSS.

## Execução local

**Pré-requisitos:** Node.js 20.9 ou superior com npm e o backend acessível pelo navegador.

```bash
npm ci
copy .env.example .env.local  # Windows
# cp .env.example .env.local  # Linux/macOS
npm run dev
```

A aplicação fica disponível em [http://localhost:3000](http://localhost:3000). Configure
`NEXT_PUBLIC_API_URL` em `.env.local` com a URL pública do backend. Para a execução local
documentada no repositório, o valor padrão é `http://localhost:8000`.

O App Router está em `src/app/`. Para alterar a página inicial, edite
`src/app/page.tsx`; o servidor de desenvolvimento atualiza a página automaticamente.

## Comandos disponíveis

- `npm run dev`: inicia o servidor de desenvolvimento.
- `npm run lint`: executa o ESLint.
- `npm run build`: gera o build de produção.
- `npm run start`: serve um build de produção já gerado.
- `npm test`: compila os módulos do formulário com TypeScript em diretório temporário e
  executa testes com o runner nativo do Node, sem novas dependências.
- `npm run test:browser`: verifica o formulário no Edge/Chromium headless com respostas
  controladas de teste; exige build padrão prévio, Node 22+ e portas 8000, 3100 e 9223 livres.
  No Windows usa o caminho padrão do Edge; em outros ambientes configure `BROWSER_PATH`.
  Esse comando não usa o backend real nem comprova persistência.

## Protótipo da jornada — Issue #152

### Testar com a base simulada pronta

O protótipo já inclui uma base fictícia em `src/app/prototipo/dados.ts`, carregada
automaticamente. Não é necessário criar banco, importar o SIGAA ou configurar `.env`.

| Dados disponíveis | Exemplos para testar |
|---|---|
| 6 professores fictícios | Ana de Computação, Ana de Matemática, Bruno, Carla, Daniel e Elisa. |
| 3 disciplinas fictícias | Algoritmos (`CIC-DEMO`), Estruturas de dados (`CIC-DEMO-2`) e Cálculo (`MAT-DEMO`). |
| Estados de avaliação | Dados suficientes com recomendação, conflito em critérios factuais, duas avaliações e ausência de avaliações. |
| Conta demonstrativa | Visitante, cadastro pendente de confirmação, conta confirmada e saída. Use `exemplo@aluno.unb.br` e uma senha fictícia de pelo menos 8 caracteres. |

Com Node.js 22 ou superior e npm, a partir da raiz do repositório:

```bash
cd frontend
npm ci
npm run dev
```

Como alternativa, com Docker aberto, execute **na raiz do repositório**:

```bash
docker compose up --build --no-deps frontend
```

Abra **http://localhost:3000/prototipo**. O comando Docker inicia somente o frontend,
sem API ou PostgreSQL; as páginas reais que dependem desses serviços não fazem parte
desse modo de teste. O build precisa de internet. Para parar esse modo Docker, use
Ctrl+C no terminal e `docker compose stop frontend`, se necessário.

Não existe login real de teste nem gravação em banco neste modo. Os exemplos já
estão disponíveis na busca. A conta simulada reinicia ao recarregar e a prévia da
avaliação não salva respostas. Para a rodada com alunos, registre o commit usado e
as observações conforme o roteiro da #153.

### Navegação e limites

Com `npm run dev` (ou `npm run start` após o build), abra
[http://localhost:3000/prototipo](http://localhost:3000/prototipo), também acessível
pelo link na página inicial. O protótipo funciona sem backend e identifica todos os
dados como demonstrativos fictícios. O cabeçalho do protótipo oferece busca e uma
entrada única “Entrar / Criar conta”, que vira “Minha conta” nos cenários simulados.
“Voltar ao sistema” leva às rotas reais, que dependem da API quando aplicável.

Na rodada de preparação da #153, experimente **Buscar professor → Ana → Avaliar nesta
disciplina → Conferir prévia da avaliação**. Os resultados já mostram as disciplinas
agrupadas por professor, com acesso direto à avaliação. As duas Anas fictícias têm
departamentos diferentes; uma oferece Algoritmos e Estruturas de dados, e a outra
oferece Cálculo. Elas permanecem registros separados.

A alternativa por disciplina permite buscar “Algoritmos”, comparar e ordenar por
recomendação antes de avaliar. “MAT-DEMO” encontra Cálculo, com ausência de avaliações.
Nome, departamento e código são identificados por rótulos; busca e organização dos
resultados permanecem na URL durante a navegação e o retorno. A opção de organizar
resultados por departamento/nome é uma proposta demonstrativa, não altera o ranking
da comparação nem os serviços reais.

No formulário, “Entrar ou criar conta para avaliar” abre a mesma área de conta do
cabeçalho. Ela reúne entrada e cadastro, Mostrar/Ocultar senha, estado do e-mail e saída.
Simular entrada representa uma conta já confirmada; simular cadastro apresenta e-mail
pendente, e a confirmação demonstrativa permite continuar. Entrada e confirmação
retornam ao ponto de origem, mantendo professor, disciplina e busca quando selecionados.
Use dados fictícios: não há criação de conta ou sessão real. O cenário de conta fica
somente em memória, é preservado na navegação interna e reinicia ao recarregar;
respostas do formulário de avaliação não são persistidas entre etapas. O protótipo
usa rótulos completos para Chamada e Recomendação, preservando os valores e escalas.

“Explorar estados de busca” reúne busca vazia, sem resultados, carregamento e erro
com recuperação. A proposta não inclui fotos do SIGAA ou novos dados de localização.

O protótipo não autentica, consulta a API, calcula agregados nem salva avaliações.
A comparação alterna entre apresentações preparadas da fixture; a regra real permanece
no backend. Os cinco campos reutilizam o componente do formulário real e suas escalas;
os rótulos explicativos são ativados somente no protótipo.
Critérios não aparecem abaixo de três avaliações; contagens e insuficiência permanecem visíveis.

`npm run test:browser` também verifica a jornada, os estados, o histórico/recarga,
as escalas, teclado e 72 combinações de tela/tema/largura (320/768/1280 px), incluindo
resultados com homônimos e a área de conta com/sem avaliação selecionada. Também verifica
os cenários visitante, e-mail pendente, e-mail confirmado, saída e retorno à avaliação.
Para gerar capturas locais durante essa verificação, configure `PREVIEW_DIR` com um
diretório de saída. Evidências, limites e prévia da PR estão em
[`verificacao-prototipo-jornada-issue-152.md`](../docs/estudos/verificacao-prototipo-jornada-issue-152.md).
O mapeamento desta adaptação aos relatos e o roteiro para registrar a próxima rodada
estão em [`ajustes-prototipo-jornada-issue-153.md`](../docs/estudos/ajustes-prototipo-jornada-issue-153.md).

## Execução com Docker — Issue #36

Na raiz do repositório, configure `backend/.env` conforme o [README principal](../README.md)
e execute `docker compose --env-file backend/.env up --build`. O frontend fica em
`http://localhost:3000`, junto da API e do PostgreSQL. Para trabalhar com recarga automática,
inicie somente `backend db` no Compose e use `npm run dev` nesta pasta.

A imagem usa Node.js 24 em Debian slim e build em múltiplas etapas. O Docker define
`BUILD_STANDALONE=true` para gerar `.next/standalone`; o container executa `node server.js`
como usuário `node`, sem root. `public/` e `.next/static/` são copiados explicitamente para
servir imagens, fontes e CSS. Dependências de desenvolvimento ficam no estágio de build,
incluindo Tailwind 4 e seu plugin PostCSS. Sem `BUILD_STANDALONE`, o build local continua
compatível com `npm run start`.

| Variável | Onde configurar | Momento e finalidade |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `.env.local` fora do Docker; argumento de build no Docker, interpolado do `backend/.env` pelo Compose | URL acessível ao navegador, incorporada ao JavaScript no build; padrão `http://localhost:8000` |
| `API_INTERNAL_URL` | Ambiente do servidor; definida pelo Compose como `http://backend:8000` | Lida em runtime apenas pelo servidor Next.js; fora do Docker pode ser omitida para usar a URL pública |
| `CORS_ORIGINS` | `backend/.env` | Origens autorizadas pela API; padrão `http://localhost:3000` |

Não coloque segredos em `NEXT_PUBLIC_*` ou em argumentos de build. Os arquivos `.env*`
são excluídos do contexto Docker. Alterar `NEXT_PUBLIC_API_URL` exige reconstruir a imagem;
passá-la somente ao container já construído não muda o JavaScript do navegador.

Para construir e executar somente a imagem, a partir da raiz (com API acessível no host):

```bash
docker build -t undb-frontend --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 frontend
docker run --rm -p 3000:3000 --add-host=host.docker.internal:host-gateway -e API_INTERNAL_URL=http://host.docker.internal:8000 undb-frontend
```

O build precisa de internet para dependências e fontes Geist. O container serve um build
otimizado, sem bind mount ou recarga automática; alterações de código exigem rebuild.
Essa composição é para validação local, sem definir provedor de deploy ou TLS.

As buscas são Client Components; detalhes e comparação consultam FastAPI em Server
Components por requisição. Por isso a entrega mantém servidor Next.js e não usa
`output: 'export'`. A análise e o estado da decisão estão no
[ADR 08](../docs/arquitetura.md#adr-08--execução-e-containerização-do-frontend).

## Padrão visual básico — Issue #31

Base implementada nesta entrega para orientar as próximas telas. A solicitação de
implementação da [Issue #31](https://github.com/unb-mds/2026-02-UnDb/issues/31) é a origem
deste trabalho; este registro não afirma aprovação coletiva nem fechamento da issue.
Os valores ficam centralizados em `src/app/globals.css`. O layout raiz usa
`src/components/cabecalho.tsx` para a navegação real; `/prototipo` herda um layout
próprio com a navegação e o estado de conta exclusivamente demonstrativos.

### Referência pesquisada

O [SuaGradeUnB](https://github.com/unb-mds/2023-2-SuaGradeUnB) atende ao mesmo contexto
universitário. Suas [notas da versão 1.0.0](https://github.com/unb-mds/2023-2-SuaGradeUnB/releases/tag/v1.0.0)
registram uma identidade com cores próximas às da UnB e nome associado à universidade.
Para o UnDb, a escolha é manter o azul já existente como destaque sobre uma base neutra,
e usar o nome do projeto no header. Não foram copiados componentes ou valores de cores
da referência. A paleta abaixo consolida os tokens que já existiam no UnDb.

### Paleta

| Token / classe Tailwind | Uso | Claro | Escuro |
|---|---|---|---|
| `--background` / `bg-background` | Fundo e campos | `#ffffff` | `#0a0a0a` |
| `--foreground` / `text-foreground` | Texto principal | `#171717` | `#ededed` |
| `--accent` / `text-accent` | Marca, destaque de navegação e foco | `#2563eb` | `#60a5fa` |

O tema acompanha `prefers-color-scheme`; `color-scheme` adapta também os controles nativos.
Use `text-foreground/70` para descrições e `/60` para metadados. `/50` fica reservado a
informação auxiliar; não o use para instruções essenciais. Bordas de cartões usam
`border-foreground/10`, campos `/20` e hover de cartões `/30` com `bg-foreground/[0.03]`.
Erros de busca usam `text-red-600 dark:text-red-400`, sempre acompanhados de mensagem.
Não use vermelho/verde, alertas ou ranking para julgar Dificuldade e Chamada: são
informações neutras, conforme [requisitos](../docs/requisitos.md).

### Tipografia

Geist Sans é a família principal, aplicada no `body`, com fallback Arial, Helvetica e
sans-serif. Geist Mono (`font-mono`) fica reservada a códigos e identificadores. Ambas
já são carregadas por `next/font` no layout raiz, sem nova dependência.

| Papel | Classes | Tamanho / entrelinha |
|---|---|---|
| Título da página inicial | `text-3xl font-semibold` | 30 / 36 px |
| Título das demais páginas | `text-2xl font-semibold` | 24 / 32 px |
| Marca no header | `text-xl font-semibold` | 20 / 28 px |
| Título de cartão de entrada | `text-lg font-medium` | 18 / 28 px |
| Corpo e campos de busca | `text-base` | 16 / 24 px |
| Descrições e navegação | `text-sm` | 14 / 20 px |
| Rótulos auxiliares | `text-xs` | 12 / 16 px |

Mantenha um `h1` por página e hierarquia semântica de títulos. Peso regular para texto,
`font-medium` para ações e `font-semibold` para títulos.

### Layout base e espaçamentos

```text
┌──────────────────────────────────────────────────────┐
│ UnDb                         Professores Disciplinas │ header: max-w-5xl
├──────────────────────────────────────────────────────┤
│         Título e descrição                           │
│         Campo de busca / conteúdo                    │ main: max-w-2xl
│         Lista de resultados / cartões                │
└──────────────────────────────────────────────────────┘
Comparações: o conteúdo pode ocupar max-w-5xl.
Em telas estreitas, navegação e cartões quebram em linhas.
```

- Header compartilhado em todas as rotas: marca ligada a `/`, navegação para
  `/professores` e `/disciplinas`, borda inferior, `px-4 py-3`, sem altura fixa.
- Buscas e detalhes: `mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10`.
  A largura máxima é 42 rem (672 px com raiz de 16 px).
- Comparação de professores: `max-w-5xl` (64 rem / 1024 px) e grade responsiva existente.
- Início: `max-w-2xl`, `gap-8 py-16`, cartões em uma coluna e duas a partir de `sm`.
  Página não encontrada: mesma largura, `gap-3 py-16`.
- Espaçamentos: 4, 8, 12, 16, 24, 32, 40 e 64 px, correspondendo às unidades
  Tailwind 1, 2, 3, 4, 6, 8, 10 e 16. Cartões de entrada usam `p-5` (20 px).
- Listas: `gap-2`, cartões `rounded-lg px-4 py-3`. Cartões de entrada: `rounded-xl`.
- Campos: `rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base`.
- Links e controles recebem contorno azul de 2 px no `focus-visible`, com afastamento
  de 4 px. Não remova essa indicação de navegação por teclado.

### Exemplo para novas telas

O header é herdado do layout; não o repita na página.

```tsx
<main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-4 py-10">
  <div>
    <h1 className="text-2xl font-semibold">Título da tela</h1>
    <p className="mt-1 text-sm text-foreground/70">Descrição da tarefa.</p>
  </div>
  {/* Conteúdo da tela */}
</main>
```

### Verificação

Execute `npm test`, `npm run lint` e `npm run build`, como no CI. Os testes cobrem a lógica
do formulário e o cliente HTTP; `npm run test:browser` verifica a interface e os estados de envio no CI, após o build, com Node 22 e Edge no runner Windows.
Esses comandos não substituem a integração com a API real. Para revisar a interface com `npm run dev`:

- confira início, buscas, detalhes, comparação e página não encontrada;
- confira temas claro e escuro e larguras de 320, 768 e 1280 px;
- navegue por Tab e confira foco, links do header e quebra de linhas sem rolagem horizontal;
- confira estados de carregamento, lista vazia e erro com o backend disponível/indisponível.

Verificação desta entrega (18/09/2026): lint e build de produção passaram. Uma checagem
pontual no Edge headless cobriu início, as duas buscas e página não encontrada nos dois
temas e nas três larguras acima (24 combinações), verificando ausência de transbordamento
horizontal, header, destinos de navegação, fonte e tema. O foco por Tab na página inicial
também foi verificado. As capturas móveis dos dois temas foram inspecionadas visualmente.
Essa checagem não adiciona uma suíte ao projeto e não cobre fluxos com dados do backend.

## Formulário de avaliação — Issues #42 e #116

Na consulta de um professor em uma disciplina, use **Avaliar este professor na disciplina**.
A rota `/professores/[id]/disciplinas/[disciplinaId]/avaliar` identifica professor e disciplina
pela API e oferece os cinco critérios obrigatórios, sem respostas predefinidas. Material
é convertido em disponibilidade e qualidade; **Não disponibiliza** envia `false`/`null`.
Não há comentário livre, histórico acadêmico nem comprovação de disciplina cursada.
Dificuldade e Chamada são apresentadas sem indicação de bom/ruim.

O envio está liberado para `POST /api/avaliacoes`. O cliente consulta a sessão existente,
envia o cookie com `credentials: include` e não envia identidade de estudante no JSON.
O servidor autentica novamente, exige e-mail confirmado e rejeita campos adicionais.
Só há sucesso após resposta válida da API. Erros preservam as respostas; o link para
entrar abre outra aba, mantendo o formulário preenchido.

A persistência usa `INSERT ... ON CONFLICT DO UPDATE` com a restrição única de
usuário/professor/disciplina já presente nas migrations. Reenvios preservam ID e data de
criação, substituem todos os critérios e atualizam `updated_at`, inclusive sob concorrência.

`npm run test:browser` usa respostas controladas para verificar UI, erros e recuperação.
A integração real tem um runner separado, sem mocks de API ou banco. Após instalar as
dependências do backend e gerar o build padrão do frontend, configure `DATABASE_URL`
para um PostgreSQL de testes, `SECRET_KEY`, `UNDB_INTEGRATION_TEST=1` e `BROWSER_PATH`
(caminho de Edge/Chrome; Edge padrão no Windows). Em `backend/`, com o venv ativado:

```sh
alembic upgrade head
python -m tests.integration_avaliacao
```

O runner exige portas 8000/3100/9223 livres, Node 22+ e banco migrado; cria fixtures
identificadas por UUID, inicia a API real e limpa somente seus dados/processos ao final.
`--api-only` executa sessão, validação e concorrência HTTP/PostgreSQL sem navegador.
O CI mantém um job específico com PostgreSQL 16 para o fluxo completo.

Veja escopo, resultados e limites em
[`verificacao-formulario-avaliacao.md`](../docs/estudos/verificacao-formulario-avaliacao.md).
