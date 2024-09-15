# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false, select, true
from sqlalchemy.types import UUID, Boolean, DateTime, Integer, String
from typing_extensions import Self

from ...db import Base, Col, Dtype

if TYPE_CHECKING:
    from .user import User


class Token(Base):
    __tablename__ = "tokens"

    id: Dtype[int] = Col(Integer, primary_key=True)
    access_token: Dtype[str] = Col(String(450), nullable=False, unique=True)
    refresh_token: Dtype[str] = Col(String(450), nullable=False)
    is_active: Dtype[bool] = Col(Boolean, default=True)
    user_id: Dtype[UUID] = Col(UUID(as_uuid=True), ForeignKey("users.id"))
    expires_at: Dtype[Optional[datetime]] = Col(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Dtype[datetime] = Col(
        DateTime(timezone=True),
        default=datetime.now,
        nullable=False,
    )
    updated_at: Dtype[datetime] = Col(
        DateTime(timezone=True),
        onupdate=datetime.now,
        nullable=True,
        server_default=text("(datetime('now','localtime'))"),
    )

    user: Dtype[User] = relationship(
        "User",
        back_populates="tokens",
    )

    @classmethod
    async def get_active_by_user(
        cls, session: AsyncSession, user_id: str
    ) -> list[Self]:
        return (
            (
                await session.execute(
                    select(cls).where(
                        cls.user_id == user_id,
                        cls.is_active == true(),
                    )
                )
            )
            .scalars()
            .all()
        )

    @classmethod
    async def get_disable(
        cls,
        session: AsyncSession,
        token: str,
    ) -> Self | None:
        return (
            await session.execute(
                select(cls).where(
                    cls.access_token == token,
                    cls.is_active == false(),
                )
            )
        ).scalar_one_or_none()

    @classmethod
    async def get_refresh_disable(
        cls,
        session: AsyncSession,
        token: str,
    ) -> Self | None:
        return (
            await session.execute(
                select(cls).where(
                    cls.access_token == token,
                    cls.refresh_token == token,
                    cls.is_active == false(),
                )
            )
        ).scalar_one_or_none()

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        token: str,
    ) -> Self | None:
        return (
            await session.execute(select(cls).where(cls.access_token == token))
        ).scalar_one_or_none()

    @classmethod
    async def get_by_refresh(
        cls, session: AsyncSession, token: str
    ) -> Self | None:
        return (
            (
                await session.execute(
                    select(cls)
                    .where(
                        cls.refresh_token == token,
                        cls.is_active == true(),
                    )
                    .order_by(cls.created_at)
                )
            )
            .scalars()
            .all()
        )

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        **kwargs,
    ) -> Self:
        token: Self = cls(**kwargs)
        session.add(token)
        await session.flush()
        await session.commit()
        await session.refresh(token)
        return token
