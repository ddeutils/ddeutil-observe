from __future__ import annotations

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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def initial_auth(db_path: Path | None = None):
    db_path: Path = db_path or Path(__file__).parent.parent / "observe.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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


def initial_db(db_path: Path | None = None):
    """Initial data to observe database for testing"""
    db_path: Path = db_path or Path(__file__).parent.parent / "observe.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

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
        create_workflow(session=db, workflow=wf)

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
        create_release_log(db, 1, data)

    db.close()


if __name__ == "__main__":
    initial_db()
