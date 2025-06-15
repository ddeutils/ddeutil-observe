# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from fastapi import APIRouter

from .audit.views import audit
from .notifications.routes import notification as notification_api
from .notifications.views import notification
from .profile.views import profile
from .trace.views import trace
from .workflow.routes import workflow as workflow_api
from .workflow.views import workflow

api_router = APIRouter()
api_router.include_router(workflow_api)
api_router.include_router(notification_api)


@api_router.get("/", tags=["api"])
async def health():
    return {"message": "Observe Application Standby ..."}
