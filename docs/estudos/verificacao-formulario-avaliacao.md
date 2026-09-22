# Verificação do formulário de avaliação — Issue #42

## Escopo e evidências

Implementação exclusivamente de frontend, conforme orientação explícita do responsável
em 22/09/2026 após constatar que as dependências de escrita não estavam implementadas.
Base: `origin/develop`, commit `0402064`. Branch: `feature/42-formulario-avaliacao`.

Foram consultadas integralmente as issues #42, #14, #29, #31, #38, #39, #47, #48, #49 e #50,
seus comentários, PRs recentes, branches remotas e histórico atualizado com `git fetch`.
Nenhum push, publicação de branch, PR ou merge faz parte desta entrega.

| Fonte verificada no GitHub em 22/09/2026 | Estado e efeito na implementação |
| --- | --- |
| [#42](https://github.com/unb-mds/2026-02-UnDb/issues/42) | Aberta; formulário com cinco critérios, sessão e envio real |
| [#14](https://github.com/unb-mds/2026-02-UnDb/issues/14) | Aberta; escrita pendente em #39/#42/#50 |
| [#29](https://github.com/unb-mds/2026-02-UnDb/issues/29), [#31](https://github.com/unb-mds/2026-02-UnDb/issues/31) | Fechadas; estrutura, tema, tipografia e padrões existentes reaproveitados |
| [#38](https://github.com/unb-mds/2026-02-UnDb/issues/38) | Fechada; escalas conferidas contra `AvaliacaoCreate` e enums reais |
| [#47](https://github.com/unb-mds/2026-02-UnDb/issues/47) | Fechada; identidade por sessão no servidor e cookie HttpOnly |
| [#48](https://github.com/unb-mds/2026-02-UnDb/issues/48), [PR #107](https://github.com/unb-mds/2026-02-UnDb/pull/107) | Cadastro integrado em develop |
| [#49](https://github.com/unb-mds/2026-02-UnDb/issues/49), [PR #114](https://github.com/unb-mds/2026-02-UnDb/pull/114) | Sessão integrada; comentário de aceite separa explicitamente o POST futuro |
| [#39](https://github.com/unb-mds/2026-02-UnDb/issues/39), [#50](https://github.com/unb-mds/2026-02-UnDb/issues/50) | Abertas, sem PR aberta; router vazio, sem contrato de resposta implementado |

Não foi encontrado trabalho prévio da #42 nas branches, PRs ou commits consultados.
O padrão adotado segue `CONTRIBUTING.md`, o template e PRs #103/#104/#107/#114:
branch `feature/<issue>-<descricao>`, título/commit `feat(frontend): ... (#42)` e
descrição com Objetivo, Tipo de mudança, Validação e Checklist.
A prévia deve usar **Refs #42**, sem fechamento automático enquanto a integração estiver bloqueada.

## Solução

- Link da consulta agregada para a rota de avaliação do mesmo professor/disciplina.
- Identificação obtida da API institucional existente, sem aceitar nomes arbitrários do usuário.
- Cinco selects nativos obrigatórios, sem valores predefinidos; labels acessíveis e foco compartilhado.
- Didática 1–5; Dificuldade `FACIL`/`MEDIO`/`DIFICIL`; Chamada e Recomenda booleanos.
- Material tem quatro opções visuais e produz `disponibiliza_material` + `qualidade_material`:
  Não disponibiliza → `false`/`null`; Ruim/Médio/Bom → `true` + `RUIM`/`MEDIO`/`BOM`.
- Sessão consultada no navegador e POST com `credentials: include`; identidade nunca vem do formulário.
- Respostas mantidas após erro, bloqueio de envios simultâneos e anúncio acessível de resultados.
- Tratamento de 401, 403, 404/405, 422 com detalhes por campo, 429, 5xx, rejeições adicionais e falha de rede.
- O cliente conserva detalhes retornados pela API; a tela não transforma rejeição em sucesso.
- Confirmação visual somente depois de resposta bem-sucedida; sem contrato inventado para distinguir criação/substituição.
- Sem histórico acadêmico, verificação de disciplina cursada, comentário livre ou nota composta.
- Dificuldade e Chamada usam a mesma apresentação neutra dos demais controles, sem escala de bom/ruim.

## Comandos e resultados

Executados no diretório `frontend/`, com Node `v24.21.0`:

| Comando | Resultado |
| --- | --- |
| `npm test` | 18 testes aprovados; inclui as 240 combinações válidas, entradas inválidas, booleanos, material, payload, credenciais e erros HTTP |
| `npm run lint` | Aprovado |
| `npm run build` | Aprovado, incluindo a rota dinâmica `/professores/[id]/disciplinas/[disciplinaId]/avaliar` |
| `npm run test:browser` | Edge headless: navegação, obrigatoriedade, cookie HttpOnly de teste, payload, sucesso controlado 201/200, bloqueio durante envio, 401/403/422/404/503, sessão ausente, preservação de respostas e ausência de overflow em 320/768/1280 px nos dois temas |
| `git diff --check` | Aprovado |

O teste de navegador precisa do build padrão, portas 8000/3100/9223 livres e Node 22+.
`BROWSER_PATH` permite selecionar Edge/Chromium fora do caminho padrão do Windows.
O runner inicia serviços locais de teste e encerra seus processos; o perfil do navegador
é temporário e exclusivo. Não utiliza perfil pessoal ou dados reais.
A primeira execução no sandbox falhou por timeout de `Page.enable`; a execução fora do
sandbox foi aprovada. Não é falha do formulário.

Não havia framework de testes de frontend. Os novos testes usam TypeScript já instalado,
runner nativo do Node e protocolo nativo de automação do navegador, sem adicionar dependências.
O CI executa `npm test`; o teste de navegador permanece opcional e exige navegador instalado.

## Limites: integração real ainda bloqueada

**Os testes controlados não comprovam integração com FastAPI, persistência ou substituição.**
Nenhum backend simulado é usado pela aplicação: apenas os testes fornecem respostas fictícias.

- `backend/app/routers/avaliacoes.py` contém somente `APIRouter(prefix="/avaliacoes", ...)`.
  Não há handler POST, schema de resposta ou operação de criação/substituição integrada.
- `specs.md` descreve prefixo geral `/api`, enquanto #42 e o router atual indicam `/avaliacoes`.
  Foi seguido o destino explícito solicitado para #42. #39 deverá consolidar o contrato.
- Não é possível validar sucesso, substituição, concorrência ou rejeições reais do POST ainda inexistente.
- Python não está instalado neste host: `python --version`, fora do sandbox, retornou
  `Python was not found`. Docker também não está disponível no PATH. Portanto a suíte
  `python -m unittest discover -s tests -v` não pôde ser executada neste ambiente.
- Backend, modelos e migrations não foram alterados, conforme escopo confirmado pelo responsável.

## Handoff para #39/#50 e aceite de #42

1. Implementar o POST e consolidar o caminho, status e corpo da resposta.
2. Aplicar as dependências de sessão/e-mail confirmado entregues por #49.
3. Garantir substituição e unicidade conforme #50, incluindo concorrência.
4. Conferir o cliente contra o contrato final; hoje ele aguarda resposta JSON bem-sucedida
   e não lê campos de criação/substituição não definidos.
5. Executar formulário → API real → banco, cobrindo cadastro/login, sessão ausente/inválida/expirada,
   e-mail não confirmado, entrada inválida, criação e segundo envio válido sem nova linha.
6. Só então avaliar a conclusão integral da Issue #42. Esta entrega não solicita seu fechamento.
