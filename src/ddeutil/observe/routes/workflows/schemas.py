"""
To avoid confusion between the SQLAlchemy models and the Pydantic models, we
will have the file models.py with the SQLAlchemy models, and the file schemas.py
with the Pydantic models.

These Pydantic models define more or less a "schema" (a valid data shape).

So this will help us avoiding confusion while using both.

Read more: https://fastapi.tiangolo.com/tutorial/sql-databases/?h=database
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class PipelineBase(BaseModel):
    name: str
    desc: Optional[str] = None


class PipelineCreate(PipelineBase):
    pass


class Pipeline(PipelineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
