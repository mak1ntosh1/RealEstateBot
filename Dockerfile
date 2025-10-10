# Установка uv
FROM rust:slim AS uv-installer
RUN cargo install uv

FROM python:3.13.8-alpine3.22
FROM python:3.11-slim-buster AS base

WORKDIR /app

RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]