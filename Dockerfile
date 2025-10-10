# ----------------------------------------------------------------------
# Stage 1: Builder (Наша "мастерская" для сборки)
# ----------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

COPY requirements.txt .

RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache -r requirements.txt

COPY . .

# ----------------------------------------------------------------------
# Stage 2: Production (Чистый образ для запуска)
# ----------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS production

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY --from=builder /app .

ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT ["python", "-u", "main.py"]