# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import os
from typing import Any

from sqlalchemy import MetaData, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    """Read more:"""
    cursor = dbapi_connection.cursor()
    settings: dict[str, Any] = {
        "journal_mode": "WAL",
        "foreign_keys": "ON",
        "page_size": 4096,
        "cache_size": 10000,
        # "locking_mode": 'EXCLUSIVE',
        "synchronous": "NORMAL",
    }
    for k, v in settings.items():
        cursor.execute(f"PRAGMA {k} = {v};")
    cursor.close()


SQLALCHEMY_DATABASE_URL: str = os.getenv(
    "OBSERVE_SQLALCHEMY_DATABASE_URL", "sqlite:///./observe.db"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, future=True, bind=engine
)

SQLALCHEMY_DATABASE_ASYNC_URL: str = os.getenv(
    "OBSERVE_SQLALCHEMY_DATABASE_ASYNC_URL", "sqlite+aiosqlite:///./observe.db"
)

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_ASYNC_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    future=True,
    expire_on_commit=False,
)

DB_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(
    naming_convention=DB_INDEXES_NAMING_CONVENTION,
    # NOTE: In SQLite schema, the value should be `main` only because it does
    #   not implement with schema system.
    schema="main",
)

Base = declarative_base(metadata=metadata)
