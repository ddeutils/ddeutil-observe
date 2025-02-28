# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
import asyncio
from contextlib import ExitStack
from pathlib import Path

import pytest
from ddeutil.observe.app import app as actual_app
from ddeutil.observe.db import sessionmanager
from ddeutil.observe.deps import get_async_session
from fastapi.testclient import TestClient

from .utils import dotenv_setting, initial_db

db_path: Path = Path(__file__).parent.parent / "observe.test.db"
db_path.unlink(missing_ok=True)
initial_db(db_path=db_path)

dotenv_setting()


@pytest.fixture(scope="session")
def db_pointer() -> Path:
    return Path(__file__).parent.parent / "observe.test.db"


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield actual_app


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()

    yield loop

    loop.close()


# @pytest.fixture(scope="session")
# def setup_db() -> Iterator[None]:
#     engine = create_engine(
#         f"sqlite:///{Path(__file__).parent.parent / 'observe.test.db'}",
#         connect_args={"check_same_thread": False},
#     )
#
#     yield
#
#     conn = engine.connect()
#     conn.execute("commit")
#     try:
#         conn.execute("drop database test")
#     except SQLAlchemyError:
#         pass
#     conn.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # NOTE: Run alembic migrations on test DB
    # async with sessionmanager.connect() as connection:
    #     await connection.run_sync(run_migrations)

    yield

    await sessionmanager.close()


@pytest.fixture(scope="function", autouse=True)
async def transactional_session():
    async with sessionmanager.session() as session:
        try:
            await session.begin()
            yield session
        finally:
            await session.rollback()  # Rolls back the outer transaction


@pytest.fixture(scope="function")
async def db_session(transactional_session):
    yield transactional_session


@pytest.fixture(scope="function", autouse=True)
async def session_override(app, db_session):

    async def get_db_session_override():
        yield db_session[0]

    app.dependency_overrides[get_async_session] = get_db_session_override
