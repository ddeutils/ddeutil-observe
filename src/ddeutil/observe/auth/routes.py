# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as st
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_async_session
from . import models
from .crud import authenticate, create_token
from .schemas import (
    TokenRefresh,
    TokenRefreshCreate,
    TokenRefreshForm,
    UserSchema,
)
from .securities import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
)

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
async def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> TokenRefresh:
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
    access_token = create_access_token(
        subject={"sub": user.name, "scopes": form_data.scopes}
    )
    refresh_token = create_refresh_token(
        subject={"sub": user.name, "scopes": form_data.scopes}
    )
    return await create_token(
        session=session,
        token_create=TokenRefreshCreate(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@auth.post("/refresh")
async def refresh(
    form_refresh: TokenRefreshForm = Depends(TokenRefreshForm.as_form),
    session: AsyncSession = Depends(get_async_session),
) -> TokenRefresh:
    user = await authenticate(
        session,
        name=form_refresh.username,
        password=form_refresh.password,
    )
    if not user:
        raise HTTPException(
            status_code=st.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@auth.get("/token/me/", response_model=UserSchema)
async def read_user_me(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    return current_user
