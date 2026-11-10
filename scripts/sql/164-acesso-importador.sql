-- Executar como administrador em neondb, após criar undb_importador.
-- Não permite migrar schema, alterar contas ou executar reconciliações da #207.
BEGIN;
GRANT CONNECT ON DATABASE neondb TO undb_importador;
GRANT USAGE ON SCHEMA public TO undb_importador;
GRANT SELECT, INSERT, UPDATE ON TABLE
    public.unidades, public.disciplinas, public.professores, public.turmas,
    public.importacao_execucoes
TO undb_importador;
-- Sincronizar docentes de uma turma pode remover vínculos anteriores.
GRANT SELECT, INSERT, DELETE ON TABLE public.turmas_professores TO undb_importador;
COMMIT;
