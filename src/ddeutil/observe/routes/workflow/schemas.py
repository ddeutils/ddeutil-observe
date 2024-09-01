"""
To avoid confusion between the SQLAlchemy models and the Pydantic models, we
will have the file models.py with the SQLAlchemy models, and the file schemas.py
with the Pydantic models.

These Pydantic models define more or less a "schema" (a valid data shape).

So this will help us avoiding confusion while using both.

Read more: https://fastapi.tiangolo.com/tutorial/sql-databases/?h=database
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, TypeAdapter


class WorkflowBase(BaseModel):
    name: str
    desc: Optional[str] = None
    params: dict[str, Any]
    on: list[dict[str, Any]]
    jobs: dict[str, Any]


class WorkflowCreate(WorkflowBase):
    pass


class Workflow(WorkflowBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


Workflows = TypeAdapter(list[Workflow])


class ReleaseBase(BaseModel):
    release: datetime


class Release(ReleaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
