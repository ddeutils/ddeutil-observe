"""
This file will contain script that will run before the app start to create the
super admin user.
"""

import asyncio

from .deps import get_async_session


async def create_admin(session): ...


async def main():
    async with get_async_session() as session:
        await create_admin(session)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
