-- Após migration 20261113_01, no banco da aplicação, como administrador.
-- Não altera ownership, senhas ou permissões de escrita no catálogo da API.
BEGIN;
GRANT SELECT ON TABLE public.professor_correspondencias, public.identidades_docentes, public.identidades_locais,
    public.pendencias_identidade, public.decisoes_identidade TO undb_api;
GRANT UPDATE (estado, identificador_destino, versao, humana) ON public.pendencias_identidade TO undb_api;
GRANT INSERT ON public.decisoes_identidade TO undb_api;

GRANT SELECT ON public.professor_correspondencias TO undb_importador;
GRANT SELECT, INSERT, UPDATE ON public.identidades_docentes, public.identidades_locais, public.pendencias_identidade TO undb_importador;
-- Reconciliação que move vínculos/avaliações usa a conexão administrativa em
-- janela de manutenção; não conceder esse acesso à API ou ao importador.
COMMIT;
