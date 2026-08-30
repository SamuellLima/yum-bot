"""Engine e sessão do SQLAlchemy."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .base import Base

load_dotenv()


def _normalize_database_url(url: str) -> str:
    """Converte JDBC / postgresql:// para a URL esperada pelo SQLAlchemy."""
    if url.startswith("jdbc:postgresql://"):
        parsed = urlparse(url.removeprefix("jdbc:"))
        query = parse_qs(parsed.query)
        user = (query.get("user") or [""])[0]
        password = (query.get("password") or [""])[0]
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        database = (parsed.path or "/").lstrip("/")
        auth = f"{user}:{password}@" if user else ""
        return f"postgresql+psycopg://{auth}{host}:{port}/{database}"

    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url


DATABASE_URL = _normalize_database_url(
    os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://yumbot:yumbot@localhost:15432/yumbot",
    )
)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
    class_=Session,
)


@contextmanager
def get_db() -> Iterator[Session]:
    """Abre uma sessão, faz commit se der certo, rollback em erro e sempre fecha.

    Uso:
        with get_db() as db:
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    from App.database import models  # noqa: F401 — registra os modelos no metadata

    Base.metadata.create_all(bind=engine)


def dispose_engine() -> None:
    """Devolve as conexões do pool ao banco. Chamar no shutdown do bot."""
    engine.dispose()
