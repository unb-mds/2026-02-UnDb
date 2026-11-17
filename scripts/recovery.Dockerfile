# Dependências do ensaio local; sem código, credenciais ou dados na imagem.
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt backend/requirements-dev.txt /requirements/
RUN pip install --no-cache-dir -r /requirements/requirements.txt -r /requirements/requirements-dev.txt
RUN addgroup --system app && adduser --system --ingroup app app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
USER app
