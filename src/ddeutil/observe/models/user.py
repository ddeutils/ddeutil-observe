# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.sql import false, select, true
from sqlalchemy.types import UUID as UUIDType
from sqlalchemy.types import Boolean, DateTime, Integer, String
from typing_extensions import Self

from . import Base, Col, Dtype

if TYPE_CHECKING:
    from .token import Token


class User(Base):
    __tablename__ = "users"

    id: Dtype[UUID] = Col(
        UUIDType(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        index=True,
    )
    username: Dtype[str] = Col(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )
    fullname: Dtype[Optional[str]] = Col(
        String(256),
        nullable=True,
        index=True,
    )
    email: Dtype[str] = Col(
        String(128),
        nullable=False,
        index=True,
    )
    hashed_password: Dtype[str] = Col(String, nullable=False)
    is_verified: Dtype[bool] = Col(Boolean, default=False)
    is_active: Dtype[bool] = Col(Boolean, default=True)
    is_superuser: Dtype[bool] = Col(Boolean, default=False)
    profile_image_url: Dtype[str] = Col(
        String, default="https://profileimageurl.com"
    )

    created_at: Dtype[datetime] = Col(
        DateTime(timezone=True),
        default=datetime.now,
        nullable=False,
    )
    updated_at: Dtype[datetime] = Col(
        DateTime(timezone=True),
        onupdate=datetime.now,
        # NOTE: This default use current timezone that this application stay.
        server_default=text("(datetime('now','localtime'))"),
    )
    deleted_at: Dtype[Optional[datetime]] = Col(
        DateTime(timezone=True),
        nullable=True,
    )

    tokens: Dtype[list["Token"]] = relationship(
        "Token",
        back_populates="user",
        order_by="Token.created_at",
        cascade=(
            "save-update, merge, refresh-expire, expunge, delete, delete-orphan"
        ),
    )

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> Self:
        """Create user from any mapping insert values.

        :rtype: Self
        """
        user: Self = cls(id=(user_id or uuid4().hex), **kwargs)
        session.add(user)
        await session.flush()
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def get_by_username(
        cls,
        session: AsyncSession,
        username: str,
        *,
        include_tokens: bool = False,
    ) -> Optional[Self]:
        stmt = select(cls).where(cls.username == username)
        if include_tokens:
            stmt = stmt.options(selectinload(cls.tokens))
        return (await session.execute(stmt)).scalar_one_or_none()

    @classmethod
    async def get_by_email(
        cls,
        session: AsyncSession,
        email: str,
    ) -> Optional[Self]:
        try:
            return (
                (
                    await session.execute(
                        select(cls).where(cls.email == email).limit(1)
                    )
                )
                .scalars()
                .first()
            )
        except NoResultFound:
            return None

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        *,
        is_active: Optional[bool] = None,
    ) -> list[Self]:
        stmt = select(cls)
        if is_active is not None:
            stmt = stmt.where(cls.is_active == (false if is_active else true)())
        return (await session.execute(stmt)).scalars().all()


class GroupUser(Base):
    __tablename__ = "associate_groups_users"

    group_id: Dtype[int] = Col(
        Integer, ForeignKey("groups.id"), primary_key=True
    )
    user_id: Dtype[int] = Col(Integer, ForeignKey("users.id"), primary_key=True)

    user: Dtype[User] = relationship(
        "Group",
        back_populates="user_associations",
    )


class Group(Base):
    __tablename__ = "groups"

    id = Col(Integer, primary_key=True)
    name = Col(String, unique=True, nullable=False)

    user_associations: Dtype[list[GroupUser]] = relationship(
        "GroupUser",
        back_populates="user",
    )
