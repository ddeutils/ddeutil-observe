# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

import bcrypt
import jwt
from fastapi import HTTPException, Request
from fastapi import status as st
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param

from ..conf import config

ALGORITHM: str = "HS256"


class OAuth2PasswordBearerOrCookie(OAuth2PasswordBearer):
    """OAuth2 flow for authentication using a bearer token obtained with a
    password. The token that will obtained able to be refresh token from the
    client cookie with `refresh_token` key.
    An instance of it would be used as a dependency."""

    # IMPORTANT: it will raise Request does not exists when use
    #   `from __future__ import annotations` on above script file.
    async def __call__(self, request: Request) -> Optional[str]:

        # NOTE: if the header has authorization key, it will use this value with
        #   the first priority.
        if request.headers.get("Authorization"):
            return await super().__call__(request)

        # NOTE: get authorization key from the cookie.
        authorization: Optional[str] = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=st.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


OAuth2Schema = OAuth2PasswordBearerOrCookie(
    tokenUrl="api/v1/auth/token",
    scheme_name="OAuth2PasswordBearerOrCookie",
    scopes={
        # NOTE: Baseline scope that use to any login user
        "me": "Read information about the current user.",
        # NOTE: Define workflow scopes.
        "workflows.get": "Read workflows and release logging.",
        "workflows.develop": "Create and update workflows and release logging.",
        "workflows.manage": "Drop and manage workflows and release logging.",
    },
    auto_error=False,
)


def create_access_token(
    subject: dict[str, Any],
    expires_delta: Union[timedelta, None] = None,
) -> str:
    """Create access token for an input subject value."""
    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = subject.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    subject: dict[str, Any],
    expires_delta: Union[timedelta, None] = None,
) -> str:
    """Create refresh token for an input subject value."""
    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = subject.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the password is equal."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    """Return hashed password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
