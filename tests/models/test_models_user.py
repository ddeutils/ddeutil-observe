import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ddeutil.observe.models.user import User


@pytest.mark.asyncio
async def test_select_user(session: AsyncSession):
    users = (await session.execute(select(User))).scalars().all()
    assert len(users) == 0


async def test_create_user(session: AsyncSession): ...
