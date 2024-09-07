# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.types import DateTime, Integer, String

from ...db import Base, Col


class Tier(Base):
    __tablename__ = "tier"

    id: Mapped[int] = Col(Integer, primary_key=True)
    name: Mapped[str] = Col(String, nullable=False, unique=True)
    created_at: Mapped[datetime] = Col(
        DateTime(timezone=True),
        default=datetime.now,
        nullable=False,
    )
    updated_at: Mapped[Optional[datetime]] = Col(
        DateTime(timezone=True),
        default=None,
        nullable=True,
    )


class Group(Base):
    __tablename__ = "groups"

    id = Col(Integer, primary_key=True)
    name = Col(String, unique=True, nullable=False)
    member = Col(Integer, ForeignKey("users.id"))


class Role(Base):
    __tablename__ = "roles"

    id = Col(Integer, primary_key=True)
    name = Col(String, unique=True, nullable=False)


class Policy(Base):
    __tablename__ = "policies"

    id = Col(Integer, primary_key=True)
    name = Col(String, unique=True, nullable=False)
