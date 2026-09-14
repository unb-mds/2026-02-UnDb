# Índices PostgreSQL

Crie índice quando uma consulta, join, filtro, ordenação ou constraint conhecida o justificar. Cada índice acelera algumas leituras, mas aumenta custo de inserção/atualização, espaço e manutenção.

1. `PRIMARY KEY` e `UNIQUE` já criam índice único B-tree: não crie duplicata.
2. FK não cria automaticamente índice no lado referenciante. Avalie índice em FK se joins, filtros ou exclusões/atualizações da tabela referenciada o exigirem.
3. Para B-tree composto, a ordem importa: igualdade nas colunas à esquerda e, depois, filtros/ordenação conhecidos tendem a ser mais eficientes. Não derive ordem de colunas da aparência do modelo.
4. Índice separado pode ser melhor que composto, ou desnecessário; compare as consultas reais e planos.
5. Considere filtros frequentes, joins e `ORDER BY`; não crie índice para toda coluna, toda FK ou “performance futura”. Tipos especializados, expressão, parcial, GIN/JSONB e `INCLUDE` exigem consulta e justificativa específicas.

No G7, a `UNIQUE(usuario_id, professor_id, disciplina_id)` já cria o índice único correspondente. Ela não prova que buscas por professor/disciplina ou a ordenação de agregados precisam de índices adicionais; essas decisões dependem das queries implementadas e de evidência.
