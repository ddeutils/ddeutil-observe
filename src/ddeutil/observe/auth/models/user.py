# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.sql import select
from sqlalchemy.types import UUID, Boolean, DateTime, Integer, String
from typing_extensions import Self

from ...db import Base, Col, Dtype


class User(Base):
    __tablename__ = "users"

    id: Dtype[int] = Col(
        Integer,
        primary_key=True,
        index=True,
    )
    username: Dtype[str] = Col(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )
    fullname = Col(String(256), nullable=True)
    email: Dtype[str] = Col(String(128), nullable=True)
    hashed_password: Dtype[str] = Col(String, nullable=False)

    is_verified: Dtype[bool] = Col(Boolean, default=False)
    is_active: Dtype[bool] = Col(Boolean, default=True)
    is_superuser: Dtype[bool] = Col(Boolean, default=False)
    profile_image_url: Dtype[str] = Col(
        String, default="https://profileimageurl.com"
    )
    uuid: Dtype[UUID] = Col(
        UUID,
        default=uuid4,
        unique=True,
    )

    created_at: Dtype[datetime] = Col(DateTime, default=datetime.now)
    updated_at: Dtype[datetime] = Col(
        DateTime,
        nullable=True,
        onupdate=datetime.now,
        server_default=text("current_timestamp"),
    )
    deleted_at: Dtype[datetime] = Col(DateTime, default=datetime.now)

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
