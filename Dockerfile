FROM python:3.11-slim-buster AS base

# Установка необходимых зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install uv && \
    uv venv --system && uv sync

COPY . .

ENTRYPOINT ["python", "-u", "main.py"]
