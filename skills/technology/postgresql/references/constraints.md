# Constraints e `NULL`

Use [a orientação genérica de integridade](../../database-design/references/constraints.md) para escolher a constraint que representa a regra autorizada. Nesta referência, verifique apenas as particularidades PostgreSQL: `PRIMARY KEY` força `NOT NULL` e cria índice único; `FOREIGN KEY` não cria índice automaticamente no lado referenciante; e ações de atualização ou exclusão continuam dependentes de regra aprovada.

## `UNIQUE` e `NULL`

Por padrão, PostgreSQL considera `NULL` distinto de `NULL` em índice/constraint única. Assim, uma `UNIQUE` permite várias linhas com `NULL` na coluna ou, em composição, valores repetidos se uma posição for `NULL`. Se “ausência” não é válida na chave lógica, use `NOT NULL`. `NULLS NOT DISTINCT` altera a semântica, mas só deve ser proposto quando a regra exigir que nulos comparem como iguais e a versão/compatibilidade estiver confirmada.

No G7, `avaliacoes.usuario_id`, `professor_id` e `disciplina_id` devem ser não nulos, de modo que a `UNIQUE(usuario_id, professor_id, disciplina_id)` realmente proíba duplicata. A constraint não realiza sozinha a substituição de reenvio: ela é a barreira de integridade, enquanto a escrita autorizada atualiza a linha existente.

Nomeie constraints explicitamente quando isso melhorar rastreabilidade/revisão de Alembic. Autogenerate é candidato a migration, nunca sua aprovação automática.
