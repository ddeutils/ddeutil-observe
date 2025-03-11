# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from fastapi import APIRouter
from fastapi import status as st

from ...utils import get_logger

logger = get_logger("ddeutil.observe")

trace = APIRouter(
    prefix="/trace",
    tags=["api", "trace"],
    responses={st.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)
