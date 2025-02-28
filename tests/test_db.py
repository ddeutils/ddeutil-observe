import pytest
from ddeutil.observe.db import sessionmanager
from sqlalchemy.ext.asyncio import AsyncSession


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


def test_model_role(db_session: AsyncSession):
    print(db_session)
