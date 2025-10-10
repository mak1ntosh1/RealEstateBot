# ----------------------------------------------------------------------
# Stage 1: Builder (Устанавливаем uv и зависимости)
# ----------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .

# 1. Скачиваем бинарный uv (самый быстрый способ, т.к. не требует pip)
# 2. Устанавливаем все зависимости, используя uv.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --system && \
    /usr/local/bin/uv pip install

COPY . .

# ----------------------------------------------------------------------
# Stage 2: Production (Копируем только зависимости)
# ----------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS production

# Устанавливаем только runtime-зависимости (необходимы для работы с PostgreSQL).
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем скомпилированные зависимости (site-packages) и исполняемые файлы (bin)
# из builder-стейджа в системный Python в production-стейдже.
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY . .

ENTRYPOINT ["python", "-u", "main.py"]
