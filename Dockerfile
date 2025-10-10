FROM rust:slim AS uv-builder
# Установка uv
RUN cargo install uv --root /usr/local

FROM python:3.11-slim-buster AS base
# Копируем скомпилированный бинарник uv с первого этапа
COPY --from=uv-builder /usr/local/bin/uv /usr/local/bin/uv

# Установка необходимых зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN uv venv --system && uv sync

COPY . .

ENTRYPOINT ["python", "-u", "main.py"]
