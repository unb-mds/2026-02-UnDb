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
Os valores ficam centralizados em `src/app/globals.css` e o header em `src/app/layout.tsx`.

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
do formulário e o cliente HTTP; `npm run test:browser` verifica a interface e o feature gate no CI, após o build, com Node 22 e Edge no runner Windows.
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

## Formulário de avaliação — Issue #42

Na consulta de um professor em uma disciplina, use **Avaliar este professor na disciplina**.
A rota `/professores/[id]/disciplinas/[disciplinaId]/avaliar` carrega a identificação pela
consulta institucional existente e oferece os cinco critérios de `AvaliacaoCreate`.
Todos são obrigatórios, sem escolha inicial; Material é convertido em disponibilidade
e qualidade, usando `false`/`null` para **Não disponibiliza**.

**Feature gate ativo:** o botão de envio está desabilitado e o handler interrompe a
submissão antes de consultar a sessão ou chamar `POST /avaliacoes`, inclusive por acesso
direto à rota. Os campos continuam disponíveis para validação local, com aviso explícito
de que as respostas não serão enviadas nem salvas. O gate é fixo no código, sem opção
pública de ativação; sua remoção pertence à #116 após validar a integração real.

A #42 entrega UI e validações locais. A #116 conecta sessão, API e banco, confirma
persistência e substituição sem duplicata e libera o envio, em coordenação com
#39/#47/#48/#49/#50. O cliente HTTP já preparado permanece coberto por testes unitários;
nenhum backend simulado é usado pela aplicação. O teste de navegador usa dados controlados
e verifica que o formulário não consulta sessão nem envia avaliações com o gate ativo.
Esses testes não comprovam integração real ou persistência.

Veja os cenários executados e o handoff em
[`verificacao-formulario-avaliacao.md`](../docs/estudos/verificacao-formulario-avaliacao.md).
