# Constraints e `NULL`

Use a constraint que materializa a regra autorizada mais perto dos dados:

- `PRIMARY KEY`: identidade estável; força `NOT NULL` e cria índice único.
- `FOREIGN KEY`: referência válida; escolha ação de atualização/exclusão somente se houver regra de produto aprovada.
- `UNIQUE`: unicidade de valor ou combinação; use composição quando a identidade lógica depende de várias colunas.
- `NOT NULL`: ausência é inválida; não converta desconhecido em valor sentinela.
- `CHECK`: domínio ou relação por linha que o banco pode testar.
- `DEFAULT`: valor de ausência explicitamente autorizado; não substitui validação de entrada.

## `UNIQUE` e `NULL`

Por padrão, PostgreSQL considera `NULL` distinto de `NULL` em índice/constraint única. Assim, uma `UNIQUE` permite várias linhas com `NULL` na coluna ou, em composição, valores repetidos se uma posição for `NULL`. Se “ausência” não é válida na chave lógica, use `NOT NULL`. `NULLS NOT DISTINCT` altera a semântica, mas só deve ser proposto quando a regra exigir que nulos comparem como iguais e a versão/compatibilidade estiver confirmada.

No G7, `avaliacoes.usuario_id`, `professor_id` e `disciplina_id` devem ser não nulos, de modo que a `UNIQUE(usuario_id, professor_id, disciplina_id)` realmente proíba duplicata. A constraint não realiza sozinha a substituição de reenvio: ela é a barreira de integridade, enquanto a escrita autorizada atualiza a linha existente.

Nomeie constraints explicitamente quando isso melhorar rastreabilidade/revisão de Alembic. Autogenerate é candidato a migration, nunca sua aprovação automática.
