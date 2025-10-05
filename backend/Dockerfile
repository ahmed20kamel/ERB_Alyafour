# backend/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (psycopg/libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# بما إن Root Directory = backend، فالملفات دي موجودة جنب الـ Dockerfile
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# انسخ كود المشروع كله (من داخل backend)
COPY . /app

# Render/Railway يوفر PORT وقت التشغيل
ENV PORT=8000

# شغّل الميجريشن + كوليكت ستاتيك + Daphne (ASGI)
CMD ["bash","-lc","python manage.py migrate --noinput && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT erp_system.asgi:application"]
