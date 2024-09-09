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
from .crud import verify_access_token
from .models import User
from .securities import OAuth2Schema


async def get_current_access_token(
    token: Optional[str] = Depends(OAuth2Schema),
) -> Optional[str]:
    """Get the current access token."""

    # TODO: If the token does not able to verify it will regenerate with the
    #  refresh token.
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
        detail="Could not validate credentials",
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
    if not current_user.is_active:
        raise HTTPException(
            status_code=st.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


async def required_auth(token: str = Depends(OAuth2Schema)):
    if not token:
        raise HTTPException(
            status_code=st.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/auth/login"},
        )
    return True
