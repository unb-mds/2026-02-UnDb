from decouple import Csv, config

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
DATABASE_URL = config("DATABASE_URL")
CORS_ORIGINS = config("CORS_ORIGINS", default="http://localhost:3000", cast=Csv())
EMAIL_BACKEND = config("EMAIL_BACKEND", default="console")
EMAIL_FROM = config("EMAIL_FROM", default="UnDb <onboarding@resend.dev>")
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")
RESEND_API_KEY = config("RESEND_API_KEY", default="")
