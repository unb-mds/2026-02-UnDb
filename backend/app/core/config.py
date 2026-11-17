from decouple import Csv, config
import json

SECRET_KEY = config("SECRET_KEY")
CANAL_TITULARES_ATIVO = config("CANAL_TITULARES_ATIVO", default=False, cast=bool)
CANAL_TITULARES_RETENCAO_APROVADA = config(
    "CANAL_TITULARES_RETENCAO_APROVADA", default=False, cast=bool
)
CANAL_TITULARES_LEITORES = config("CANAL_TITULARES_LEITORES", default="", cast=Csv())
CANAL_TITULARES_ATENDENTES = config("CANAL_TITULARES_ATENDENTES", default="", cast=Csv())
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

# #266 bloco 2: PROVISÓRIOS, pendentes de validação (item 4).
AUTH_ABUSO_MODO = config("AUTH_ABUSO_MODO", default="enforce")
AUTH_ABUSO_GLOBAL_MINUTO = config("AUTH_ABUSO_GLOBAL_MINUTO", default=30, cast=int)
AUTH_ABUSO_MINUTO_SEGUNDOS = config("AUTH_ABUSO_MINUTO_SEGUNDOS", default=60, cast=int)
AUTH_LOGIN_MAX_TENTATIVAS = config("AUTH_LOGIN_MAX_TENTATIVAS", default=100, cast=int)
AUTH_LOGIN_JANELA_SEGUNDOS = config("AUTH_LOGIN_JANELA_SEGUNDOS", default=900, cast=int)
AUTH_LOGIN_ATRASO_APOS = config("AUTH_LOGIN_ATRASO_APOS", default=3, cast=int)
AUTH_LOGIN_ATRASO_INICIAL_SEGUNDOS = config(
    "AUTH_LOGIN_ATRASO_INICIAL_SEGUNDOS", default=1, cast=int
)
AUTH_LOGIN_ATRASO_MAX_SEGUNDOS = config("AUTH_LOGIN_ATRASO_MAX_SEGUNDOS", default=60, cast=int)
AUTH_EMAIL_MAX_TENTATIVAS = config("AUTH_EMAIL_MAX_TENTATIVAS", default=3, cast=int)
AUTH_EMAIL_JANELA_SEGUNDOS = config("AUTH_EMAIL_JANELA_SEGUNDOS", default=900, cast=int)
AUTH_EMAIL_INTERVALO_SEGUNDOS = config("AUTH_EMAIL_INTERVALO_SEGUNDOS", default=60, cast=int)
AUTH_EMAIL_DESTINO_MAX = config("AUTH_EMAIL_DESTINO_MAX", default=1, cast=int)
# Referência conservadora: Resend Free, não confirmação do plano contratado.
AUTH_EMAIL_COTA_DIARIA_PROVEDOR = config("AUTH_EMAIL_COTA_DIARIA_PROVEDOR", default=100, cast=int)
AUTH_EMAIL_ORCAMENTO_DIARIO = config("AUTH_EMAIL_ORCAMENTO_DIARIO", default=80, cast=int)
AUTH_EMAIL_DIA_SEGUNDOS = config("AUTH_EMAIL_DIA_SEGUNDOS", default=86400, cast=int)
AUTH_TOKEN_MAX_TENTATIVAS = config("AUTH_TOKEN_MAX_TENTATIVAS", default=10, cast=int)
AUTH_TOKEN_JANELA_SEGUNDOS = config("AUTH_TOKEN_JANELA_SEGUNDOS", default=900, cast=int)
AUTH_REDEFINICAO_GLOBAL_MINUTO = config("AUTH_REDEFINICAO_GLOBAL_MINUTO", default=10, cast=int)
AUTH_CONFIRMACAO_TTL_HORAS = config("AUTH_CONFIRMACAO_TTL_HORAS", default=24, cast=int)
AUTH_SESSAO_TTL_DIAS = config("AUTH_SESSAO_TTL_DIAS", default=7, cast=int)
AUTH_RECUPERACAO_TTL_MINUTOS = config("AUTH_RECUPERACAO_TTL_MINUTOS", default=60, cast=int)

# #266 bloco 3: PROVISÓRIOS, pendentes de validação (item 4).
FLUXOS_ABUSO_MODO = config("FLUXOS_ABUSO_MODO", default="enforce")
FLUXOS_ABUSO_JANELA_SEGUNDOS = config("FLUXOS_ABUSO_JANELA_SEGUNDOS", default=60, cast=int)
FLUXOS_ABUSO_GLOBAL = config("FLUXOS_ABUSO_GLOBAL", default=300, cast=int)
FLUXOS_ABUSO_POR_PAPEL = {
    "moderador": config("ABUSO_MODERADOR_QUANTIDADE", default=120, cast=int),
    "reconciliador": config("ABUSO_RECONCILIADOR_QUANTIDADE", default=120, cast=int),
}
DENUNCIA_FALLBACK_QUANTIDADE = config("DENUNCIA_FALLBACK_QUANTIDADE", default=3, cast=int)
DENUNCIA_FALLBACK_JANELA_SEGUNDOS = config(
    "DENUNCIA_FALLBACK_JANELA_SEGUNDOS", default=60, cast=int
)
FLUXOS_ABUSO_POLITICAS = {
    nome: {
        "quantidade": config(variavel, default=padrao, cast=int),
        "janela_segundos": FLUXOS_ABUSO_JANELA_SEGUNDOS,
        "quantidade_global": FLUXOS_ABUSO_GLOBAL,
        "janela_global_segundos": FLUXOS_ABUSO_JANELA_SEGUNDOS,
        "modo": FLUXOS_ABUSO_MODO,
        "falha": falha,
    }
    for nome, variavel, padrao, falha in (
        ("avaliacao.escrever", "ABUSO_AVALIACAO_QUANTIDADE", 10, "seguir"),
        ("denuncia.criar", "ABUSO_DENUNCIA_QUANTIDADE", 5, "local"),
        ("titular.criar", "ABUSO_TITULAR_CRIAR_QUANTIDADE", 3, "fechar"),
        ("titular.consultar", "ABUSO_TITULAR_CONSULTAR_QUANTIDADE", 10, "fechar"),
        ("titular.complementar", "ABUSO_TITULAR_COMPLEMENTAR_QUANTIDADE", 3, "fechar"),
        ("moderacao.fila", "ABUSO_MODERACAO_FILA_QUANTIDADE", 60, "fechar"),
        ("moderacao.decidir", "ABUSO_MODERACAO_DECIDIR_QUANTIDADE", 30, "fechar"),
        ("moderacao.triagem", "ABUSO_MODERACAO_TRIAGEM_QUANTIDADE", 10, "fechar"),
        ("identidade.fila", "ABUSO_IDENTIDADE_FILA_QUANTIDADE", 60, "fechar"),
        ("identidade.decidir", "ABUSO_IDENTIDADE_DECIDIR_QUANTIDADE", 30, "fechar"),
    )
}
