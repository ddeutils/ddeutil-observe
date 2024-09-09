# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status as st
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..conf import config
from ..deps import get_async_session
from ..utils import get_logger
from .crud import TokenCRUD, authenticate, verify_refresh_token
from .deps import get_current_active_user
from .models import User
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


@auth.post("/token")
async def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
    service: TokenCRUD = Depends(TokenCRUD),
) -> TokenRefresh:
    if form_data.grant_type != "password":
        raise HTTPException(
            status_code=st.HTTP_406_NOT_ACCEPTABLE,
            detail=(
                f"grant type: {form_data.grant_type} does not support for this "
                f"application yet."
            ),
        )

    logger.debug("Authentication with user-password")
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
    sub: dict[str, Any] = {
        "sub": user.username,
        "scopes": form_data.scopes,
    }
    access_token = create_access_token(subject=sub | {"id": user.id})
    refresh_token = create_refresh_token(subject=sub)
    return await service.create(
        token=TokenRefreshCreate(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=(
                datetime.now()
                + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
            ),
        ),
    )


@auth.post("/refresh")
async def refresh(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    # NOTE: Getting the refresh token from the client cookie.
    refresh_token: str | None = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND, detail="Refresh token missing."
        )

    if not (user_data := await verify_refresh_token(refresh_token, session)):
        raise HTTPException(
            status_code=st.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    new_access_token = create_access_token(subject={"sub": user_data.username})
    return {"access_token": new_access_token, "token_type": "Bearer"}


@auth.get("/token/me/", response_model=UserSchema)
async def read_user_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get current active user from the current token."""
    return current_user


@auth.get("/user/{username}")
async def read_user(
    username: str,
    session: AsyncSession = Depends(get_async_session),
) -> UserSchema:
    return await User.get_by_username(session, username=username)


@auth.get("/user")
async def read_user_all(
    session: AsyncSession = Depends(get_async_session),
) -> list[UserSchema]:
    return await User.get_all(session)
