# backend/Dockerfile
FROM python:3.12

# سرّع pip و زوّد مهلة التحميل
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ✅ PostgreSQL client عشان pg_isready يشتغل في الـ compose
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# المتطلبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# كود المشروع
COPY . .

# نشغّل عبر compose command (هينتظر DB ويعمل migrate)
