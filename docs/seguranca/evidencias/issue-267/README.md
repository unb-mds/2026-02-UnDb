# Evidências da recuperação isolada — #267

Data: **17/11/2026**. Base: `develop@cea7d6bdd01aedce51ce8db857377a483ed72e49`,
com #280 integrada. Ensaio executado antes do commit; hashes dos executáveis,
imagem, versões e horários UTC estão em [resultados.json](resultados.json).
Autorização: solicitação desta sessão e escopo vigente da
[#267](https://github.com/unb-mds/2026-02-UnDb/issues/267), atribuída a Gabriel.
Foram lidos o corpo atual e os três comentários, além de #266, #168, #260,
#171, #262 e #263 e dos documentos de hospedagem/continuidade/manutenção/retenção.
Checklists jurídicos históricos incompatíveis não foram transformados em gates.

Continuação autorizada em 17/11/2026: o usuário solicitou **um único commit, push,
PR para develop, merge e encerramento da #267**, deixando explícitas as pendências
operacionais já apresentadas. Isso autoriza o encerramento da entrega técnica com
ressalvas; não comprova canal, backup real ou diário operacional nem dispensa checks
e revisão do repositório. Resultado de publicação/merge deve ser conferido na PR.

## Resultado e alcance

Ensaio aprovado em Docker Desktop local, PostgreSQL **16.15**, Python **3.12.16**.
Rede interna exclusiva, sem portas publicadas; dados do cluster, dump e fixtures
em `tmpfs`. Fonte `undb267_disposable_source` e destino
`undb267_disposable_restore`, criados vazios em cluster novo. Nenhum banco, volume,
conta, log ou painel de produção foi acessado. A imagem contém somente dependências;
backend/migrations/testes da base local são montados para leitura.

Verificações executadas:

- `alembic upgrade head` e `alembic check` na origem; revisão **20261117_05**
  e `alembic check` no restaurado, sem diferença em relação ao modelo.
- `pg_dump -Fc --no-owner --no-acl`, arquivo `0600` em diretório `0700`,
  `pg_restore --list` e `pg_restore --exit-on-error` no destino distinto, retornos zero.
- Descoberta dinâmica de **26 tabelas**, incluindo Alembic; comparação de todas
  as linhas/colunas e contagens, não apenas uma quantidade fixa do ensaio anterior.
  PKs, FKs, unicidade, CHECKs, índices, nulidade/defaults, enums e persistência
  refletidos; 58 FKs/UNIQUEs/CHECKs comparados. Algumas tabelas sem fixtures estão
  vazias: isso comprova seu schema, não todas as suas jornadas.
- Fixtures de catálogo/turma/vínculos, conta e ciência dos Termos, avaliações,
  versões, votos, sessões/tokens, registros de acesso e pedido/eventos/hash de
  acompanhamento. Relações exercitadas pela consulta e escrita da aplicação.
- Sete eventos ocorridos **depois** do dump foram aplicados na origem e depois
  reaplicados no destino: exclusão de conta, exclusão de avaliação, retirada de
  comentário, revogação de papel e revogações de sessão, recuperação e confirmação.
  Cópia antiga inicialmente contém o estado anterior: não seria segura para liberação.
  Reaplicação conserva datas/janelas e efeitos; repetição verifica idempotência.
- Jornada HTTP pelos routers/serviços reais via `TestClient`, **com PostgreSQL
  restaurado**, sem substituir banco, autenticação ou limitador: busca → agregado
  → cadastro/ciência → confirmação → login → avaliação → agregado atualizado →
  voto/retirada → logout. Somente transporte de e-mail usa memória, sem envio real.
- Sessão e tokens revogados recusados; conta excluída não autentica; papel revogado
  não modera; outra conta não exclui avaliação alheia; atendimento não autorizado
  negado; origem externa negada; cookie Secure/HttpOnly/SameSite e no-store conferidos.
  CHECK, FK, UNIQUE, NOT NULL e par de ciência dos Termos exercitados com escritas inválidas.
- Relógio sintético na fronteira de sete dias: conteúdo existe imediatamente antes
  e é purgado na fronteira; votos dependentes também. Retirada de texto conserva
  critérios, acesso vencido é removido e vigente permanece. Conta mínima/pedidos
  não recebem prazo de descarte inventado. O diário não contém textos ou credenciais.
- Containers e rede próprios removidos no `finally`, eliminando cluster/bancos,
  dump, diário, fixtures e conexões. Conferência posterior por label sem recursos
  remanescentes. Não foi criado volume persistente nem removido recurso preexistente.

Limites: comparação lógica de valores/schema, **não igualdade física/byte a byte**.
O PostgreSQL reescreve casts textuais equivalentes em CHECKs `ANY(ARRAY...)`; o
comparador normaliza apenas coerções literais de texto. Antes do replay todos os
valores são comparados; depois dele `updated_at` técnico de avaliações/comentários
pode refletir a nova escrita, enquanto datas de exclusão/purga e outros valores
continuam comparados. O ensaio não comprova restauração externa, permissões reais,
RPO/RTO, backup automático, cobertura de logs/provedores ou jornada de navegador
com o banco restaurado. Não abre o canal de titulares nem autoriza publicar a cópia.

## Reprodução

Na raiz de um checkout próprio da base atual, com Docker local acessível e Python:

```bash
docker build -f scripts/recovery.Dockerfile -t undb267-disposable-tools:local .
python scripts/recovery_drill.py --confirm-disposable --image undb267-disposable-tools:local --output /caminho/novo/resultados.json
```

Use destino **novo**, com diretório existente, adaptado ao sistema operacional.
Na execução registrada, foi usada a tag `undb267-disposable-tools:20261117` e saída
fora do repositório; só o relatório agregado foi copiado para cá. A imagem deriva
de `python:3.12-slim` com `backend/requirements{,-dev}.txt`, sem arquivo `.env`,
chaves ou dados. Dependências de runtime têm versões flutuantes no projeto;
`pip freeze` e digest da imagem registram o ambiente realmente executado.

O runner recusa falta de confirmação, sobrescrita do relatório e endpoint Docker
remoto. Não aceita URLs, dumps, volumes ou bancos externos. Cria rede/containers
com nomes aleatórios `undb267-disposable-*` e label `undb.issue=267`; só remove os
nomes que criou, inclusive em falha de etapa. A imagem fornecida não é removida
pelo runner, pois pode ser preexistente. Após o ensaio, remova apenas a imagem de
ferramentas **que você criou exclusivamente para ele**. Nesta sessão sua tag/digest
foram conferidos antes do descarte, sem apagar imagens preexistentes ou fazer prune.

Em encerramento abrupto do processo, conferir os nomes/labels do próprio ensaio
antes de limpar recursos; nunca usar `prune` nem apagar por prefixo sem conferir
propriedade. O relatório registra eventual falha de limpeza com o nome correspondente.
Quem controla o daemon Docker pode inspecionar conexões sintéticas enquanto o
container existe; o ensaio não é um cofre de segredos reais. Não usar dados reais.

## Checks e tentativas

Resultados finais e comandos estão em [verificacoes.json](verificacoes.json).
As tentativas anteriores permanecem resumidas em [tentativas.json](tentativas.json),
sem dumps, linhas de banco, tokens, senhas ou logs brutos.

- As quatro primeiras tentativas pararam na comparação textual de casts dos
  CHECKs. Diagnóstico de **ensaio**, sem defeito de constraint/produto comprovado.
- A quinta passou o restore, mas comparava também `updated_at` técnico de uma
  reaplicação em outro instante. Corrigida a comparação de efeitos/janelas;
  nenhuma alteração de serviço de produção.
- A sexta passou todas as etapas. A final repete apenas após fortalecer a recusa
  de Docker remoto e a limpeza em falha de inicialização. Recursos removidos nas
  tentativas, inclusive após a interrupção da conversa.
- Regressões selecionadas: **31 aprovadas, 9 puladas**, 40 descobertas. As nove
  exigem URL PostgreSQL com nomes/hosts específicos; o container SQLite sem rede
  não fornece essa configuração. Não contabilizadas como aprovadas. O ensaio
  acima fornece a evidência PostgreSQL própria da #267, sem repetir a CI inteira.

## Matriz dos critérios vigentes da issue

| Critério | Evidência | Estado / insumo que falta |
|---|---|---|
| Canal privado, recepção e acompanhamento de Nicolas; interrupção/reversão | [Roteiro](../../../operacao/incidentes-recuperacao.md), hospedagem/manutenção e resposta de Nicolas nesta sessão | **Parcial:** roteiro e modelo prontos; confirmar Gabriel/Vinicius, canal, participantes e como Nicolas acompanha. Não há interruptor global comprovado; operação confirma mecanismo/intervenção antes de executar |
| Backup realmente disponível: cobertura, acesso, período, limites e restauração | Relato de Nicolas, distinção recurso/plano/capacidade e roteiro existente | **Parcial:** cópias manuais no Docker relatadas; faltam cobertura/origem/formato, local protegido, histórico recuperável, acessos e recuperação de uma cópia real. Automação não comprovada |
| Restaurar isolado com schema/vínculos e jornada | `resultados.json`: verify, replay, journey e Alembic | **Atendido no ambiente sintético autorizado:** destino novo e distinto, dados e controles conferidos; sem inferir produção |
| Data, versão, resultado, descarte e tratamento de exclusões antes da liberação | Manifesto, scripts, replay/retention, limpeza e roteiro | **Ensaio e descrição atendidos; operação parcial:** falta registro real completo/protegido, responsável e acesso. Não prometer ausência de reexposição sem esse insumo |
| Roteiro/limitações para equipe, transparência e resumo à #168 | Arquivos preparados, navegação MkDocs, política/Termos/inventário corrigidos e resumo abaixo | **Publicação por PR autorizada na continuação:** conferir integração e checks no GitHub; deploy não executado. Não reabre #269/#260/#171 |

## Resumo factual preparado para a #168

Em 17/11/2026, sobre `develop@cea7d6b` com #280 integrada, a implementação local
da #267 estendeu a evidência parcial do Bloco 7 sem alterá-la. Dump/restore
sintético isolado, schema/Alembic, valores/vínculos, jornada API e controles de
sessão/autorização/retencão passaram. Exclusões, retirada e revogações posteriores
ao dump foram reaplicadas antes de concluir a validação; recursos descartados.
Roteiro curto e textos afetados estão preparados. Nicolas relata backups manuais
no Docker, ainda sem cobertura/histórico/acessos detalhados. Recebedores foram
informados de memória; canal privado e acompanhamento precisam de confirmação.
Registro operacional protegido de exclusões/revogações não confirmado. Essas
lacunas impedem afirmar prontidão ou recuperação hospedada. Sem produção ou ativação.
O usuário autorizou publicar a entrega e encerrar a #267 com essas ressalvas;
isso não equivale a cumprimento das pendências operacionais. A #168 deve consumir esta evidência
e identificar a versão efetivamente publicada, sem repetir o ensaio por rotina.
