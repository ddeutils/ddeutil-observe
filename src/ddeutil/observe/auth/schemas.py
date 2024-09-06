# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Optional, Union

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenRefresh(Token):
    refresh_token: str
    token_type: str = Field(default="bearer")


class TokenRefreshCreate(TokenRefresh):
    user_id: int
    status: bool = Field(default=True)


class TokenRefreshForm(BaseModel):
    username: str
    password: str
    refresh_token: str

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
        refresh_token: str = Form(...),
    ):
        return cls(
            username=username, password=password, refresh_token=refresh_token
        )


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: list[str] = []


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


class UserSchemaResetForm(BaseModel):
    name: str
    old_password: str
    new_password: str

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        old_password: str = Form(...),
        new_password: str = Form(...),
    ):
        return cls(
            name=username,
            old_password=old_password,
            new_password=new_password,
        )


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
