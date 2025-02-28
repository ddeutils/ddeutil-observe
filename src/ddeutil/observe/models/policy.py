# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from . import Base, Col, Dtype

# NOTE: This will work with add this line to the Role model.
#
#   policies: Dtype[list["Policy"]] = relationship(
#       secondary=associate_roles_policies,
#       back_populates="roles",
#       uselist=True,
#       viewonly=True,
#   )
#
# associate_roles_policies = Table(
#     "associate_roles_policies",
#     Base.metadata,
#     Column("left_id", ForeignKey("left_table.id"), primary_key=True),
#     Column("right_id", ForeignKey("right_table.id"), primary_key=True),
# )


class RolePolicy(Base):
    __tablename__ = "associate_roles_policies"

    role_id: Dtype[int] = Col(
        Integer,
        ForeignKey("roles.id"),
        primary_key=True,
    )
    policy_id: Dtype[int] = Col(
        Integer,
        ForeignKey("policies.id"),
        primary_key=True,
    )

    role: Dtype["Role"] = relationship(
        "Role",
        back_populates="policy_associations",
    )
    policy: Dtype["Policy"] = relationship(
        "Policy",
        back_populates="role_associations",
    )


class Role(Base):
    """A Role model for keep a group of policies that mean one role can handle
    many policies.

        Initial roles that will create when start this application:
            - admin
            - develop
            - monitor
            - anon
    """

    __tablename__ = "roles"

    id: Dtype[int] = Col(Integer, primary_key=True)
    name: Dtype[str] = Col(String, unique=True, nullable=False)

    # policies: Dtype[list["Policy"]] = relationship(
    #     "Policy",
    #     secondary="associate_roles_policies",
    #     back_populates="roles",
    #     uselist=True,
    #     viewonly=True,
    # )

    policy_associations: Dtype[list["RolePolicy"]] = relationship(
        "RolePolicy",
        back_populates="role",
    )


class Policy(Base):
    """A Policy model for keep mapping of resource and action that exists on
    your application. A resource is alias of route that you want to assign name
    for it such as at the logs route, you assign resource name is `monitor`.

        Initial phase it will allow to have 4 actions:
            - create: Post
            - update: Put
            - delete: Delete
            - read: Get
    """

    __tablename__ = "policies"

    id: Dtype[int] = Col(Integer, primary_key=True)
    resource: Dtype[str] = Col(String, nullable=False)
    action: Dtype[str] = Col(String, nullable=False)

    # roles: Dtype[list["Role"]] = relationship(
    #     "Role",
    #     secondary="associate_roles_policies",
    #     back_populates="policies",
    #     uselist=True,
    #     viewonly=True,
    # )

    role_associations: Dtype[list["RolePolicy"]] = relationship(
        "RolePolicy",
        back_populates="policy",
    )
