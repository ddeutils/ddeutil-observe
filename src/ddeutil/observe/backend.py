# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    BaseUser,
)
from starlette.requests import HTTPConnection

from .auth.deps import verify_refresh_token
from .auth.schemas import TokenDataSchema
from .deps import get_async_session


class FastAPIUser(BaseUser):
    """Sample API User that gives basic functionality"""

    def __init__(self, username: str):
        """FastAPIUser Constructor

        :param username: an username value
        """
        self.username: str = username

    @property
    def is_authenticated(self) -> bool:
        """Checks if the user is authenticated. This method essentially does
        nothing, but it could implement session logic for example.

        :rtype: bool
        :return: True if the user is authenticated
        """
        return True

    @property
    def display_name(self) -> str:
        """Display name of the user"""
        return self.username

    @property
    def identity(self) -> str:
        """Identification attribute of the user"""
        return self.username


class OAuth2Backend(AuthenticationBackend):
    """OAuth2 Backend"""

    async def authenticate(
        self,
        conn: HTTPConnection,
        session: AsyncSession = Depends(get_async_session),
    ) -> tuple[AuthCredentials, BaseUser]:
        """The authenticate method is invoked each time a route is called that
        the middleware is applied to.

        :param conn: An HTTP connection of FastAPI/Starlette
        :type conn: HTTPConnection
        :param session: A database async session
        :type session: AsyncSession

        :rtype: tuple[AuthCredentials, BaseUser]
        :return: A tuple of AuthCredentials (scopes) and a user object that is
            or inherits from BaseUser.
        """

        if (token := conn.cookies.get("refresh_token")) is None:
            return

        token_data: TokenDataSchema = await verify_refresh_token(
            token=token, session=session
        )

        return (
            AuthCredentials(scopes=token_data.scopes),
            FastAPIUser(token_data.username),
        )
