# =============================================
# MEMAX OTT - Celery Worker Dockerfile
# =============================================

FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install --no-cache-dir --user eventlet

# ─── Production Stage ─────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

RUN apt-get update && apt-get install -y libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .

RUN mkdir -p uploads/movies && chmod -R 777 uploads/

ENV PATH=/root/.local/bin:$PATH

# Render Web Service Hack: Run a dummy HTTP server on $PORT to pass Render's port scan timeout,
# while running Celery in the foreground.
CMD ["sh", "-c", "python -m http.server ${PORT:-10000} & exec celery -A app.core.celery_app worker --loglevel=info -P eventlet -c 2"]
