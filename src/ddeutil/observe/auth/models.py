from uuid import uuid4

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.types import Boolean, Integer, String
from typing_extensions import Self

from ..db import Base, Col


class User(Base):
    __tablename__ = "users"

    id = Col(Integer, primary_key=True)
    name = Col(String, unique=True, nullable=False)
    email = Col(String, nullable=True)
    hashed_password = Col(String, nullable=False)
    fullname = Col(String, nullable=True)
    is_active = Col(Boolean, default=True)
    is_superuser = Col(Boolean, default=False)

    @classmethod
    async def create(
        cls, session: AsyncSession, user_id=None, **kwargs
    ) -> Self:
        if not user_id:
            user_id = uuid4().hex

        transaction = cls(id=user_id, **kwargs)
        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)
        return transaction

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Self:
        stmt = select(cls).where(cls.email == email)
        try:
            return (await session.execute(stmt)).scalars().first()
        except NoResultFound:
            return None

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Self]:
        return (await session.execute(select(cls))).scalars().all()


class Group(Base):
    __tablename__ = "groups"

    id = Col(Integer, primary_key=True)
    name = Col(String, unique=True, nullable=False)


class Role(Base):
    __tablename__ = "roles"

    id = Col(Integer, primary_key=True)


class Policy(Base):
    __tablename__ = "policies"

    id = Col(Integer, primary_key=True)
