# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status as st
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_async_session
from ..utils import get_logger
from . import models
from .crud import authenticate, create_token, verify_token
from .deps import get_current_active_user
from .schemas import (
    Token,
    TokenRefresh,
    TokenRefreshCreate,
    UserSchema,
)
from .securities import (
    create_access_token,
    create_refresh_token,
)

logger = get_logger("ddeutil.observe")
auth = APIRouter(prefix="/auth", tags=["api", "auth"])


@auth.get("/user/{username}")
async def read_user(
    username: str,
    session: AsyncSession = Depends(get_async_session),
) -> UserSchema:
    return await models.User.get_by_username(session, username=username)


@auth.get("/user")
async def read_user_all(
    session: AsyncSession = Depends(get_async_session),
) -> list[UserSchema]:
    return await models.User.get_all(session)


@auth.post("/token")
async def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> TokenRefresh:
    if form_data.grant_type == "password":
        logger.info("With password authenticate")

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
        subject={"sub": user.username, "scopes": form_data.scopes}
    )
    refresh_token = create_refresh_token(
        subject={"sub": user.username, "scopes": form_data.scopes}
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
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    refresh_token: str | None = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND, detail="Refresh token missing."
        )

    if not (user_data := await verify_token(refresh_token, session)):
        raise HTTPException(
            status_code=st.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    new_access_token = create_access_token(subject={"sub": user_data.username})
    return {"access_token": new_access_token, "token_type": "Bearer"}


@auth.get("/token/me/", response_model=UserSchema)
async def read_user_me(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    """Get current active user from the current token."""
    return current_user
