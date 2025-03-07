# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, Request
from fastapi.templating import Jinja2Templates

from ...auth.deps import required_current_active_user
from ...deps import get_templates
from ...utils import get_logger

logger = get_logger("ddeutil.observe")

log = APIRouter(
    prefix="/log",
    tags=["log", "frontend"],
    # NOTE: This page require authentication step first.
    dependencies=[Depends(required_current_active_user)],
)


@log.get("/logs")
async def read_logs(
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    templates: Jinja2Templates = Depends(get_templates),
):
    """Return all logs."""
    if hx_request:
        return templates.TemplateResponse(
            "log/partials/log_results.html", {"request": request}
        )
    return templates.TemplateResponse(request=request, name="log/log.html")
