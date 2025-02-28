from ddeutil.observe.models.policy import Policy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def test_select_policy(session: AsyncSession):
    policies = (await session.execute(select(Policy))).scalars().all()
    assert len(policies) == 0


async def test_create_policy(session: AsyncSession):
    policies = [
        Policy(resource="workflow", action="read"),
        Policy(resource="workflow", action="create"),
        Policy(resource="workflow", action="update"),
        Policy(resource="workflow", action="delete"),
        Policy(resource="auth", action="read"),
        Policy(resource="auth", action="create"),
        Policy(resource="auth", action="update"),
        Policy(resource="auth", action="delete"),
    ]
    session.add_all(policies)
    await session.commit()

    policies = (await session.execute(select(Policy))).scalars().all()
    print(policies)
    assert len(policies) == 8
