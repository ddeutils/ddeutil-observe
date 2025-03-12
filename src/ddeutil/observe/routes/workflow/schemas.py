# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class WorkflowBase(BaseModel):
    """Base Workflow Pydantic model that does not include surrogate key column
    that create on the observe database.
    """

    name: str = Field(description="A workflow name.")
    desc: Optional[str] = Field(
        default=None, description="A workflow description."
    )
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
    update_date: datetime


class WorkflowView(Workflow):
    model_config = ConfigDict(from_attributes=True)

    def dump_yaml(self) -> str: ...

    def dump_params(self) -> str:
        return json.dumps(
            self.params,
            sort_keys=True,
            indent=2,
            separators=(",", ": "),
        )


Workflows = TypeAdapter(list[Workflow])
WorkflowViews = TypeAdapter(list[WorkflowView])
