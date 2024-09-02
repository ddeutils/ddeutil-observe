from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class LogBase(BaseModel):
    """Base Workflow Pydantic model that does not include surrogate key column
    that create on the observe database.
    """

    run_id: str
    log: dict[str, Any]
    release_id = int


class Log(LogBase):
    model_config = ConfigDict(from_attributes=True)
