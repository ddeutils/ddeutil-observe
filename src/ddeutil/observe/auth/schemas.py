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
    name: str
    email: Optional[str] = None
    fullname: Optional[str] = None


class UserSchemaCreate(UserSchemaBase):
    pass


class UserSchema(UserSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool


class UserSchemaCreateForm(UserSchemaBase):
    password: str

    @classmethod
    def as_form(
        cls,
        email: EmailStr = Form(...),
        username: str = Form(...),
        password: str = Form(...),
    ):
        return cls(
            name=username,
            email=email,
            password=password,
        )
