# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from fastapi import status as st
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ...db import engine
from ...deps import get_db, get_templates
from ...utils import get_logger
from . import crud, models
from .schemas import Workflow, WorkflowCreate, Workflows

logger = get_logger("ddeutil.observe")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan for create workflow tables on target database."""
    models.Base.metadata.create_all(bind=engine)
    yield


workflow = APIRouter(prefix="/workflow", tags=["workflow"], lifespan=lifespan)


@workflow.get("/")
def read_workflows(
    request: Request,
    db: Session = Depends(get_db),
    templates=Depends(get_templates),
):
    """Return all workflows."""
    workflows: list[Workflow] = Workflows.validate_python(
        crud.list_workflows(db)
    )
    return templates.TemplateResponse(
        request=request,
        name="workflow/index.html",
        context={
            "workflows": workflows,
            "search_text": "",
        },
    )


@workflow.post("/", response_model=Workflow)
def create_workflow(wf: WorkflowCreate, db: Session = Depends(get_db)):
    db_workflow = crud.get_workflow_by_name(db, name=wf.name)
    if db_workflow:
        raise HTTPException(
            status_code=st.HTTP_302_FOUND,
            detail="Workflow already registered to observe database.",
        )
    return crud.create_workflow(db=db, workflow=wf)


@workflow.get("/search")
def search_workflows(
    request: Request,
    search_text: str,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
):
    workflows: list[Workflow] = Workflows.validate_python(
        crud.search_workflow(db=db, search_text=search_text)
    )
    if hx_request:
        return templates.TemplateResponse(
            "workflow/partials/search_results.html",
            {"request": request, "workflows": workflows},
        )
    return templates.TemplateResponse(
        request=request,
        name="workflow/index.html",
        context={
            "workflows": workflows,
            "search_text": search_text,
        },
    )
