# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = Field(default="Bearer")


class TokenRefresh(Token):
    refresh_token: str


class TokenRefreshCreate(TokenRefresh):
    user_id: int
    status: bool = Field(default=True)


class TokenRefreshForm(BaseModel):
    username: str
    password: str
    refresh_token: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: list[str] = []


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
