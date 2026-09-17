# Performance e planos

Desempenho começa pela consulta e por evidência, não pelo tipo de índice. Reúna SQL/consulta SQLAlchemy, parâmetros representativos, volume/cardinalidade conhecida e plano antes de propor mudança.

- `EXPLAIN` mostra o plano estimado, scans e joins sem executar a consulta.
- `EXPLAIN ANALYZE` executa e mede a consulta; trate-o como potencialmente oneroso e nunca o aplique a mutações em ambiente real sem contexto seguro/autorização.
- Compare estimativas com linhas/tempos reais, filtros, joins e ordenações. Um sequential scan pode ser adequado em tabela pequena; não o classifique como defeito isoladamente.
- Investigue N+1: uma coleção carregada em loop pode virar muitas queries. Corrija o padrão de acesso autorizado antes de concluir que o banco precisa de novo índice.
- Evite buscar colunas/linhas além do necessário e agregue apenas com regra autorizada. Agregados do G7 são calculados na consulta; não materialize resultado, ranking ou índice composto ponderado sem decisão explícita.

MVCC permite leituras/escritas concorrentes com versões de linhas; atualizações e exclusões deixam tuplas mortas que exigem VACUUM/autovacuum. Não desligue nem altere configuração de VACUUM como “otimização” sem métricas, contexto operacional e aprovação.
