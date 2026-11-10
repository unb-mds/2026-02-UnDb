-- Executar como administrador no banco neondb da API, após criar undb_api.
-- Base: 15 tabelas informadas pelo operador e repositories de develop.
-- Não define senha, não altera ownership e não troca a conexão do Render.
BEGIN;

GRANT CONNECT ON DATABASE neondb TO undb_api;
GRANT USAGE ON SCHEMA public TO undb_api;

-- Catálogo: a API consulta; o importador usa outra conexão.
GRANT SELECT ON TABLE
    public.unidades, public.disciplinas, public.professores,
    public.turmas, public.turmas_professores
TO undb_api;

-- Cadastro, confirmação, upsert de avaliações e renovação de sessão.
GRANT SELECT, INSERT, UPDATE ON TABLE
    public.usuarios, public.email_confirmation_tokens,
    public.avaliacoes, public.sessoes_usuario
TO undb_api;
GRANT DELETE ON TABLE public.sessoes_usuario TO undb_api;

-- Comentários: criação, revisão, retirada e descarte de versões.
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
    public.comentario_versoes
TO undb_api;

-- Denúncias, mensagens e decisões: criação, consulta e descarte.
GRANT SELECT, INSERT, DELETE ON TABLE
    public.denuncias, public.agradecimentos, public.decisoes_moderacao
TO undb_api;

-- Sem concessões a alembic_version ou importacao_execucoes.
-- Sem privilégios automáticos em tabelas futuras ou sequências.
COMMIT;
