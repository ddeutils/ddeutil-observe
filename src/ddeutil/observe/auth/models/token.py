# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false, or_, select, true
from sqlalchemy.types import Boolean, DateTime, Integer, String
from typing_extensions import Self

from ...db import Base, Col, Dtype


class Token(Base):
    __tablename__ = "tokens"

    id: Dtype[int] = Col(Integer, primary_key=True)
    access_token: Dtype[str] = Col(String(450), nullable=False, unique=True)
    refresh_token: Dtype[str] = Col(String(450), nullable=False)
    status: Dtype[bool] = Col(Boolean, default=True)
    user_id: Dtype[int] = Col(Integer, ForeignKey("users.id"))

    expires_at: Dtype[datetime] = Col(DateTime)
    created_at: Dtype[datetime] = Col(
        DateTime,
        default=datetime.now,
        server_default=text("current_timestamp"),
    )
    updated_at: Dtype[datetime] = Col(
        DateTime,
        nullable=True,
        onupdate=datetime.now,
        server_default=text("current_timestamp"),
    )

    user = relationship(
        "User",
        back_populates="tokens",
    )

    @classmethod
    async def get_active_by_user(
        cls, session: AsyncSession, user_id: int
    ) -> list[Self]:
        return (
            (
                await session.execute(
                    select(cls).where(
                        cls.user_id == user_id,
                        cls.status == true(),
                    )
                )
            )
            .scalars()
            .all()
        )

    @classmethod
    async def get_disable(
        cls, session: AsyncSession, token: str
    ) -> Self | None:
        return (
            await session.execute(
                select(cls).where(
                    or_(
                        cls.access_token == token,
                        cls.refresh_token == token,
                    ),
                    cls.status == false(),
                )
            )
        ).scalar_one_or_none()

    @classmethod
    async def get(cls, session: AsyncSession, token: str) -> Self | None:
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
                        cls.status == true(),
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
    ):
        transaction = cls(**kwargs)
        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)
        return transaction
