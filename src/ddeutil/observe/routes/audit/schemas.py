# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from ..trace.schemas import Trace, TraceCreate


class AuditBase(BaseModel):
    """Base Audit Pydantic model that does not include surrogate key column
    that create on the observe database.
    """

    release: int


class Audit(AuditBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_id: int


class AuditTraceCreate(AuditBase):
    logs: list[TraceCreate] = Field(default_factory=list)


class AuditTrace(AuditBase):
    model_config = ConfigDict(from_attributes=True)

    logs: list[Trace]
    workflow_id: int


class AuditView(Audit): ...


Audits = TypeAdapter(list[Audit])
AuditViews = TypeAdapter(list[AuditView])
