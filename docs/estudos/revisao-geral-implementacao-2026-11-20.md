# Revisão geral — implementação em 20/11/2026

## Alvo e autoridade

Nicolas solicitou executar o trabalho pendente da Yasmin nesta revisão e deixar a
implementação pronta antes de tratar main/publicação. Base conferida com fetch:
`origin/develop@1817919`, sem atualizações desde a criação do worktree.
Branch local `codex/revisao-geral-final`; nenhum commit/push/PR/merge nesta etapa.
Alterações preexistentes no checkout principal não foram modificadas.

Consulta ao GitHub: não havia PR aberta de `ailoiol`. Escopo da #265 executado
conforme a issue vigente, reutilizando entregas já integradas. Não foi criado
código atribuído a uma PR inexistente nem alterada a responsabilidade no GitHub.

## Implementação consolidada

- Reenvio de confirmação na interface, com resposta neutra, retorno seguro e proteções
  existentes na API. Sem trocar provedor ou enviar email externo nos testes.
- Consulta privada e paginada das próprias avaliações, critérios e contexto institucional.
  Autor vem da sessão; exclusão lógica e no-store preservados.
- Home e catálogo com consultas reduzidas, estados de erro/vazio e cartões responsivos.
  Catálogo em lotes de 12, links públicos e paginação preservados; disciplinas longas
  no perfil expansíveis. Frase antiga da home e indicador curto restaurados por pedido.
- Espaçamento do contato no Sobre e alinhamento dos ícones corrigidos na prévia local.
- Atualização corretiva de Next/eslint-config-next 16.4.6 e lockfile validado no Docker.
- Dependência declarada do TestClient e correção da entrada do teste de migration SQLite.
- #265: matriz de campos/atores, necessidade técnica, limites e cinco regressões novas.
  Correção da permanência de dados antigos na interface de atendimento após perda de
  permissão; respostas atrasadas não repõem pedido/fila anteriores.

## Inspeção e findings

| Área inspecionada | Resultado / decisão |
|---|---|
| Auth, reenvio, schemas e retorno | Reutilizados token/hash, TTL, validação e orçamento da #266. Interface não cria usuário/retorno arbitrário; nenhum finding adicional confirmado |
| Avaliações, repository/schema/serviço e RF27 | Filtro de usuário no servidor, exclusão lógica, ordem determinística, paginação e schema sem autor. Testes com duas contas e tentativas de identidade por query aprovados |
| Comentários, denúncia, votos e papéis | Respostas públicas limitadas, autor/denunciante internos somente nos endpoints autorizados; preservada regra de agregados e impedimentos. Nenhuma exposição de conta confirmada nos cenários testados |
| Sessão no atendimento | Finding corrigido: revalidar ao retornar, limpar ao ocultar/revalidar e invalidar leitura/escrita obsoleta. Backend mantém a autorização existente |
| Catálogo e mobile | Finding corrigido: 100 cartões causavam páginas com mais de 23 mil px; lotes de 12 e agrupamento compacto reduzem altura sem omitir acesso ao restante |
| Infra local / migrations | Banco descartável novo migrado; não testado sobre o banco de catálogo da prévia; sem DDL ad hoc no produto |
| Dependências | Runtime npm consultado em 20/11: zero avisos. Ferramentas dev permanecem com ressalvas da auditoria anterior; sem afirmar segurança total ou versões de produção |
| Logs e dados privados | Campos de retorno, schemas e erros examinados; regressões da #266 reutilizadas. Não consultados logs reais de usuários ou painéis dos provedores |
| Transparência | Política complementada para RF27; Sobre/Termos mantêm vínculo interno e risco contextual, sem prometer anonimato absoluto. Sem alteração de acesso/retenção |

A revisão concentrou inspeção em arquivos alterados e fronteiras relacionadas:
routers, services, repositories, schemas, sessão/origens/erros/cache; telas de
conta/catálogo/home/atendimento e serviços frontend. As suítes ampliam regressão
para importação, moderação, retenção e concorrência. Não é prova exaustiva de todos
os caminhos nem parecer jurídico. Zero findings adicionais não é aprovação de PR.

## Evidências locais

- PostgreSQL 16 descartável novo, sem portas publicadas: migrations até head aprovadas.
- Backend Python 3.12: **461 testes, dois ignorados**; Ruff check, format e compileall aprovados.
- Frontend: **99 testes aprovados**, ESLint sem avisos, build Docker/TypeScript aprovados.
- Privacidade #265: cinco cenários HTTP novos aprovados; atendimento com perda de
  permissão, recuperação e resposta atrasada aprovado no navegador.
- Regressão completa de navegador do conjunto: **18 runners aprovados**, incluindo a nova regressão de revogação/resposta atrasada no atendimento e a paginação do catálogo em lotes de 12. Execução com fixtures HTTP sintéticas em Brave headless.
- Documentação: MkDocs strict aprovado; páginas históricas fora da navegação reportadas
  informativamente pelo MkDocs, sem erro de build.
- `git diff --check`: aprovado.

Logs/capturas locais em `output/revisao-2026-11-20/`, sem publicar segredos. `.env`
de testes ignorado pelo Git contém somente credenciais novas e descartáveis.
As verificações históricas de 18/11 não foram reclassificadas como execução hospedada.

## Implementação versus publicação

A implementação e a revisão local não exigem mais aguardar a PR da Yasmin.
A versão permanece preparada localmente para revisão humana e autorização própria
sobre commit/PR/main. A prévia usa catálogo autorizado do backup e dados de conta/
avaliações demonstrativos; isso não reproduz contas ou conteúdo real de produção.

Ficam para a próxima etapa: integração/aprovação de main, CI do commit final,
SHA realmente publicado, smoke tests hospedados, CORS/cookies/TLS/cache/CDN,
operadores/papéis efetivos, supervisão e purgas, logs/fornecedores e aceite da
release. Guardas/cotas provisórias e limites operacionais documentados não viram
requisitos novos ou bloqueios de implementação inventados. Canal/IA continuam
com flags existentes; nenhuma ativação ou alteração em Render foi executada.

Referências: [#265 e matriz de privacidade](privacidade-apis-265-revisao-final.md),
[histórico da revisão](revisao-final-local-2026-11-18.md),
[consolidação #168](../releases/2.0.0-resumo-revisao-168.md) e
[ressalvas operacionais #266](../seguranca/validacoes-pendentes-266.md).

## Preparação da PR autorizada

Após concluir a revisão local, Nicolas autorizou commit/push/PR com até quatro
commits. A branch foi renomeada para `feature/168-revisao-geral-final` para atender
ao Gitflow de `CONTRIBUTING.md`; destino `develop`. Os registros anteriores de
“sem commit/PR” descrevem o estado antes dessa autorização. Publicação/main e
aceite operacional permanecem fora desta preparação. Diretórios `output/`, bancos,
capturas temporárias e `.env` não integram os commits.
