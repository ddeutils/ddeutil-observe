# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Security
from fastapi import status as st
from fastapi.security import SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_async_session
from .crud import verify_access_token, verify_refresh_token
from .models import Token, User
from .securities import OAuth2Schema, OAuth2SchemaView, Tokens


async def get_current_access_token(
    token: Optional[str] = Depends(OAuth2Schema),
    session: AsyncSession = Depends(get_async_session),
) -> Optional[str]:
    """Get the current access token."""
    if await Token.get_disable(session, token):
        raise HTTPException(
            status_code=st.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(get_current_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Get the current user async function that will."""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=st.HTTP_401_UNAUTHORIZED,
        detail="Token was expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if (token_data := await verify_access_token(token, session)) is None:
        raise credentials_exception

    if not (
        user := await User.get_by_username(
            session, username=token_data.username
        )
    ):
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=st.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["me"]),
):
    """Get current user and checking it is actively or not. This method add on
    the ``me`` oauth scope.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=st.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


async def required_refresh_token(
    tokens: Tokens = Depends(OAuth2SchemaView),
) -> str:
    if not tokens.has_refresh:
        raise HTTPException(
            status_code=st.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/auth/login"},
        )
    return tokens.refresh


async def required_current_user(
    token: str = Depends(required_refresh_token),
    session: AsyncSession = Depends(get_async_session),
):
    if (token_data := await verify_refresh_token(token, session)) is None:
        raise HTTPException(
            status_code=st.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"Location": "/auth/login"},
        )

    if not (
        user := await User.get_by_username(
            session, username=token_data.username
        )
    ):
        raise HTTPException(
            status_code=st.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"Location": "/auth/login"},
        )
    return user


async def required_current_active_user(
    current_user: User = Depends(required_current_user),
):
    """Get current user and checking it is actively or not from session cookie.

    :param current_user: A current user that depends on token verification.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=st.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
            headers={"Location": "/auth/login"},
        )
    return current_user
