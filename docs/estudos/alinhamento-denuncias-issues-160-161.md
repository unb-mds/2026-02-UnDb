# Análise prévia e proposta de contrato — Issues #160/#161

**Estado:** `Proposed`; escolhas técnicas e perguntas abaixo aguardam alinhamento.
**Data da inspeção:** 01/11/2026.
**Resultado:** análise preparatória; RF21 não implementado nem validado.

## Fontes e evidências

- [Requisitos](../requisitos.md): RF20–RF22, AC21-01 a AC22-06 e R2-DEC-01 a
  R2-DEC-15. As regras de produto aprovadas permanecem a fonte de verdade.
- [Arquitetura](../arquitetura.md), [especificação](../../specs.md), `AGENTS.md`,
  `CLAUDE.md`, `CONTRIBUTING.md` e skills locais aplicáveis.
- Issues [#145](https://github.com/unb-mds/2026-02-UnDb/issues/145),
  [#154](https://github.com/unb-mds/2026-02-UnDb/issues/154),
  [#156](https://github.com/unb-mds/2026-02-UnDb/issues/156),
  [#160](https://github.com/unb-mds/2026-02-UnDb/issues/160),
  [#161](https://github.com/unb-mds/2026-02-UnDb/issues/161),
  [#162](https://github.com/unb-mds/2026-02-UnDb/issues/162) e
  [#163](https://github.com/unb-mds/2026-02-UnDb/issues/163), consultadas no GitHub.
- [PR #180](https://github.com/unb-mds/2026-02-UnDb/pull/180): integrada em
  `5360ff46bb390c7e0ff26f5849257cf77727d1a0`; detalha produto, sem aprovar schema.
- [PR #191](https://github.com/unb-mds/2026-02-UnDb/pull/191): integrada em
  `4126897e89e119696f3c137c2491771959f52bbd`, base `origin/develop` inspecionada.
  A revisão disponível registra aprovação humana. Resultados descritos na PR
  são evidência histórica, não testes reexecutados nesta análise.

O checkout inicial estava limpo em `feature/186-integracao-visual`, em `edd9188`,
sem a #156. `git fetch origin` confirmou a base integrada mais recente. A branch
`feature/160-denuncia-conteudo` foi criada a partir dela, preservando a branch
anterior. Não foi realizado merge, push, PR ou alteração de Issues.

A #161 estava aberta, com zero comentários. A busca por PRs de denúncia/moderação
não identificou implementação adicional; a busca por branch contendo `161` não
retornou resultados. Isso não comprova ausência de trabalho não publicado.
Na base integrada não foram encontrados modelos, routers ou serviços de denúncia
e moderação. A seção de contratos da #156 em `specs.md` declara explicitamente
que os contratos RF21/RF22 ainda não estão definidos.

## O que pode ser reutilizado

| Componente integrado | Uso na #160 e limite observado |
|---|---|
| `ComentarioVersao.id` | UUID identifica uma versão; não usar o ID da avaliação como alvo |
| `ComentarioVersao.avaliacao_id` e `substitui_id` | Associação à avaliação e à versão substituída |
| `EstadoComentario` | `PENDENTE`, `PUBLICADO`, `SUSPENSO`, `REMOVIDO`, `RETIRADO`, `SUBSTITUIDO`; não criar enum paralelo |
| `comentario_repository.listar_publicados` | Consulta pública filtra `PUBLICADO`; suspensão pode reutilizar esse filtro |
| `ComentarioPublicoResponse` | Retorna somente `id`, `texto`, `created_at`; preservar privacidade |
| `obter_sessao_opcional` | Sessão válida identifica conta sem exigir e-mail confirmado |
| `comentario_service.retirar` | Retirada já existe; precisa integrar encerramento na mesma transação |
| Migration `20261024_01` | Base de comentários, dependente de `20260921_01`; não editar migration aplicada |
| `tests/test_comentario.py` | `unittest`, HTTP ASGI e SQLite em memória; ampliar a estrutura existente |
| CI do backend | Testes determinísticos, migrações e consistência com PostgreSQL 16 |

Não existe papel de moderador no modelo `Usuario`. Não existem aprovação,
rejeição, manutenção, restauração e remoção humanas implementadas nessa base.
`texto` é obrigatório e tem tamanho mínimo no modelo/migration da #156: o descarte
aprovado exige alinhamento sobre sua representação física na #161.

## Regras compartilhadas já aprovadas

- Apenas versões textuais são denunciáveis; critérios estruturados não são alvos.
- Contas confirmadas ou não e visitantes podem registrar motivos da lista RF21.
- Uma denúncia aberta por conta/versão; visitantes podem repetir, sem deduplicação
  por navegador. A fila separa origens e contagens.
- Suspensão por 50 contas autenticadas distintas com denúncias abertas da mesma
  versão publicada. Visitantes e denúncias encerradas não contam.
- Suspensão oculta o texto público, conserva o texto para revisão e preserva notas.
- Denúncias e identidades são privadas; somente moderadores autorizados consultam
  registros internos, respeitando impedimento sobre comentário/denúncia próprios.
- Decisão humana encerra as denúncias relacionadas; retirada encerra como
  `conteúdo retirado`; substituição aprovada encerra como `versão substituída`.
- Denúncias encerradas são descartadas, sem arquivo permanente. Decisões duram
  sete dias; texto removido/retirado dura sete dias; substituído/rejeitado não é
  conservado. Estados do produto não impõem enums ou tabelas específicos.
- Suspensão pelo limiar e remoção humana de denunciado geram agradecimento às
  contas relacionadas com denúncia aberta; apagar após primeira exibição.
- Não há consulta pública de denúncias nem painel posterior do denunciante.

## Proposta técnica conjunta para revisão

Esta seção não é contrato aprovado e não autoriza implementação dependente.
Mantém FastAPI, SQLAlchemy síncrono, PostgreSQL, Alembic, Pydantic e as camadas
existentes. Não requer biblioteca, provedor ou serviço novo.

### Persistência e estados

1. Uma tabela `denuncias` com UUID próprio, FK obrigatória `comentario_versao_id`,
   FK opcional `denunciante_id` para `usuarios`, motivo fechado obrigatório e
   `created_at` com fuso. Conta nula representa visitante. Não coletar IP,
   fingerprint ou identidade adicional do visitante.
2. Cada linha representa uma denúncia **em aberto**. Encerramento remove a linha
   na transação da ação correspondente; não persistir linhas `ENCERRADA` nem
   snapshots de denúncias em auditoria. O registro aberto contém versão, ator
   quando existir, motivo, data e estado inicial implícito. A decisão tem seu
   registro separado e prazo próprio.
3. `UNIQUE(comentario_versao_id, denunciante_id)` impede repetição autenticada;
   valores nulos permitem repetições de visitantes no PostgreSQL. O índice atende
   à consulta por versão e à duplicidade; não criar outro índice equivalente.
   FKs não devem apagar registros silenciosamente como substituto do encerramento.
4. Reutilizar `EstadoComentario`; responsabilidade da #161 representar rejeição,
   descarte do texto e retenção sem contornar constraints da #156. Não incluir
   texto ou denúncias encerradas nos registros privados de decisão.
5. Agradecimentos persistidos por conta, versão e evento, sem identidade de autor
   ou outros denunciantes. A apresentação e confirmação de primeira exibição
   precisam de contrato próprio; nenhuma leitura pública pode consumir mensagens.

Os atributos propostos dependem da PK de sua própria entidade; identidade nominal
continua em `usuarios`, texto em `comentario_versoes`. Não duplicar nomes, e-mails,
texto ou contagens derivadas em `denuncias`. A contagem deve ser calculada sobre
registros abertos. O modelo físico, inclusive agradecimentos e decisões, precisa
de aceite conjunto antes da migration.

Alternativa considerada: armazenar denúncias abertas e encerradas com enum e índice
único parcial. Ela exigiria apagar as encerradas imediatamente para cumprir
R2-DEC-14; não fornece um arquivo permitido. Recomenda-se representar apenas as
abertas, reduzindo o risco de contagem ou retenção indevida. Isso é uma escolha
técnica proposta, não alteração do ciclo de vida aprovado.

### Concorrência e integração

- Repositório bloqueia a linha da versão para serializar registro, decisão,
  retirada e substituição; todas essas operações precisam seguir a mesma ordem.
- Na mesma transação: validar alvo e estado, identificar origem pela sessão,
  rejeitar duplicidade, inserir, contar `DISTINCT denunciante_id` não nulos e,
  quando aplicável, mudar `PUBLICADO` para `SUSPENSO` e criar agradecimentos.
- Encerramento é operação interna compartilhada com a #161 e a retirada da #156,
  sem `commit` próprio. Não criar endpoint público de encerramento/restauração.
- Codificações propostas de causa de encerramento: `MANTIDO`, `RESTAURADO`,
  `REMOVIDO`, `CONTEUDO_RETIRADO`, `VERSAO_SUBSTITUIDA`. Correspondem a ações,
  sem presumir que remoção declara toda denúncia procedente.
- Na #161, manter/restaurar/remover encerra as denúncias da versão analisada;
  aprovar substituto encerra as da anterior; rejeitar outro texto não as encerra.
- Aprovação inicial de comentários na #161 deve poder operar sem denúncias.
  A conclusão da #160 exige teste real dessas integrações, não apenas mocks.

### API candidata

| Operação proposta | Entrada / saída | Acesso |
|---|---|---|
| `POST /api/comentarios/{versao_id}/denuncias` | Somente `motivo`; `201` com mensagem de confirmação, sem protocolo ou identidade | Sessão opcional; não exigir e-mail confirmado |
| `GET /api/moderacao/comentarios/{versao_id}/denuncias` | Registros abertos separados por origem e contagens; identidades internas autenticadas | Moderador confirmado e autorizado, conforme dependência única da #161 |

Motivos candidatos como códigos técnicos: `OFENSA_PESSOAL`, `XINGAMENTO`,
`PALAVRAO`, `AMEACA`, `DISCRIMINACAO`, `EXPOSICAO_DADOS_PESSOAIS`, `SPAM`.
Não aceitar texto livre, `usuario_id`, origem, estado ou contagem enviados pelo cliente.
Erros propostos: `422` para motivo/schema inválido; `404` para alvo inexistente ou
indisponível; `409` para denúncia autenticada já aberta; `401`/`403` para consultas
internas sem autenticação/permissão. Esses códigos e payloads aguardam alinhamento.
Não adicionar consulta pública de denúncias ou exposição de contagens internas na
resposta pública de comentários.

## Decisões necessárias antes do código dependente

| ID | Pergunta / encaminhamento | Impacto |
|---|---|---|
| PD-160-01 | Existe contrato da #161 em trabalho não publicado? Se houver, fornecer referência. Caso contrário, aprovar ou corrigir a proposta conjunta acima, incluindo persistência, transações, encerramento, rotas e erros. | Evita modelos/enums/endpoints paralelos |
| PD-160-02 | Uma versão já `SUSPENSO` ainda aceita novas denúncias por UUID conhecido, ou registro só é permitido enquanto `PUBLICADO`? Pendentes nunca publicados não são expostos pela API pública. | Define elegibilidade sem escolher comportamento de produto por suposição |
| PD-160-03 | Qual entrega da #161 fornecerá papel/dependência de moderador, decisões, descarte e agradecimentos? Se ainda não existir, confirmar divisão de trabalho; incorporar suas ações à #160 exigiria ampliação explícita do escopo. | Consulta privada e integração não podem ser declaradas concluídas sem isso |

As regras de produto existentes não precisam ser reaprovadas. Não há bloqueio pela
lista de filtro nem pela ausência de IA. A limitação de identificar impedimento de
visitante permanece a aprovada; não acrescentar coleta de identidade.

## Verificação necessária após o alinhamento

- Ampliar testes existentes: alvo textual válido/inexistente/não elegível,
  visitante, conta não confirmada, duplicidade e vínculo exato da versão.
- Cobrir 49/50 contas, repetições, visitantes, versões distintas, encerramento e
  nova denúncia após decisão, sem contagem ou suspensão herdadas.
- Cobrir identidade privada, acesso autorizado/não autorizado, impedimentos,
  retirada/substituição, agradecimento após próximo acesso e consumo após exibição.
- Usar PostgreSQL para concorrência entre denúncia, suspensão, decisão e retirada,
  constraints, upgrade/downgrade/upgrade e `alembic check`.
- Executar suíte do backend, compilação e Docker Compose conforme CI; não afirmar
  validação de RF21/RF22 antes da implementação e integração.

Nesta análise foram inspecionados código, testes, migration e workflow existentes.
Os três links locais do documento foram verificados, assim como a marcação
`Proposed` e os três identificadores de pendências. `git diff --check` e
`git diff --cached --check` passaram; o diff documental foi revisado integralmente.
Nenhum teste funcional foi executado. O Docker não estava disponível: pipe
`docker_engine` ausente; a leitura
da configuração do Docker também foi negada pelo ambiente restrito. Python
disponível no PATH é 3.14; o launcher `py` não enumerou instalações. Esses fatos
não comprovam regressão do produto nem validam o fluxo solicitado.

Este documento é a única alteração preparatória. Nenhuma migration, endpoint ou
funcionalidade foi adicionada. RF21 permanece pendente de alinhamento e execução.
