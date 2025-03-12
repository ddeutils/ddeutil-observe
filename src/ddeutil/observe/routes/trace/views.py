# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, Request
from fastapi.templating import Jinja2Templates

from ...auth.deps import required_current_active_user
from ...deps import get_templates
from .crud import TraceCRUD
from .schemas import TraceView, TraceViews

logger = logging.getLogger("uvicorn.error")

trace = APIRouter(
    prefix="/trace",
    tags=["trace", "frontend"],
    # NOTE: This page require authentication step first.
    dependencies=[Depends(required_current_active_user)],
)


@trace.get("/")
async def trace_read_all(
    request: Request,
    crud: TraceCRUD = Depends(TraceCRUD),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Return all traces."""
    traces: list[TraceView] = TraceViews.validate_python(
        [wf async for wf in crud.list()]
    )
    return templates.TemplateResponse(
        request=request,
        name="trace/trace.html",
        context={"traces": traces},
    )


@trace.get("/search/")
async def trace_read_all_by_search(
    request: Request,
    search_text: str,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    templates: Jinja2Templates = Depends(get_templates),
):
    traces: list[TraceView] = TraceViews.validate_python()
    if hx_request:
        return templates.TemplateResponse(
            request=request,
            name="trace/partials/trace-row.html",
            context={"traces": traces},
        )
    return templates.TemplateResponse(request=request, name="trace/trace.html")
