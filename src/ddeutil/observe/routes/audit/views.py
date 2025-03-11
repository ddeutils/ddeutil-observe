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
from .schemas import AuditView, AuditViews

logger = logging.getLogger("uvicorn.error")

audit = APIRouter(
    prefix="/audit",
    tags=["audit", "frontend"],
    # NOTE: This page require authentication step first.
    dependencies=[Depends(required_current_active_user)],
)


@audit.get("/")
async def audit_read_all(
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    templates: Jinja2Templates = Depends(get_templates),
):
    """Return all audits."""
    return templates.TemplateResponse(
        request=request,
        name="audit/audit.html",
        context={"audit": None},
    )


@audit.get("/search/")
async def audit_read_all_by_search(
    request: Request,
    search_text: str,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    templates: Jinja2Templates = Depends(get_templates),
):
    audits: list[AuditView] = AuditViews.validate_python()
    if hx_request:
        return templates.TemplateResponse(
            request=request,
            name="audit/partials/audit-row.html",
            context={"audits": audits},
        )
    return templates.TemplateResponse(request=request, name="trace/trace.html")
