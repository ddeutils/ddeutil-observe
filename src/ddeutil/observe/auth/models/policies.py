# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer, String

from ...db import Base, Col


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
