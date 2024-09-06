# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi import status as st
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ..conf import config
from ..deps import get_async_session
from . import models
from .schemas import TokenData
from .securities import ALGORITHM, oauth2_scheme


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=st.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config.OBSERVE_SECRET_KEY, algorithms=[ALGORITHM]
        )

        if not (username := payload.get("sub")):
            raise credentials_exception

        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception from None

    if not (
        user := await models.User.get_by_name(session, name=token_data.username)
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
    current_user: models.User = Security(get_current_user, scopes=["me"]),
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=st.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


async def required_auth(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=st.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/auth/login"},
        )
    return True
