FROM python:3.12-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    POETRY_VERSION=2.4.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR="/var/cache/pypoetry" \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base AS builder_base
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
      curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry --version

WORKDIR $PYSETUP_PATH

COPY pyproject.toml poetry.lock ./

FROM builder_base AS development

RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root
