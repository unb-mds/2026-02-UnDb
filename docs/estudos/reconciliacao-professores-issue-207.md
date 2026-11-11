# Reconciliação explícita de professores — #207

## Estado e diagnóstico

Preparação da estratégia autorizada por Nicolas em 07/11/2026: tabela de correspondências explícitas, reunião dos vínculos e avaliações sem colisão, bloqueio se o mesmo aluno já avaliou ambos na mesma disciplina. A execução em banco real, a revisão de Vinicius e o merge continuam pendentes. O ADR 07 não foi reescrito nem substituído: preserva-se a importação por ocorrência e a proibição de unir homônimos automaticamente.

A duplicação de Ajax não vem da tela: as turmas 02 e 03 de FGA0312 geraram professores diferentes. Alterar a chave para usar apenas nome/unidade confundiria homônimos; simplesmente agrupar a busca deixaria as avaliações fragmentadas.

## Implementação

- Migration `20261107_01` cria `professor_correspondencias` vazia; não une nenhum registro.
- Cada origem provisória aponta para um destino final. O registro antigo e sua `identidade_origem` permanecem armazenados, junto da evidência e data da correspondência. Não se inventa SIAPE nem se promove `identidade_confirmada`.
- O comando exige IDs explícitos, confirmação de mesma pessoa e evidência para aplicar. Nome igual não é confirmação. Não há endpoint público de união.
- Turmas, inclusive inativas, migram para o destino, sem duplicar vínculos. Avaliações mantêm IDs e timestamps; apenas a FK do professor muda. Comentários/versões/denúncias/decisões continuam ligados às mesmas avaliações/versões.
- Havendo colisão `(usuario, disciplina)` entre os dois professores, a operação inteira é recusada. Não há descarte, média, soma ou escolha de avaliação. Esses casos exigem política adicional aprovada; esta entrega deliberadamente não os resolve.
- A busca exclui origens reconciliadas. Consulta e envio com ID antigo resolvem para o destino, inclusive comentários e filtro privado do autor.
- Reimportar as **ocorrências já reconciliadas** reutiliza o destino. Ocorrências novas (por exemplo, outro semestre) continuam provisórias até confirmação explícita; não há inferência de identidade por nome.
- A aplicação recusa origem com SIAPE/identidade confirmada, ciclos, cadeias e tentativa de remapear correspondência já aplicada para outro destino. Repetir o mesmo par é idempotente.

## Como o Vinicius pode aproveitar os arquivos

