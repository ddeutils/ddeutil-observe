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
from datetime import datetime
from typing import Optional

from fastapi.routing import APIRoute
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth.securities import get_password_hash
from .conf import config
from .db import sessionmanager
from .utils import get_logger

logger = get_logger("ddeutil.observe")
sessionmanager.init(config.sqlalchemy_db_async_url)


async def create_admin(session: AsyncSession) -> None:
    """Create Admin user."""
    from src.ddeutil.observe.auth.models import User

    from .db import sessionmanager

    username: str = config.web_admin_user

    # NOTE: Check this user already exists on the current backend database.
    user: Optional[User] = (
        await session.execute(
            select(User).filter(User.username == username).limit(1)
        )
    ).scalar_one_or_none()

    if user is None:
        password_hash = get_password_hash(config.web_admin_pass)

        async with sessionmanager.connect() as conn:
            await conn.execute(
                insert(User).values(
                    {
                        "username": username,
                        "email": config.web_admin_email,
                        "hashed_password": password_hash,
                        "is_superuser": True,
                    }
                )
            )
            await conn.commit()

        logger.info(f"Admin user {username} created successfully.")
    else:
        logger.warning(f"Admin user {username} already exists.")


async def create_role_policy(
    session: AsyncSession, routes: list[APIRoute]
) -> None:
    """Create Role and Policy."""
    from src.ddeutil.observe.auth.models import Role

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

    logger.info(f"{set(policy_routes)}")


async def create_workflows(session: AsyncSession):
    from src.ddeutil.observe.routes.workflow.models import (
        Workflow,
        WorkflowLog,
        WorkflowRelease,
    )
    from src.ddeutil.observe.routes.workflow.schemas import (
        ReleaseLogCreate,
        WorkflowCreate,
    )

    workflows = (await session.execute(select(Workflow))).scalars().all()
    if len(workflows) > 0:
        logger.warning("Skip initial workflow data because it already existed.")
        return

    for workflow in [
        WorkflowCreate(
            name="wf-scheduling",
            params={"asat-dt": {"type": "datetime"}, "notify": {"type": "str"}},
            on=[{"cronjob": "*/3 * * * *", "timezone": "Asia/Bangkok"}],
            jobs={"some-job": {"stages": [{"name": "Empty"}]}},
        ),
        WorkflowCreate(
            name="wf-trigger",
            params={"asat-dt": {"type": "datetime"}},
            on=[{"cronjob": "*/5 * * * *", "timezone": "Asia/Bangkok"}],
            jobs={"some-job": {"stages": [{"name": "Empty"}]}},
        ),
        WorkflowCreate(
            name="wf-batch-job-01",
            params={"asat-dt": {"type": "datetime"}},
            on=[
                {"cronjob": "*/5 * * * *", "timezone": "Asia/Bangkok"},
                {"cronjob": "*/10 * * * *", "timezone": "Asia/Bangkok"},
            ],
            jobs={"some-job": {"stages": [{"name": "Empty"}]}},
        ),
        WorkflowCreate(
            name="wf-batch-job-02",
            params={"asat-dt": {"type": "datetime"}},
            on=[{"cronjob": "*/15 */10 * * *", "timezone": "Asia/Bangkok"}],
            jobs={"some-job": {"stages": [{"name": "Empty"}]}},
        ),
        WorkflowCreate(
            name="wf-run-python-01",
            params={"asat-dt": {"type": "datetime"}},
            on=[{"cronjob": "*/3 12 * * *", "timezone": "Asia/Bangkok"}],
            jobs={"some-job": {"stages": [{"name": "Empty"}]}},
        ),
        WorkflowCreate(
            name="wf-run-python-02",
            params={"asat-dt": {"type": "datetime"}, "source": {"type": "str"}},
            on=[{"cronjob": "*/3 12 * * *", "timezone": "Asia/Bangkok"}],
            jobs={"some-job": {"stages": [{"name": "Empty"}]}},
        ),
    ]:
        db_workflow = Workflow(
            name=workflow.name,
            desc=workflow.desc,
            params=workflow.params,
            on=workflow.on,
            jobs=workflow.jobs,
            valid_start=datetime.now(),
            valid_end=datetime(2999, 12, 31),
        )
        session.add(db_workflow)
        await session.commit()

    for release_log in [
        ReleaseLogCreate(
            release="20240902093600",
            logs=[
                {
                    "run_id": "635351540020240902093554579053",
                    "context": {
                        "name": "wf-scheduling",
                        "on": "*/3 * * * *",
                        "release": "2024-09-02 09:36:00+07:00",
                        "context": {
                            "params": {"asat-dt": "2024-09-02 09:36:00+07:00"},
                            "jobs": {
                                "condition-job": {
                                    "matrix": {},
                                    "stages": {
                                        "6708019737": {"outputs": {}},
                                        "0663452000": {"outputs": {}},
                                    },
                                }
                            },
                        },
                        "parent_run_id": "635351540020240902093554579053",
                        "run_id": "635351540020240902093554579053",
                        "update": "2024-09-02 09:35:54.579053",
                    },
                },
                {
                    "run_id": "635351540020240902093554573333",
                    "context": {
                        "name": "wf-scheduling",
                        "on": "*/3 * * * *",
                        "release": "2024-09-02 09:36:00+07:00",
                        "context": {
                            "params": {"asat-dt": "2024-09-02 09:36:00+07:00"},
                            "jobs": {
                                "condition-job": {
                                    "matrix": {},
                                    "stages": {
                                        "6708019737": {"outputs": {}},
                                        "0663452000": {"outputs": {}},
                                    },
                                }
                            },
                        },
                        "parent_run_id": "635351540020240902093554573333",
                        "run_id": "635351540020240902093554573333",
                        "update": "2024-09-02 09:35:54.579053",
                    },
                },
            ],
        ),
        ReleaseLogCreate(
            release="20240901114700",
            logs=[
                {
                    "run_id": "635351540020240901114649502176",
                    "context": {
                        "name": "wf-scheduling",
                        "on": "* * * * *",
                        "release": "2024-09-01 11:47:00+07:00",
                        "context": {
                            "params": {"asat-dt": "2024-09-01 11:47:00+07:00"},
                            "jobs": {
                                "condition-job": {
                                    "matrix": {},
                                    "stages": {
                                        "6708019737": {"outputs": {}},
                                        "0663452000": {"outputs": {}},
                                    },
                                }
                            },
                        },
                        "parent_run_id": "635351540020240901114649502176",
                        "run_id": "635351540020240901114649502176",
                        "update": "2024-09-01 11:46:49.503175",
                    },
                }
            ],
        ),
    ]:
        db_release = WorkflowRelease(
            release=release_log.release,
            workflow_id=1,
        )
        session.add(db_release)
        await session.commit()
        await session.refresh(db_release)

        for log in release_log.logs:
            db_log = WorkflowLog(
                run_id=log.run_id,
                context=log.context,
                release_id=db_release.id,
            )
            session.add(db_log)
            await session.commit()


async def main():
    from .deps import get_async_session

    async with get_async_session() as session:
        await create_admin(session)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
