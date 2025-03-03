import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.ddeutil.observe.models.policy import Policy, Role


@pytest.mark.asyncio
async def test_select_policy(session: AsyncSession):
    policies = (await session.execute(select(Policy))).scalars().all()
    assert len(policies) == 0


@pytest.mark.asyncio
async def test_create_policies(session: AsyncSession):
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


@pytest.mark.asyncio
async def test_create_policy_duplicate(session: AsyncSession):
    with pytest.raises(IntegrityError):
        session.add(Policy(resource="auth", action="delete"))
        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.mark.asyncio
async def test_create_roles(session: AsyncSession):
    roles = [
        Role(name="admin"),
        Role(name="develop"),
        Role(name="monitor"),
        Role(name="anon"),
    ]
    session.add_all(roles)
    await session.commit()

    roles = (await session.execute(select(Role))).scalars().all()
    print(roles)
    assert len(roles) == 4


@pytest.mark.asyncio
async def test_create_role_with_policies(session: AsyncSession):
    stmt = select(Policy).where(Policy.resource == "auth")
    auth_policies = (await session.execute(stmt)).scalars().all()
    assert len(auth_policies) == 4

    role = Role(name="custom")
    for policy in auth_policies:
        role.policies.append(policy)

    session.add(role)
    await session.commit()
    await session.refresh(role)

    assert len(role.policies) == 4
