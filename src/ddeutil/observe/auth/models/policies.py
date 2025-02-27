# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer, String

from ...db import Base, Col


class Role(Base):
    """A role will be a group of policies.

    Initial roles that will create when start this application:
        - Admin
        - Develop
        - User
        - Anon
    """

    __tablename__ = "roles"

    id = Col(Integer, primary_key=True)
    name = Col(String, unique=True, nullable=False)


class RolePolicy(Base):

    __tablename__ = "rel_roles_policies"

    id = Col(Integer, primary_key=True)
    role = Col(Integer, ForeignKey("roles.id"))
    policy = Col(Integer, ForeignKey("policies.id"))


class Policy(Base):
    """
    Initial roles that will create when start this application:
        - create: Post, Put
        - delete: Delete
        - get: Get
    """

    __tablename__ = "policies"

    id = Col(Integer, primary_key=True)
    name = Col(String, unique=True, nullable=False)
    route = Col(String, nullable=False)
    action = Col(String, nullable=False)
