#!/bin/sh
set -e

echo "Aguardando o PostgreSQL..."
python - <<'PY'
import sys
import time

from sqlalchemy import text

from App.database.session import engine

for attempt in range(1, 31):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("PostgreSQL disponível.")
        sys.exit(0)
    except Exception as exc:
        print(f"Tentativa {attempt}/30: {exc}")
        time.sleep(2)

print("Timeout aguardando o PostgreSQL.", file=sys.stderr)
sys.exit(1)
PY

echo "Aplicando migrações Alembic..."
alembic upgrade head

echo "Iniciando o Yum Bot..."
exec python main.py
