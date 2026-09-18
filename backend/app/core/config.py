from decouple import Csv, config

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
DATABASE_URL = config("DATABASE_URL")
CORS_ORIGINS = config("CORS_ORIGINS", default="http://localhost:3000", cast=Csv())
