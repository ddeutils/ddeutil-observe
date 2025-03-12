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
import logging
from datetime import datetime
from typing import Optional

from fastapi.routing import APIRoute
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth.securities import get_password_hash
from .conf import config
from .db import sessionmanager

logger = logging.getLogger("uvicorn.error")
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
    from src.ddeutil.observe.routes.audit.schemas import AuditCreate
    from src.ddeutil.observe.routes.models import (
        Audit,
        AuditLog,
        Trace,
        TraceMeta,
        Workflow,
    )
    from src.ddeutil.observe.routes.trace.schemas import TraceCreate
    from src.ddeutil.observe.routes.workflow.schemas import WorkflowCreate

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
            valid_end=datetime(9999, 12, 31),
        )
        session.add(db_workflow)
        await session.commit()

    for audit_log in [
        AuditCreate(
            release="20240902093600",
            logs=[
                {
                    "name": "wf-scheduling",
                    "release": "2024-09-02 09:36:00+07:00",
                    "type": "task",
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
                {
                    "name": "wf-scheduling",
                    "release": "2024-09-02 09:36:00+07:00",
                    "type": "task",
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
            ],
        ),
        AuditCreate(
            release="20240901114700",
            logs=[
                {
                    "name": "wf-scheduling",
                    "release": "2024-09-01 11:47:00+07:00",
                    "type": "task",
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
                }
            ],
        ),
    ]:
        db_audit = Audit(
            release_id=audit_log.release,
            workflow_id=1,
        )
        session.add(db_audit)
        await session.commit()
        await session.refresh(db_audit)

        for log in audit_log.logs:
            db_audit_log = AuditLog(
                id=log.parent_run_id or log.run_id,
                audit_id=db_audit.id,
                workflow_name=log.name,
                release=log.release,
                type=log.type,
                context=log.context,
                parent_run_id=log.parent_run_id,
                run_id=log.run_id,
                release_create_date=log.update,
            )
            session.add(db_audit_log)
            await session.commit()

    for trace in [
        TraceCreate(
            run_id="635351540020240901114649502176",
            data={
                "meta": [
                    {
                        "mode": "stdout",
                        "datetime": "2025-03-12 10:28:12",
                        "process": 26232,
                        "thread": 7852,
                        "message": "(643202 ->       ) [POKING]: Start Poking: 'tmp-wf-scheduling-minute' from 2025-03-12 10:28:11 to 2025-03-12 10:29:11",
                        "filename": "workflow.py",
                        "lineno": 745,
                    },
                    {
                        "mode": "stdout",
                        "datetime": "2025-03-12 10:28:12",
                        "process": 26232,
                        "thread": 7852,
                        "message": "(643202 ->       ) [POKING]: The latest release, 2025-03-12 10:29:00, is not able to run on this minute",
                        "filename": "workflow.py",
                        "lineno": 785,
                    },
                ]
            },
        ),
    ]:
        db_trace = Trace(run_id=trace.run_id)
        session.add(db_trace)
        await session.commit()
        await session.refresh(db_trace)

        for index, meta in enumerate(trace.data.meta, start=1):
            db_trace_meta = TraceMeta(
                run_id=db_trace.run_id,
                trace_id=index,
                mode=meta.mode,
                datetime=meta.datetime,
                process=meta.process,
                thread=meta.thread,
                message=meta.message,
                filename=meta.filename,
                lineno=meta.lineno,
            )
            session.add(db_trace_meta)
            await session.commit()


async def main():
    from .deps import get_async_session

    async with get_async_session() as session:
        await create_admin(session)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
