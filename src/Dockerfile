# Build image. Loads dependencies with poetry
FROM python:3.11 AS builder

RUN mkdir /apps/
WORKDIR /apps/

RUN pip install pip==24.0 && \
    pip install poetry==1.8.3

ENV PYTHONUNBUFFERED 1 \
    PYTHONDONTWRITEBYTECODE 1

RUN poetry config virtualenvs.in-project true && \
    poetry config virtualenvs.create true && \
    poetry config cache-dir /tmp/poetry_cache

COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --only main --no-interaction && \
    # clear poetry cache
    rm -rf /tmp/poetry_cache

# The runtime image, uses virtual environment created by poetry, but poetry is not installed
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED 1 \
    PYTHONDONTWRITEBYTECODE 1

RUN mkdir /apps/
WORKDIR /apps/

ENV VIRTUAL_ENV_BUILDER=/apps/.venv \
    VIRTUAL_ENV_RUNTIME=/apps/.venv \
    PATH="/apps/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV_BUILDER} ${VIRTUAL_ENV_RUNTIME}
COPY ./. ./

ENTRYPOINT ["bash", "entrypoint.sh"]
