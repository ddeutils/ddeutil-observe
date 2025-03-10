from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.ddeutil.observe.auth.models import Base

DB_POINTER = Path(__file__).parent.parent.parent / "observe.test.db"
engine = create_async_engine(
    f"sqlite+aiosqlite:///{DB_POINTER}",
    echo=False,
    pool_pre_ping=False,
    connect_args={"check_same_thread": False},
)


@pytest.fixture(scope="session")
async def connection() -> AsyncGenerator[AsyncConnection, None]:
    async with engine.connect() as conn:
        yield conn


@pytest.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    sessionmaker = async_sessionmaker(
        autoflush=False,
        autocommit=False,
        future=True,
        expire_on_commit=False,
        bind=engine,
    )
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="session", autouse=True)
async def create_and_drop_tables(connection: AsyncConnection):
    await connection.run_sync(Base.metadata.create_all)

    yield

    await connection.run_sync(Base.metadata.drop_all)
