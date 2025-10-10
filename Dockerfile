FROM python:3.13-slim-bookworm AS builder

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
    uv venv .venv && \
    uv sync

COPY . .

FROM python:3.13-slim-bookworm AS production

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY --from=builder /app/ /app/

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "-u", "main.py"]
