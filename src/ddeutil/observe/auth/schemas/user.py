# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Optional

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr


class UserSchemaBase(BaseModel):
    username: str
    email: Optional[str] = None
    fullname: Optional[str] = None


class UserSchemaCreate(UserSchemaBase): ...


class UserSchema(UserSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool


class UserResetPassForm(BaseModel):
    username: str
    old_password: str
    new_password: str


class UserCreateForm(BaseModel):
    username: str
    password: str
    email: EmailStr
    fullname: Optional[str] = None


class UserScopeForm(BaseModel):
    scopes_me: bool
    scopes_workflows: bool

    @classmethod
    def as_form(
        cls,
        scopes_me: bool = Form(default=False),
        scopes_workflows: bool = Form(default=False),
    ):
        return cls(
            scopes_me=scopes_me,
            scopes_workflows=scopes_workflows,
        )

    def scopes(self) -> list[str]:
        rs: list[str] = []
        for sc in self.__dict__:
            if sc.startswith("scopes_") and self.__dict__[sc]:
                rs.append(sc.split("_", maxsplit=1)[-1])
        return rs
