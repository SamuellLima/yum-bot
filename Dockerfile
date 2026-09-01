FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=America/Sao_Paulo

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

COPY requirements.txt .
RUN grep -vE '^ruff($|~|=)' requirements.txt \
    | pip install --no-cache-dir -r /dev/stdin

COPY alembic.ini .
COPY alembic ./alembic
COPY App ./App
COPY main.py .
COPY docker-entrypoint.sh .

RUN chmod +x docker-entrypoint.sh \
    && useradd --create-home --uid 1000 yumbot \
    && chown -R yumbot:yumbot /app

USER yumbot

ENTRYPOINT ["./docker-entrypoint.sh"]
