# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class AuditLog(BaseModel):
    name: str = Field(description="A workflow name.")
    release: datetime = Field(description="A release datetime.")
    type: str = Field(description="A running type before logging.")
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="A context that receive from a workflow execution result.",
    )
    parent_run_id: Optional[str] = Field(default=None)
    run_id: str
    update: datetime = Field(default_factory=datetime.now)
    execution_time: float = Field(default=0)


class AuditLogView(AuditLog):
    model_config = ConfigDict(from_attributes=True)


class AuditBase(BaseModel):
    """Base Audit Pydantic model that does not include surrogate key column
    that create on the observe database.
    """

    release: int


class Audit(AuditBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_id: int
    logs: list[AuditLog] = Field(default_factory=list)


class AuditCreate(AuditBase):
    logs: list[AuditLog] = Field(default_factory=list)


class AuditView(Audit): ...


Audits = TypeAdapter(list[Audit])
AuditViews = TypeAdapter(list[AuditView])
