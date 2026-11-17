from decouple import Csv, config
import json

SECRET_KEY = config("SECRET_KEY")
CANAL_TITULARES_ATIVO = config("CANAL_TITULARES_ATIVO", default=False, cast=bool)
CANAL_TITULARES_RETENCAO_APROVADA = config(
    "CANAL_TITULARES_RETENCAO_APROVADA", default=False, cast=bool
)
CANAL_TITULARES_LEITORES = config("CANAL_TITULARES_LEITORES", default="", cast=Csv())
CANAL_TITULARES_ATENDENTES = config("CANAL_TITULARES_ATENDENTES", default="", cast=Csv())
CANAL_TITULARES_LIMITE_MINUTO = config("CANAL_TITULARES_LIMITE_MINUTO", default=30, cast=int)
DEBUG = config("DEBUG", default=False, cast=bool)
PORT = config("PORT", default=10000, cast=int)
DATABASE_URL = config("DATABASE_URL")
MIGRATION_DATABASE_URL = config("MIGRATION_DATABASE_URL", default=DATABASE_URL)
CORS_ORIGINS = config("CORS_ORIGINS", default="http://localhost:3000", cast=Csv())
EMAIL_BACKEND = config("EMAIL_BACKEND", default="console")
EMAIL_FROM = config("EMAIL_FROM", default="UnDb <onboarding@resend.dev>")
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")
RESEND_API_KEY = config("RESEND_API_KEY", default="")

# Triagem opcional; publicação automática exige flag própria.
MODERACAO_FILTRO_ATIVO = config("MODERACAO_FILTRO_ATIVO", default=False, cast=bool)
# Complemento #252; ativação em produção depende de autorização própria.
MODERACAO_DISFARCES_ATIVO = config("MODERACAO_DISFARCES_ATIVO", default=False, cast=bool)
MODERACAO_SUBSTITUICOES_ATIVAS = config("MODERACAO_SUBSTITUICOES_ATIVAS", default=False, cast=bool)
MODERACAO_IA_ATIVA = config("MODERACAO_IA_ATIVA", default=False, cast=bool)
MODERACAO_IA_DADOS_APROVADOS = config("MODERACAO_IA_DADOS_APROVADOS", default=False, cast=bool)
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
OPENAI_MODERACAO_MODEL = config("OPENAI_MODERACAO_MODEL", default="omni-moderation-latest")
MODERACAO_IA_TIMEOUT = config("MODERACAO_IA_TIMEOUT", default=10, cast=float)
MODERACAO_IA_POR_MINUTO = config("MODERACAO_IA_POR_MINUTO", default=5, cast=int)
MODERACAO_IA_POR_DIA = config("MODERACAO_IA_POR_DIA", default=100, cast=int)

MODERACAO_AUTOMATICA_ATIVA = config("MODERACAO_AUTOMATICA_ATIVA", default=False, cast=bool)

# #266 bloco 1: núcleo sem endpoints vinculados. Políticas operacionais nos blocos seguintes.
ABUSO_HMAC_SECRET = config("ABUSO_HMAC_SECRET", default="")
ABUSO_POLITICAS = config("ABUSO_POLITICAS", default="{}", cast=json.loads)
# Perfil genérico inativo até registro explícito; não representa cota de e-mail.
ABUSO_QUANTIDADE_PADRAO = config("ABUSO_QUANTIDADE_PADRAO", default=100, cast=int)
ABUSO_JANELA_SEGUNDOS_PADRAO = config("ABUSO_JANELA_SEGUNDOS_PADRAO", default=60, cast=int)
ABUSO_QUANTIDADE_GLOBAL_PADRAO = config("ABUSO_QUANTIDADE_GLOBAL_PADRAO", default=100, cast=int)
ABUSO_JANELA_GLOBAL_SEGUNDOS_PADRAO = config(
    "ABUSO_JANELA_GLOBAL_SEGUNDOS_PADRAO", default=60, cast=int
)
ABUSO_STATEMENT_TIMEOUT_MS = config("ABUSO_STATEMENT_TIMEOUT_MS", default=250, cast=int)
ABUSO_LOCK_TIMEOUT_MS = config("ABUSO_LOCK_TIMEOUT_MS", default=100, cast=int)
ABUSO_CONNECT_TIMEOUT_SEGUNDOS = config("ABUSO_CONNECT_TIMEOUT_SEGUNDOS", default=2, cast=int)
ABUSO_POOL_TIMEOUT_SEGUNDOS = config("ABUSO_POOL_TIMEOUT_SEGUNDOS", default=0.25, cast=float)
ABUSO_POOL_TAMANHO = config("ABUSO_POOL_TAMANHO", default=2, cast=int)
ABUSO_RETRY_FALHA_SEGUNDOS = config("ABUSO_RETRY_FALHA_SEGUNDOS", default=5, cast=int)
ABUSO_LIMPEZA_INTERVALO_SEGUNDOS = config("ABUSO_LIMPEZA_INTERVALO_SEGUNDOS", default=60, cast=int)
ABUSO_LIMPEZA_LOTE = config("ABUSO_LIMPEZA_LOTE", default=1000, cast=int)
