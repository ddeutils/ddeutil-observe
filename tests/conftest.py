# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from contextlib import ExitStack
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from .utils import dotenv_setting

dotenv_setting()


@pytest.fixture(scope="session")
def test_path() -> Path:
    return Path(__file__).parent


@pytest.fixture()
def app():
    from src.ddeutil.observe.app import app as actual_app

    with ExitStack():
        yield actual_app


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


# @pytest.fixture(scope='session', autouse=True)
# async def db_engine(db_url: str):
#     """yields a SQLAlchemy engine which is suppressed after the test session"""
#     sessionmanager.init(db_url)
#
#     yield
#
#     if sessionmanager.is_opened():
#         await sessionmanager.close()
#
#
# # @pytest.fixture(scope="session")
# # def setup_db() -> Iterator[None]:
# #     engine = create_engine(
# #         f"sqlite:///{Path(__file__).parent.parent / 'observe.test.db'}",
# #         connect_args={"check_same_thread": False},
# #     )
# #
# #     yield
# #
# #     conn = engine.connect()
# #     conn.execute("commit")
# #     try:
# #         conn.execute("drop database test")
# #     except SQLAlchemyError:
# #         pass
# #     conn.close()
#
#
# # @pytest.fixture(scope="session", autouse=True)
# # async def setup_database():
# #     # NOTE: Run alembic migrations on test DB
# #     # async with sessionmanager.connect() as connection:
# #     #     await connection.run_sync(run_migrations)
# #
# #     yield
# #
# #     await sessionmanager.close()
#
#
# # @pytest_asyncio.fixture(scope="function")
# # async def async_session() -> AsyncIterator[AsyncSession]:
# #     async with sessionmanager.session() as session:
# #         try:
# #             yield session
# #         finally:
# #             await session.rollback()
