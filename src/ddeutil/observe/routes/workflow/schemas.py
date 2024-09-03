from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, TypeAdapter


class WorkflowBase(BaseModel):
    """Base Workflow Pydantic model that does not include surrogate key column
    that create on the observe database.
    """

    name: str
    desc: Optional[str] = None
    params: dict[str, Any]
    on: list[dict[str, Any]]
    jobs: dict[str, Any]


class WorkflowCreate(WorkflowBase): ...


class Workflow(WorkflowBase):
    """Workflow Pydantic model that receive the Workflows model object
    from SQLAlchemy ORM.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    delete_flag: bool
    valid_start: datetime
    valid_end: datetime


Workflows = TypeAdapter(list[Workflow])


class ReleaseBase(BaseModel):
    release: datetime


class ReleaseCreate(ReleaseBase): ...


class Release(ReleaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_id: int


class ReleaseLog(ReleaseBase):
    log: dict[str, Any]


class LogBase(BaseModel):
    """Base Log Pydantic model that does not include surrogate key column
    that create on the observe database.
    """

    run_id: str
    log: dict[str, Any]
    release_id: int


class LogCreate(LogBase): ...


class Log(LogBase):
    model_config = ConfigDict(from_attributes=True)
