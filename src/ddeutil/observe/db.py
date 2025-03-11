# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Optional

from sqlalchemy import event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session

from .conf import config

logger = logging.getLogger("uvicorn.error")


class DatabaseManageException(Exception): ...


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set pragma property to the SQLite database for the best performance.

    Read more:
    - https://docs.sqlalchemy.org/en/20/dialects/sqlite.html -
        #foreign-key-support
    """
    cursor = dbapi_connection.cursor()
    settings: dict[str, Any] = {
        # NOTE:
        #   Baseline setting that be production ready.
        #   * WAL mode might be the one for you if you want to concurrently work
        #     on the database, it does not block readers and writers.
        #
        #   Ref: https://forum.qt.io/topic/139657/multithreading-with-sqlite/
        #
        "journal_mode": "'WAL'",
        "locking_mode": "'NORMAL'",
        "synchronous": "'OFF'",
        "foreign_keys": "'ON'",
        "page_size": 4096,
        "cache_size": 10000,
        # NOTE: Set busy timeout for avoid database locking with 10 sec.
        "busy_timeout": 10000,
    }
    for k, v in settings.items():
        cursor.execute(f"PRAGMA {k} = {v};")
    cursor.close()


if config.log_sqlalchemy_debug:

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        conn.info.setdefault("query_start_time", []).append(time.time())
        logger.debug("Start Query: %s", statement)

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        logger.debug("Query Complete! Total Time: %f", total)

    @event.listens_for(Session, "before_commit")
    def before_commit(session):
        logger.debug(f"before commit: {session.info}")
        session.info["before_commit_hook"] = "yup"

    @event.listens_for(Session, "after_commit")
    def after_commit(session):
        logger.debug(
            f"before commit: {session.info['before_commit_hook']}, "
            f"after update: {session.info.get('after_update_hook', 'null')}"
        )


class DBSessionManager:
    """Database session manager object for creating engine and session mapping
    with host url string on the FastAPI lifespan step.
    """

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker] = None

    def init(self, host: str):
        self._engine = create_async_engine(
            host,
            echo=False,
            pool_pre_ping=False,
            connect_args={"check_same_thread": False},
        )
        self._sessionmaker = async_sessionmaker(
            autoflush=False,
            autocommit=False,
            future=True,
            expire_on_commit=False,
            bind=self._engine,
        )

    def is_opened(self) -> bool:
        return self._engine is not None

    async def close(self):
        if self._engine is None:
            raise DatabaseManageException(
                "DatabaseSessionManager is not initialized"
            )
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise DatabaseManageException(
                "DatabaseSessionManager is not initialized"
            )

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise DatabaseManageException(
                "DatabaseSessionManager is not initialized"
            )

        session: AsyncSession = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @staticmethod
    async def create_all(connection: AsyncConnection):
        from src.ddeutil.observe.auth.models import Base

        await connection.run_sync(Base.metadata.create_all)

    @staticmethod
    async def drop_all(connection: AsyncConnection):
        from src.ddeutil.observe.auth.models import Base

        await connection.run_sync(Base.metadata.drop_all)


sessionmanager = DBSessionManager()


DB_INDEXES_NAMING_CONVENTION: dict[str, str] = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


if config.log_sqlalchemy_debug:
    from src.ddeutil.observe.auth.models import Base

    @event.listens_for(Base, "after_update")
    def after_update(mapper, connection, target):
        session = inspect(target).session
        session.info["after_update_hook"] = "yup"
