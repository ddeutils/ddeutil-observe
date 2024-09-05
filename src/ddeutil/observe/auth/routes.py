# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as st
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..conf import config
from ..deps import get_async_session
from . import models
from .crud import authenticate
from .schemas import (
    Token,
    UserSchema,
)
from .securities import create_access_token, get_current_active_user

auth = APIRouter(prefix="/auth", tags=["api", "auth"])


@auth.get("/user/{name}", response_model=UserSchema)
async def read_user(
    name: str,
    session: AsyncSession = Depends(get_async_session),
):
    return await models.User.get_by_name(session, name=name)


@auth.get("/user", response_model=list[UserSchema])
async def read_user_all(session: AsyncSession = Depends(get_async_session)):
    return await models.User.get_all(session)


@auth.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    user = await authenticate(
        session,
        name=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=st.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject={
            "sub": user.name,
            "scopes": form_data.scopes,
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@auth.get("/token/me/", response_model=UserSchema)
async def read_user_me(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    return current_user
