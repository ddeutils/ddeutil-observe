# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from sqlalchemy.orm import Session

from ...db import engine
from ...deps import get_db, get_templates
from . import crud, models
from .schemas import Pipeline, PipelineCreate


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
    hx_request: Annotated[Optional[str], Header(...)] = None,
    templates=Depends(get_templates),
):
    """Return all workflows."""
    if hx_request:
        return templates.TemplateResponse(
            "workflows/partials/show_workflows.html", {"request": request}
        )
    return templates.TemplateResponse(
        request=request, name="workflows/index.html"
    )


@workflows.post("/", response_model=Pipeline)
def create_workflow(pipeline: PipelineCreate, db: Session = Depends(get_db)):
    db_user = crud.get_pipeline_by_name(db, name=pipeline.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_pipeline(db=db, pipeline=pipeline)
