from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def _get_database_url() -> str:
    url = os.getenv(
        "DATABASE_URL",
        "",
    )
    if not url:
        raise RuntimeError(
            "DATABASE_URL 未配置。请在 backend/.env 中设置，例如：\n"
            "DATABASE_URL=mysql+pymysql://user:password@localhost:3306/bazi?charset=utf8mb4"
        )
    return url


DATABASE_URL = _get_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_session() -> Generator[Session, None, None]:
    """FastAPI 依赖：提供一个数据库 Session，并在请求结束后自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

