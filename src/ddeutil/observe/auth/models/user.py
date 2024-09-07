# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, relationship, selectinload
from sqlalchemy.sql import select
from sqlalchemy.types import UUID, Boolean, DateTime, Integer, String
from typing_extensions import Self

from ...db import Base, Col


class User(Base):
    __tablename__ = "users"

    id = Col(Integer, primary_key=True, index=True)
    username = Col(String, unique=True, nullable=False, index=True)
    email = Col(String, nullable=True)
    hashed_password = Col(String, nullable=False)

    fullname = Col(String, nullable=True)

    is_verified: Mapped[bool] = Col(Boolean, default=False)
    is_active: Mapped[bool] = Col(Boolean, default=True)
    is_superuser: Mapped[bool] = Col(Boolean, default=False)
    profile_image_url: Mapped[str] = Col(
        String,
        default="https://profileimageurl.com",
    )
    uuid: Mapped[UUID] = Col(
        UUID,
        default=uuid4,
        primary_key=True,
        unique=True,
    )

    created_at: Mapped[datetime] = Col(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = Col(DateTime, default=datetime.now)
    deleted_at: Mapped[datetime] = Col(DateTime, default=datetime.now)

    tokens = relationship(
        "Token",
        back_populates="user",
        order_by="Token.created_at",
        cascade=(
            "save-update, merge, refresh-expire, expunge, delete, delete-orphan"
        ),
    )

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
    async def get_by_username(
        cls,
        session: AsyncSession,
        username: str,
        *,
        include_tokens: bool = False,
    ) -> Self | None:
        stmt = select(cls).where(cls.username == username)
        if include_tokens:
            stmt = stmt.options(selectinload(cls.tokens))
        return (await session.execute(stmt)).scalar_one_or_none()

    @classmethod
    async def get_by_email(
        cls,
        session: AsyncSession,
        email: str,
    ) -> Self | None:
        try:
            return (
                (await session.execute(select(cls).where(cls.email == email)))
                .scalars()
                .first()
            )
        except NoResultFound:
            return None

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Self]:
        return (await session.execute(select(cls))).scalars().all()
