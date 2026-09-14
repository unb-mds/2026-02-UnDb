# Índices orientados por acesso

Índice depende de consultas conhecidas, não é decoração de toda coluna. Registre consulta/filtro/join/ordenação, seletividade/volume quando houver evidência, custo de escrita e como verificar eficácia.

1. Comece por chaves e constraints: `PRIMARY KEY` e `UNIQUE` normalmente têm suporte de índice; confirme no banco alvo.
2. Avalie FKs usadas em joins ou filtros. Em PostgreSQL, FK não cria automaticamente índice na coluna referenciante.
3. Para filtro/ordenação recorrentes, escolha ordem composta conforme padrão de consulta.
4. Não duplique índice de PK/UNIQUE nem antecipe índices; reavalie com plano/medição autorizada.
5. Tipo de índice, parcial, expressão, operador e plano pertencem a futura `postgresql` ou decisão técnica autorizada.

Na `UNIQUE (usuario_id, professor_id, disciplina_id)`, a ordem sustenta buscas iniciadas por `usuario_id` nessa sequência; não prova índices adicionais por professor, disciplina ou ordenação.
