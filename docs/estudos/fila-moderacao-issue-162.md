# Fila de moderação — Issue #162

Implementação de RF22 na interface do moderador, sobre a `develop` integrada em
`81e54be` (PR #192). Fontes: [requisitos](../requisitos.md),
[arquitetura](../arquitetura.md) e
[contrato das #160/#161](alinhamento-denuncias-issues-160-161.md).
Não modifica backend, contratos ou regras de produto.

## Análise e plano executado

O checkout inicial estava limpo na `develop`. As Issues #159 e #193 estavam abertas;
não havia componentes de comentários, denúncias ou moderação integrados no frontend,
nem branches remotas dessas interfaces identificadas na inspeção. Não se presumiu
conclusão de trabalho paralelo. As APIs da PR #192 já estavam disponíveis.

Foram reutilizados o App Router do Next.js 16.3.5, React 19, TypeScript estrito,
Tailwind 4, cabeçalho, fontes, tokens, `apiClient`, `ApiError` e o mecanismo de testes
Node/CDP/Edge existente. Os guias locais da versão instalada do Next.js foram
consultados antes do código. Nenhuma dependência foi adicionada.

O plano apresentado antes das alterações foi: serviço privado tipado, rota e
componentes da fila, testes de serviço/navegador/API real e documentação. A branch
local de trabalho é `feature/162-fila-moderacao`.

## Página e componentes

- `/moderacao`: composição no servidor, metadados sem indexação e nenhuma consulta
  privada durante geração do HTML. O conteúdo protegido é carregado no navegador.
- `app/moderacao/fila-moderacao.tsx`: acesso, filtros, seleção, carregamento,
  atualização, concorrência de consultas e retorno das ações.
- `app/moderacao/detalhe-moderacao.tsx`: texto completo, versão/estado/data, autoria
  interna, anterior do substituto, relatos por origem, decisões disponíveis e formulário.
- `components/cabecalho.tsx`: entrada “Moderação”, sem substituir navegação existente.
  A entrada identifica a rota, não concede permissão nem expõe dados privados.
- `lib/types/moderacao.ts`, `lib/services/moderacao.ts` e `lib/moderacao.ts`:
  contrato HTTP privado, validação de respostas, rótulos e mensagens de apresentação.

A lista usa prévias de três linhas e o painel mostra o texto completo. Em telas
estreitas, o painel fica abaixo da lista; ao selecionar, recebe foco para acesso
direto à análise. Em desktop há duas colunas. Há rótulos, regiões de estado/alerta,
foco visível e controles por teclado, nos temas existentes.

## API consumida

| Operação | Uso |
|---|---|
| `GET /api/moderacao/comentarios?estado=` | Acesso definitivo e fila; filtros vazio, `PENDENTE`, `PUBLICADO`, `SUSPENSO` |
| `GET /api/moderacao/comentarios/{id}` | Versão selecionada e, quando houver, versão anterior do substituto |
| `GET /api/moderacao/comentarios/{id}/denuncias` | Relatos e contagens do servidor, separados em autenticados e visitantes |
| `GET /api/moderacao/comentarios/{id}/decisoes` | Decisões ainda disponíveis no prazo do backend |
| `POST /api/moderacao/comentarios/{id}/acoes` | Apenas `acao` e `motivo`, aguardando a decisão real retornada |

As chamadas usam `credentials: include`. Leituras privadas usam `cache: no-store`.
O cliente HTTP recebeu opções facultativas de cache/cancelamento, preservando o
comportamento de todos os consumidores anteriores. As respostas são validadas em
runtime, incluindo associação à versão solicitada; TypeScript não substitui isso.
Não há persistência de texto, motivo, denúncias ou identidades em Web Storage.

O contrato de sessão existente informa somente `autenticado`; não informa papel
nem identidade. A interface não inventa um endpoint ou papel local. A autorização
é verificada pela API da fila e em cada operação. `401` orienta entrar e retornar
pelo menu; o contrato de retorno de login, restrito à avaliação, não foi ampliado.

Nome/e-mail internos somente aparecem após resposta autorizada. Textos são
renderizados pelo React, sem HTML injetado. Uma negação de acesso limpa os dados
privados da tela. Não são consumidos endpoints de denúncia pública ou agradecimentos
da #193, nem modificados os fluxos de comentários da #159.

## Estados e ações

- Carregamento e falha inicial são distintos de fila vazia. O filtro é enviado à
  API; não se inventa paginação, ordenação ou estado “denunciado” no backend.
- Pendentes oferecem aprovar/rejeitar; publicados com relatos oferecem manter/
  remover; suspensos oferecem restaurar/remover. Estados finais não oferecem ações.
- Motivo obrigatório, desconsiderando espaços, e seleção da ação impedem envio
  vazio. O payload não inclui identidade, permissão, contagem ou mudança de estado.
- Aprovação inicial não consulta denúncias. Falha de histórico não impede esse
  fluxo. Versões publicadas/suspensas aguardam a consulta de denúncias para análise.
- A resposta `200` informa o estado confirmado; a seleção e seus dados são removidos
  e a fila é consultada novamente. Se a atualização falhar, a decisão confirmada
  continua informada, junto da falha; a lista antiga não é reutilizada.
- `403` em uma ação não simula sucesso: informa que outro moderador deve analisar
  casos próprios, bloqueia novas ações nessa análise e revalida o acesso pela fila.
  Se a consulta também negar acesso, todos os dados privados são removidos.
- `409` informa mudança de estado e recarrega a fila. `404` trata indisponibilidade.
  `422` orienta corrigir o formulário. Falhas de rede/servidor não confirmam sucesso
  e exigem dados novamente consultados antes de outra ação.
- Consultas abandonadas são canceladas. Um número de geração impede resposta de
  seleção ou filtro anterior de substituir a seleção atual, inclusive após sair da rota.

O mapa de ações é apresentação do contrato, não autorização ou transação local.
O backend continua responsável pelos impedimentos, contagens, limiar, suspensão,
encerramento, auditoria e retenção. Sem identidade da sessão no contrato, não é
possível prever no cliente todo impedimento pessoal antes da primeira decisão;
nenhuma alteração de API foi feita para contornar essa limitação.

## Verificação

| Verificação | Evidência |
|---|---|
| `npm test` | 33 testes aprovados: 26 existentes e sete de serviços/apresentação da moderação |
| `npm run lint` | Aprovado, sem avisos na execução final |
| `npx tsc --noEmit` | Aprovado com configuração estrita existente |
| `npm run build` | Aprovado; inclui verificação TypeScript e rota `/moderacao` |
| `npm run test:moderacao`, HTTP controlado | Fila com três estados, vazio, carregamento, erro, seis ações, campos obrigatórios, `401/403/409/422/503`, atualização, consultas obsoletas, teclado, escape de texto e ausência de consumo da #193 |
| `npm run test:browser` completo | Aprovado: regressão existente de busca, acesso, avaliação e protótipo, seguida pela fila de moderação |
| Responsividade controlada | 18 combinações: três estados × 320/768/1280 px × claro/escuro, sem rolagem horizontal e com prévias limitadas |
| Mesmo runner com `MODERACAO_FIXTURE_FILE` | Navegador real → FastAPI existente → PostgreSQL 16 migrado: acesso negado a visitante/conta comum/não confirmada, seis ações, autoria e denúncia próprias bloqueadas |
| Responsividade com API real | Seis combinações de largura/tema, com capturas sintéticas inspecionadas |
| Conferência posterior no PostgreSQL | Seis decisões persistidas, relatos encerrados, texto rejeitado/substituído descartado, critérios preservados e impedimentos sem alteração de estado |
| MkDocs estrito, Python 3.12 | Aprovado com `mkdocs build --strict --site-dir /tmp/undb-site` em container descartável |

Os testes de navegador usam Edge headless e perfis isolados, conforme os runners
existentes. A versão controlada testa falhas e concorrência de consultas; não é
evidência de persistência. A versão real não substitui respostas da API e usa dados
sintéticos próprios, incluindo estados previamente preparados, sem afirmar nova
verificação do cálculo de suspensão já entregue nas #160/#161.

`npm run test:browser` inclui a regressão existente e a fila, sequencialmente,
para o CI continuar cobrindo a interface. `npm run test:moderacao` executa só a fila.

### Reprodução da integração real

Em banco PostgreSQL descartável chamado `moderacao_interface_test`, aplique as
migrations existentes e defina `SECRET_KEY`, `DATABASE_URL` e
`UNDB_INTEGRATION_TEST=1`. O backend deve permitir a origem `http://localhost:3100`
e, no teste HTTP local, usar `DEBUG=True` para o cookie de desenvolvimento.
Com as dependências de Python existentes, na raiz do repositório:

```text
python frontend/tests/moderacao-fixture.py preparar CAMINHO_TEMPORARIO/fixture.json
```

Inicie a API em `localhost:8000`. No frontend, após o build, defina
`MODERACAO_FIXTURE_FILE` para esse arquivo e execute `npm run test:moderacao`.
O runner inicia Next.js em 3100 e Edge em 9226; ambas as portas devem estar livres.
`BROWSER_PATH` permite outro Chromium; `PREVIEW_DIR` guarda capturas opcionais.
Depois execute o mesmo script Python com `verificar` e `limpar`, usando o mesmo
arquivo. O arquivo temporário contém somente tokens sintéticos de teste, não deve
ser versionado e é apagado na limpeza. O script recusa outro nome de banco ou
execução sem a marca explícita de ambiente de teste.

## Limitações e preservação de escopo

- O build inicial no sandbox não alcançou as fontes Geist existentes; executado
  com acesso à rede, passou. Não houve troca de fontes ou dependências.
- A automação CDP ficou bloqueada pelo sandbox; passou fora dele com perfil isolado.
- Capturas e tokens são de fixtures sintéticas, não usuários reais. Não houve teste
  em dispositivo físico ou leitor de tela. A homologação global permanece na #163.
- O backend e o contrato da PR #192 permanecem sem alterações. #159/#193 seguem
  com suas próprias interfaces; não se afirma que elas foram concluídas aqui.
- Nenhuma decisão essencial de produto ficou pendente nesta implementação.
- Sem push, PR, merge ou encerramento de Issue. As fixtures e os containers de
  teste são exclusivos desta tarefa e removidos após a verificação.
