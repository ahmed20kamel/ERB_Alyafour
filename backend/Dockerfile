# backend/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (for psycopg / libpq)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Project code
COPY backend /app

# Render provides PORT at runtime
ENV PORT=8000

# Run migrations + collectstatic + start ASGI (Daphne)
CMD bash -lc "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    daphne -b 0.0.0.0 -p $PORT erp_system.asgi:application \
    "
