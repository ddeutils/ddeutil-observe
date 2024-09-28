from __future__ import annotations

import asyncio
from pathlib import Path

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
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def initial_auth(db_path: Path | None = None):
    db_path: Path = db_path or Path(__file__).parent.parent / "observe.db"
    engine = create_async_engine(
        f"sqlite:///{db_path}",
        echo=False,
        pool_pre_ping=False,
        connect_args={"check_same_thread": False},
    )
    SessionLocal = async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
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


async def initial_db(db_path: Path | None = None) -> None:
    """Initial data for testing to the observe database. This function will
    insert workflow and logging data that will show on monitoring page.
    The data will cover all testcases.
    """
    db_path: Path = db_path or Path(__file__).parent.parent / "observe.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        echo=False,
        pool_pre_ping=False,
        connect_args={"check_same_thread": False},
    )
    SessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        future=True,
        expire_on_commit=False,
        bind=engine,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session: AsyncSession = SessionLocal()

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
