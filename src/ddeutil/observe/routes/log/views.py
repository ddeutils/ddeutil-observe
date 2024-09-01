# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, FastAPI, Header, Request

from ...db import engine
from ...deps import get_templates
from . import models


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan for create log tables on target database."""
    models.Base.metadata.create_all(bind=engine)
    yield


log = APIRouter(prefix="/log", tags=["log"], lifespan=lifespan)


@log.get("/")
def read_logs(
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    templates=Depends(get_templates),
):
    """Return all workflows."""
    if hx_request:
        return templates.TemplateResponse(
            "log/partials/show_add_author_form.html", {"request": request}
        )
    return templates.TemplateResponse(request=request, name="log/index.html")
