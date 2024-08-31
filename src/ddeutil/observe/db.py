# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import os
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
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
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
