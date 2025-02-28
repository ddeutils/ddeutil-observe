# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
"""An initial module. This module will contain scripts that should run before
the app starting step for create the super admin user and policies.
"""

from __future__ import annotations

import asyncio
from typing import Optional

from fastapi.routing import APIRoute
from sqlalchemy import insert, select

from .auth.models import Role, User
from .auth.securities import get_password_hash
from .conf import config
from .db import sessionmanager
from .deps import get_async_session
from .utils import get_logger

logger = get_logger("ddeutil.observe")
sessionmanager.init(config.sqlalchemy_db_async_url)


async def create_admin(session) -> None:
    """Create Admin user."""
    username: str = config.web_admin_user
    email: str = config.web_admin_email
    hashed_password = get_password_hash(config.web_admin_pass)

    # NOTE: Check this user already exists on the current backend database.
    user: Optional[User] = (
        await session.execute(
            select(User).filter(User.username == username).limit(1)
        )
    ).scalar_one_or_none()

    if user is None:
        async with sessionmanager.connect() as conn:
            await conn.execute(
                insert(User).values(
                    {
                        "username": username,
                        "email": email,
                        "hashed_password": hashed_password,
                        "is_superuser": True,
                    }
                )
            )
            await conn.commit()

        logger.info(f"Admin user {username} created successfully.")
    else:
        logger.info(f"Admin user {username} already exists.")


async def create_role_policy(session, routes: list[APIRoute]) -> None:
    """Create Role and Policy."""
    roles: Optional[Role] = (await session.execute(select(Role))).scalars()
    logger.info(str(roles))

    policy_routes: list[str] = []
    for route in routes:
        if not isinstance(route, APIRoute):
            continue
        route_path: str = route.path.replace(config.api_prefix, "").strip("/")

        if not route_path:
            continue

        first_path: str = route_path.split("/", maxsplit=1)[0]
        if first_path == "index":
            continue

        policy_routes.append(first_path)

    print(set(policy_routes))


async def main():
    async with get_async_session() as session:
        await create_admin(session)


if __name__ == "__main__":
    # NOTE: Start running create function.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
