# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

import jwt
from fastapi import Depends, HTTPException, Request, Security
from fastapi import status as st
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.security.utils import get_authorization_scheme_param
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ..conf import config
from ..deps import get_async_session
from . import models
from .schemas import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


class OAuth2PasswordBearerCookie(OAuth2PasswordBearer):

    # NOTE: it will raise Request does not exists when use
    #   `from __future__ import annotations` on above script file.
    async def __call__(self, request: Request) -> Optional[str]:
        if request.headers.get("Authorization"):
            return await super().__call__(request)

        authorization: str = request.cookies.get("access_token")
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


oauth2_scheme = OAuth2PasswordBearerCookie(
    tokenUrl="api/v1/auth/token",
    scopes={
        "me": "Read information about the current user.",
        "workflows": "Read items.",
    },
    auto_error=False,
)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Union[timedelta, None] = None,
) -> str:
    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    if isinstance(subject, dict):
        to_encode = subject.copy()
        to_encode.update({"exp": expire})
    else:
        to_encode = {"exp": expire, "sub": str(subject)}

    return jwt.encode(to_encode, config.OBSERVE_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    subject: Union[str, Any], expires_delta: Union[timedelta, None] = None
) -> str:
    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    if isinstance(subject, dict):
        to_encode = subject.copy()
        to_encode.update({"exp": expire})
    else:
        to_encode = {"exp": expire, "sub": str(subject)}

    return jwt.encode(
        to_encode, config.OBSERVE_REFRESH_SECRET_KEY, algorithm=ALGORITHM
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


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
