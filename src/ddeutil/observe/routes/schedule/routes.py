# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from fastapi import APIRouter, Depends

from ...auth.deps import required_current_active_user
from ...utils import get_logger

logger = get_logger("ddeutil.observe")

schedule = APIRouter(
    prefix="/schedule",
    tags=["schedule", "frontend"],
    # NOTE: This page require authentication step first.
    dependencies=[Depends(required_current_active_user)],
)
