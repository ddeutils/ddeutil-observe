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
from .schemas import Pipeline, PipelineCreate, Pipelines

logger = get_logger("ddeutil.observe")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan for create workflow tables on target database."""
    models.Base.metadata.create_all(bind=engine)
    yield


workflows = APIRouter(
    prefix="/workflows", tags=["workflows"], lifespan=lifespan
)


@workflows.get("/")
def read_workflows(
    request: Request,
    db: Session = Depends(get_db),
    templates=Depends(get_templates),
):
    """Return all workflows."""
    pipelines: list[Pipeline] = Pipelines.validate_python(
        crud.list_pipelines(db)
    )
    return templates.TemplateResponse(
        request=request,
        name="workflows/index.html",
        context={
            "pipelines": pipelines,
            "search_text": "",
        },
    )


@workflows.post("/", response_model=Pipeline)
def create_workflow(pipeline: PipelineCreate, db: Session = Depends(get_db)):
    db_pipeline = crud.get_pipeline_by_name(db, name=pipeline.name)
    if db_pipeline:
        raise HTTPException(
            status_code=st.HTTP_302_FOUND,
            detail="Pipeline already registered to observe database.",
        )
    pipeline = crud.create_pipeline(db=db, pipeline=pipeline)
    return pipeline


@workflows.get("/search")
def search_workflows(
    request: Request,
    search_text: str,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
):
    pipelines: list[Pipeline] = Pipelines.validate_python(
        crud.search_pipeline(db=db, search_text=search_text)
    )
    if hx_request:
        return templates.TemplateResponse(
            "workflows/partials/search_results.html",
            {"request": request, "pipelines": pipelines},
        )
    return templates.TemplateResponse(
        request=request,
        name="workflows/index.html",
        context={
            "pipelines": pipelines,
            "search_text": search_text,
        },
    )
