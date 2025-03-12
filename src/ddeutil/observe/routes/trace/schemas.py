# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class TraceMeta(BaseModel):
    mode: str
    datetime: datetime
    process: int
    thread: int
    message: str
    filename: str
    lineno: int


class TraceData(BaseModel):
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    meta: list[TraceMeta]


class TraceBase(BaseModel):
    """Base Log Pydantic model that does not include surrogate key column
    that create on the observe database.
    """

    run_id: str
    data: TraceData = Field(default_factory=TraceData)


class TraceCreate(TraceBase): ...


class Trace(TraceBase):
    model_config = ConfigDict(from_attributes=True)

    release_id: int


class TraceView(Trace): ...


Traces = TypeAdapter(list[Trace])
TraceViews = TypeAdapter(list[TraceView])
