from decouple import Csv, config

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
