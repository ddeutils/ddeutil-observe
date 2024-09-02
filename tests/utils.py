from __future__ import annotations

from pathlib import Path

from ddeutil.observe.routes.workflow.crud import create_workflow
from ddeutil.observe.routes.workflow.models import Base
from ddeutil.observe.routes.workflow.schemas import WorkflowCreate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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
        create_workflow(db=db, workflow=wf)

    db.close()


if __name__ == "__main__":
    initial_db()
