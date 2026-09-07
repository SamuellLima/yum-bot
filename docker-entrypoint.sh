#!/bin/sh
set -e

echo "Aguardando o PostgreSQL..."
python - <<'PY'
import asyncio
import sys

from sqlalchemy import text

from App.database.session import engine


async def wait_for_postgres() -> None:
    for attempt in range(1, 31):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("PostgreSQL disponível.")
            return
        except Exception as exc:
            print(f"Tentativa {attempt}/30: {exc}")
            await asyncio.sleep(2)

    print("Timeout aguardando o PostgreSQL.", file=sys.stderr)
    sys.exit(1)


asyncio.run(wait_for_postgres())
PY

echo "Aplicando migrações Alembic..."
alembic upgrade head

echo "Iniciando o Yum Bot..."
exec python main.py
