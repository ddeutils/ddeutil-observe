# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class ScheduleBase(BaseModel):
    """Base Log Pydantic model that does not include surrogate key column
    that create on the observe database.
    """

    run_id: str
    context: dict[str, Any] = Field(default_factory=dict)


class ScheduleCreate(ScheduleBase): ...


class Schedule(ScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    release_id: int


class ScheduleView(Schedule): ...


Schedules = TypeAdapter(list[Schedule])
ScheduleViews = TypeAdapter(list[ScheduleView])
