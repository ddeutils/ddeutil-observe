# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from textwrap import dedent
from typing import Optional

from ddeutil.observe.auth.schemas import UserCreateForm
from ddeutil.observe.routes.workflow.crud import (
    create_release_log,
    create_workflow,
)
from ddeutil.observe.routes.workflow.models import Base
from ddeutil.observe.routes.workflow.schemas import (
    ReleaseLogCreate,
    WorkflowCreate,
)
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

OUTSIDE_PATH: Path = Path(__file__).parent.parent


def initial_auth(db_path: Optional[Path] = None):
    db_path: Path = db_path or OUTSIDE_PATH / "observe.db"
    engine = create_async_engine(
        f"sqlite:///{db_path}",
        echo=False,
        pool_pre_ping=False,
        connect_args={"check_same_thread": False},
    )
    _sessionLocal = async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    Base.metadata.create_all(bind=engine)

    db = _sessionLocal()
    _ = db

    for _ in [
        UserCreateForm(
            username="admin", email="admin@mail.com", password="admin"
        ),
        UserCreateForm(username="user", email="user@mail.com", password="user"),
        UserCreateForm(username="lead", email="lead@mail.com", password="lead"),
        UserCreateForm(username="anon", email="anon@mail.com", password="anon"),
    ]:
        ...


def dotenv_setting() -> None:
    """Create .env file if this file in the current path does not exist."""
    env_path: Path = OUTSIDE_PATH / ".env"
    if not env_path.exists():
        logging.warning("Dot env file does not exists")
        env_str: str = dedent(
            """
            OBSERVE_CORE_TIMEZONE=Asia/Bangkok
            OBSERVE_CORE_SQLALCHEMY_DB_ASYNC_URL=sqlite+aiosqlite:///./observe.db
            OBSERVE_CORE_ACCESS_TOKEN_EXPIRE_MINUTES=30
            OBSERVE_CORE_REFRESH_TOKEN_EXPIRE_MINUTES=11520
            OBSERVE_LOG_DEBUG_MODE=true
            OBSERVE_LOG_SQLALCHEMY_DEBUG_MODE=true
            """
        ).strip()
        env_path.write_text(env_str)

    load_dotenv(env_path)


async def initial_db(db_path: Optional[Path] = None) -> None:
    """Initial data for testing to the observe database. This function will
    insert workflow and logging data that will show on monitoring page.
    The data will cover all testcases.
    """
    db_path: Path = db_path or OUTSIDE_PATH / "observe.test.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        echo=False,
        pool_pre_ping=False,
        connect_args={"check_same_thread": False},
    )
    _sessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        future=True,
        expire_on_commit=False,
        bind=engine,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session: AsyncSession = _sessionLocal()

    for wf in [
        WorkflowCreate(
            name="wf-scheduling",
            params={"asat-dt": {"type": "datetime"}},
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
            on=[{"cronjob": "* * * * *", "timezone": "Asia/Bangkok"}],
            jobs={"some-job": {"stages": [{"name": "Empty"}]}},
        ),
        WorkflowCreate(
            name="wf-batch-job-02",
            params={"asat-dt": {"type": "datetime"}},
            on=[{"cronjob": "*/15 */10 * * *", "timezone": "Asia/Bangkok"}],
            jobs={"some-job": {"stages": [{"name": "Empty"}]}},
        ),
        WorkflowCreate(
            name="wf-run-python-common",
            params={"asat-dt": {"type": "datetime"}},
            on=[{"cronjob": "*/3 12 * * *", "timezone": "Asia/Bangkok"}],
            jobs={"some-job": {"stages": [{"name": "Empty"}]}},
        ),
    ]:
        await create_workflow(session=session, workflow=wf)

    for data in [
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
        await create_release_log(session, 1, data)

    await session.close()


if __name__ == "__main__":
    asyncio.run(initial_db())
