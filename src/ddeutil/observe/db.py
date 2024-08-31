# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import os

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    """Read more:"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode = 'WAL';")
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA page_size = 4096;")
    cursor.execute("PRAGMA cache_size = 10000;")
    cursor.execute("PRAGMA locking_mode = 'EXCLUSIVE';")
    cursor.execute("PRAGMA synchronous = 'NORMAL';")
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
