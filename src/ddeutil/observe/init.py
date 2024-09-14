"""
This file will contain script that will run before the app start to create the
super admin user.
"""

from __future__ import annotations

import asyncio

from sqlalchemy import insert, select

from .auth.models.user import User
from .auth.securities import get_password_hash
from .conf import config
from .db import sessionmanager
from .deps import get_async_session
from .utils import get_logger

logger = get_logger("ddeutil.observe")
sessionmanager.init(config.OBSERVE_SQLALCHEMY_DB_ASYNC_URL)


async def create_admin(session):
    username: str = config.WEB_ADMIN_USER
    email: str = config.WEB_ADMIN_EMAIL
    hashed_password = get_password_hash(config.WEB_ADMIN_PASS)

    # NOTE: Check this user already exists on the current backend database.
    user: User | None = (
        await session.execute(
            select(User).filter(User.username == username).limit(1)
        )
    ).scalar_one_or_none()

    if user is None:
        # metadata = MetaData()
        # user_table = Table(
        #     "user",
        #     metadata,
        #     Column("id", Integer, primary_key=True, index=True),
        #     Column(
        #         "username", String(64), nullable=False, unique=True, index=True
        #     ),
        #     Column("fullname", String(256), nullable=True, index=True),
        #     Column("email", String(128), nullable=False, index=True),
        #     Column("hashed_password", String, nullable=False),
        #     Column(
        #         "profile_image_url", String,
        #         default="https://profileimageurl.com"
        #     ),
        #     Column(
        #         "uuid", UUID(as_uuid=True), default=uuid.uuid4, unique=True
        #     ),
        #     Column(
        #         "created_at", DateTime(timezone=True), default=datetime.now,
        #         nullable=False
        #     ),
        #     Column(
        #         "updated_at",
        #         DateTime(timezone=True),
        #         onupdate=datetime.now,
        #         server_default=text("current_timestamp"),
        #         nullable=False,
        #     ),
        #     Column(
        #         "deleted_at",
        #         DateTime(timezone=True),
        #         default=null,
        #         nullable=True,
        #     ),
        #     Column("is_verified", Boolean, default=False),
        #     Column("is_active", Boolean, default=True),
        #     Column("is_superuser", Boolean, default=False),
        #     # Column("tier_id", Integer, ForeignKey("tier.id"), index=True),
        # )

        data = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "is_superuser": True,
        }
        async with sessionmanager.connect() as conn:
            # await conn.execute()
            await conn.execute(insert(User).values(data))
            await conn.commit()

        logger.info(f"Admin user {username} created successfully.")
    else:
        logger.info(f"Admin user {username} already exists.")


async def main():
    async with get_async_session() as session:
        await create_admin(session)


if __name__ == "__main__":
    # NOTE: Start running create function.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
