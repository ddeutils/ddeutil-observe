from ddeutil.observe.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def test_select_user(session: AsyncSession):
    existing_user = (await session.execute(select(User))).scalars().all()
    assert len(existing_user) == 0
