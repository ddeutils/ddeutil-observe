# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserSchemaBase(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None


class UserSchemaCreate(UserSchemaBase):
    pass


class UserSchema(UserSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