Base original da preparação: `72227cc` de `develop` (após integração da #190). A continuação de 10/11/2026 foi aplicada sobre `fcc1b7f`, candidata `release/1.2.0`, na branch local `fix/207-reconciliacao-atualizada`, preservando os campos de nomes institucionais e as integrações #204/#206. O patch contém somente os arquivos relacionados à #207 e este guia, sem banco, ambiente virtual, logs ou segredos.

Em checkout limpo de `develop`, criar a branch da issue e aplicar o arquivo fornecido pelo Nicolas:

```sh
git switch -c fix/207-reconciliacao-professores
git apply --check caminho/reconciliacao-professores-207.patch
git apply caminho/reconciliacao-professores-207.patch
```

Se `develop` avançou ou já houver trabalho na branch do Vinicius, conferir o diff e adaptar conflitos; não sobrescrever seus arquivos. O patch não cria commits. A entrega pode ser revisada e publicada em um único commit conforme a preferência do PO.

Arquivos principais: modelo/migration de correspondência; `repositories/reconciliacao_professor_repository.py`; comando `commands/reconciliar_professores.py`; integração em `professor_repository`, `avaliacao_repository`, serviços institucionais/avaliações/comentários e testes `test_reconciliacao_professores.py`.

## Procedimento operacional após revisão

1. Rehearsal em PostgreSQL descartável/restauração de backup, com a revisão de migration e código. Confirmar que não existe outra migration nova com a mesma ancestralidade; usar revisão de merge se necessário, sem editar migrations aplicadas.
2. Para implantação real, parar **API, importador agendado e demais escritores**, incluindo processos iniciados antes da janela. Fazer backup completo e verificar restauração. Os locks não tornam seguro executar a manutenção com requisições antigas ainda em andamento.
3. Com a configuração apontando explicitamente para o banco pretendido, aplicar `alembic upgrade head` e disponibilizar o código novo antes de reabrir escritores.
4. Simular e conferir origem/destino com evidência institucional/humana suficiente. Os dois IDs de Ajax abaixo reproduzem o diagnóstico local, mas não comprovam por si só que se trata da mesma pessoa nem garantem os mesmos IDs em outro banco.

```sh
python -m app.commands.reconciliar_professores --origem 8cac9b42-cfc6-4ddb-a92e-ed6f9cf9c49f --destino 883a9871-acbd-4ee4-addb-4e183fbccf3e
```

5. Somente após conferir backup, destino, ausência de colisões e confirmação individual, usar o mesmo comando com `--aplicar --confirmo-mesma-pessoa --evidencia "Referência da verificação aprovada"`. Evidência deve ser uma referência operacional de até 500 caracteres, sem dados pessoais desnecessários. Não copiar uma evidência fictícia do teste.
6. Conferir ambas as turmas sob o destino, avaliações e seus históricos, resultados da busca e comparação, acesso por ID antigo e reimportação repetida. A contagem de avaliações abaixo de três continua protegida. Reabrir os escritores só depois da conferência.

O padrão é **simulação**, sem commit no banco. A aplicação exige PostgreSQL e uma transação única; no PostgreSQL bloqueia tabelas relevantes com timeout de lock de cinco segundos e revalida o plano. Exceções causam rollback. Se a simulação mostrar `bloqueada`, o código de saída é 2 e nenhuma união é permitida. Não repetir indiscriminadamente após timeout: conferir processos concorrentes.

## Reversão

Antes de aplicar qualquer correspondência: downgrade da migration vazia é permitido. Depois de aplicar: o downgrade recusa remover a tabela de correspondências. A reversão suportada é restaurar o **backup completo** na janela de manutenção; remover apenas o alias não devolveria as avaliações às origens e faria a importação fragmentar os registros novamente. Não apagar linhas manualmente para contornar a proteção.

## Evidências e limites

Ambiente isolado da entrega: Windows, Python 3.13, dependências declaradas no projeto, SQLite em memória com FKs habilitadas e `BEGIN` explícito para emular a semântica transacional. `ruff check .`, `ruff format --check .` e a suíte completa `python -m unittest discover -s tests -q`: **170 testes aprovados** (nove novos cenários da #207).

Os cenários verificam preservação de IDs/timestamps/comentários/denúncias/decisões, busca e respostas dos handlers públicos, privacidade antes/depois do limiar, reimportação/idempotência, colisões sem perda, rollback, identidades confirmadas, ciclos e upgrade/downgrade aditivos. A aplicação utiliza os serviços de autenticação e permissões existentes; não concede acesso novo.

Também foram aprovados no **PostgreSQL 16 descartável**, em container exclusivo com armazenamento temporário: cadeia completa de `alembic upgrade head`, `alembic check` sem divergências, os nove cenários novos e o percurso HTTP/CLI real (`tests.integration_reconciliacao`). Este último verifica simulação/aplicação/repetição do comando, busca única, consulta por ID antigo, privacidade, login e substituição autenticada usando o ID antigo, sem gerar uma segunda avaliação. A fixture usa cookie HTTP de desenvolvimento somente no subprocesso de teste.

Para reproduzir no PostgreSQL descartável exclusivo `undb_207_test`, configurar `DATABASE_URL` e `RECONCILIACAO_POSTGRES_TEST_URL` para a mesma URL, com `SECRET_KEY` fictícia, e executar a partir de `backend/`:

```sh
python -m unittest discover -s tests -p test_reconciliacao_professores.py -v
python -m tests.integration_reconciliacao
```

**Atenção:** esses testes criam/removem tabelas nesse banco de teste, cuja finalidade exclusiva deve ser confirmada; nunca apontar para banco de trabalho ou produção. A integração HTTP exige a porta 8127 livre e encerra apenas o subprocesso que iniciou. A configuração PostgreSQL opcional não é usada pela suíte padrão em SQLite.

**Pendente antes de integrar:** revisão de Vinicius, CI/Python 3.12, exercício explícito de timeout/contenção e ensaio de backup/restauração. Nenhum banco do projeto foi migrado ou reconciliado. A identidade real de Ajax continua exigindo confirmação humana individual; as fixtures não comprovam essa correspondência.

## Continuação de 10/11/2026 — caso Lindomar

Nicolas forneceu duas capturas e declarou que os três resultados representam o mesmo professor, com três disciplinas. Uma leitura pública de `https://api.undb.app.br/api/professores?nome=LINDOMAR` e dos respectivos endpoints `/disciplinas` confirmou a fragmentação abaixo. A evidência de mesma pessoa é a declaração do solicitante; a API expõe três identidades não confirmadas, sem SIAPE, e por si só não confirma a identidade institucional.

| Registro de professor | Disciplina | Unidade |
| --- | --- | --- |
| `10fd9c18-2dc9-44fd-bfb1-4c1143a03c6a` | IFD0171 — FISICA 1 | 524 — Instituto de Física |
| `2347537c-13bb-4e6d-bf19-98329802e14d` | FGA0108 — MATEMÁTICA DISCRETA 2 | 673 — Campus UnB Gama |
| `4239e160-7531-4381-a666-ef49742878e9` | FGA0134 — TÓPICOS ESPECIAIS DE ENGENHARIA DE SOFTWARE | 673 — Campus UnB Gama |

O comando agora aceita repetir `--origem`. A simulação verifica colisões no conjunto inteiro, inclusive entre duas origens cujas avaliações não conflitem individualmente com o destino. A aplicação reúne o grupo em uma única transação/savepoint: falha na segunda origem desfaz também a primeira. Não cria uma política de escolha entre avaliações conflitantes; continua recusando o grupo inteiro.

Plano concreto para revisão: manter o primeiro ID como destino e apontar os outros dois para ele. A escolha preserva o rótulo de unidade do registro de destino; cada disciplina mantém seu código e seu nome institucional original, inclusive quando pertence a outra unidade. A proposta não afirma que a unidade do destino seja a lotação oficial do docente.

```sh
python -m app.commands.reconciliar_professores --origem 2347537c-13bb-4e6d-bf19-98329802e14d --origem 4239e160-7531-4381-a666-ef49742878e9 --destino 10fd9c18-2dc9-44fd-bfb1-4c1143a03c6a
```

Esse comando é somente simulação. Não foi executado contra o banco público: a tabela de correspondências ainda precisa de revisão/implantação. A leitura pública não permite verificar colisões privadas, backup ou estado transacional. A aplicação real continua sujeita ao procedimento operacional e à aprovação descritos nesta issue; nenhuma migration, união ou escrita foi executada no ambiente público nesta continuação.

Os testes acrescentados verificam três disciplinas/duas unidades, preservação dos nomes institucionais atuais, busca única, perfil completo por todos os IDs antigos, comparação por disciplina, reimportação e repetição idempotentes, colisões entre origens, rollback do grupo e simulação CLI. Uma nova ocorrência de outro semestre sem confirmação continua distinta; não se generaliza a confirmação do Lindomar a todo nome coincidente.

Validação desta continuação, Windows/Python 3.13:

- `ruff check .`, `ruff format --check .` (119 arquivos) e `python -m compileall -q app alembic`: aprovados.
- `python -m unittest discover -s tests -q`: 202 testes, 200 aprovados e dois erros de limpeza de arquivo SQLite em `test_migration_connection` (`WinError 32`). Os mesmos dois erros foram reproduzidos na base `release/1.2.0` sem esta correção. Os 14 testes da reconciliação passaram nesta execução.
- PostgreSQL, integração HTTP/CLI operacional e contenção não foram reexecutados nesta continuação: o daemon Docker está indisponível e `docker desktop start` falhou. As evidências PostgreSQL da seção anterior pertencem à preparação original, não validam as adições de grupo desta revisão.
- A revisão do diff preservou os contratos de nomes institucionais atuais; não houve alteração de frontend, das escalas de avaliação ou do limiar de privacidade. A migration continua aditiva e vazia, com downgrade recusado após correspondências aplicadas.

**Estado:** implementação local preparada para revisão. Permanecem pendentes aprovação operacional/estrutural conforme #207, revisão de Vinicius, validação PostgreSQL/Python 3.12, backup/restauração e aplicação/publicação. Sem commit, push, PR, merge ou encerramento da issue nesta continuação.

### Validação Docker após transferência da execução

Na continuação da conversa, Nicolas informou que assumiu a execução da issue e que Vinicius fará a revisão; autorizou alterações de código e pediu uma prévia Docker. Foi criado o projeto local exclusivo `undb-issue207-preview`, usando o mesmo código desta worktree, com frontend em `localhost:3107`, API em `localhost:8107` e PostgreSQL 16 em volume próprio. O catálogo público do Lindomar foi carregado com seus três IDs e turmas; não foram copiados usuários, avaliações ou comentários.

Com backup e serviços de aplicação parados, o comando CLI aplicou as duas correspondências numa única operação. A reimportação das três ocorrências preservou a união. A busca no navegador mostra um resultado; o perfil mostra FGA0108, FGA0134 e IFD0171 com os nomes das unidades preservados. Captura e instruções de reinício estão na pasta local `.worktrees/local-runtime/issue-207/`, fora da entrega de produto.

Resultados posteriores, que superam as limitações ambientais da execução Windows acima:

- Imagens frontend/backend construídas; TypeScript/build aprovados; três containers saudáveis.
- Suíte completa no container Linux/Python 3.12: **202 testes aprovados**. O utilitário `backend/pegar_id.py` foi montado apenas para essa execução dos testes, pois a imagem de runtime não o inclui. Os dois erros de limpeza de arquivos do Windows não ocorreram no Linux.
- PostgreSQL 16 exclusivo `undb_207_test`: cadeia de migrations e `alembic check` aprovados; **14 testes da reconciliação aprovados**, incluindo o grupo de três disciplinas em duas unidades, colisões e rollback.
- `tests.integration_reconciliacao`: fluxo HTTP/CLI aprovado, incluindo simulação, aplicação, repetição, IDs antigos, privacidade, login e substituição autenticada sem segunda avaliação.
- Backup local restaurado em `undb_207_restore`: **três registros originais, zero correspondências**, confirmando o retorno ao estado anterior nesse ensaio isolado.

Responsável pela implementação nesta continuação: Nicolas; revisão de Vinicius permanece pendente. Teste explícito de contenção/timeout e implantação operacional continuam pendentes. Esta autorização e ensaio se limitam à prévia local; nenhuma migration ou reconciliação foi aplicada à produção. Sem commit, push, PR ou merge.

### Preparação da PR conjunta

Por solicitação posterior de Nicolas, a publicação foi preparada na branch
`fix/207-professores-sessao`, a partir de `develop` `1b979a9`. Isso evita incluir
documentos/versionamento exclusivos da candidata de release usada na prévia inicial.
A mesma PR inclui somente o ajuste do cabeçalho autenticado registrado na #211,
conforme [relatório próprio](cabecalho-sessao-issue-211.md). A solicitação autoriza
commit, push, abertura de PR e revisão por `ViniGvdo`; merge e implantação permanecem
fora desta execução. As menções anteriores à ausência de publicação descrevem o
estado dos respectivos ensaios locais.

### Revisão da PR #223 — 11/11/2026

Revisado o diff `1b979a9..4f5448e` da reconciliação, incluindo migration,
comando, repositories, serviços, testes e este procedimento, contra a #207,
o ADR 07 e os contratos existentes. Não foi confirmado defeito adicional na
reconciliação. Aprovação e aplicação operacional continuam pendentes.

Foi acrescentado o teste
`test_postgres_timeout_de_lock_desfaz_e_permite_nova_tentativa`. Um escritor
independente bloqueia `professor_correspondencias`, a última tabela adquirida
pela manutenção. A aplicação atinge o timeout real de cinco segundos
(`SQLSTATE 55P03`); após rollback, avaliações, vínculos e correspondências
permanecem intactos. Liberado o escritor, uma nova aplicação termina com sucesso.
O teste é pulado na suíte SQLite e executado com a configuração PostgreSQL
descartável documentada acima.

Resultados desta revisão:

- PostgreSQL 16 em container exclusivo, sem dados reais: cadeia completa de
  migrations e `alembic check` aprovados; **15 testes de reconciliação aprovados**,
  incluindo timeout/rollback; `tests.integration_reconciliacao` aprovado no
  fluxo HTTP/CLI. O ensaio de contenção antes pendente foi executado nesta revisão.
- Ruff, formatação de 119 arquivos e compilação aprovados.
- Suíte completa em Linux/Python 3.12: 203 testes, **201 aprovados, um pulado**
  (o teste exclusivo de PostgreSQL) e uma falha em
  `test_explicit_migration_connection_does_not_migrate_runtime_database`.
  Essa mesma falha foi reproduzida em snapshot limpo de `develop` `1b979a9`,
  com a mesma imagem/dependências. Os arquivos de configuração, Alembic e esse
  teste não foram alterados pela PR; não é um finding introduzido por ela.
- No Windows/Python 3.14, a suíte completa também encontrou erro de limpeza
  `WinError 32` em `test_without_override_preserves_existing_database_url_behavior`:
  200 aprovados, um pulado, uma falha e um erro. Não se declara a suíte inteira verde.

O banco isolado foi usado apenas para fixtures. Não houve migration,
reconciliação ou escrita em produção, nem novo ensaio de backup/restauração.
As evidências anteriores de backup preservam seu escopo histórico. As correções
do cabeçalho e dos runners estão no [registro da #211](cabecalho-sessao-issue-211.md).
