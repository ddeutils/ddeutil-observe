# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi import status as st
from sqlalchemy.orm.session import Session

from ...db import async_engine
from ...deps import get_session
from . import crud, models
from .crud import ReadWorkflows
from .schemas import ReleaseLog, ReleaseLogCreate, Workflow, WorkflowCreate


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan for create workflow tables on target database."""
    async with async_engine.begin() as conn:
        # await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)
    yield


workflow = APIRouter(
    prefix="/workflow",
    tags=["workflow"],
    lifespan=lifespan,
    responses={st.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@workflow.get("/", response_model=list[Workflow])
async def read_all(
    skip: int = 0,
    limit: int = 100,
    service: ReadWorkflows = Depends(ReadWorkflows),
):
    return [wf async for wf in service.execute(skip=skip, limit=limit)]


@workflow.post("/", response_model=Workflow)
def create_workflow(
    wf: WorkflowCreate, session: Session = Depends(get_session)
):
    db_workflow = crud.get_workflow_by_name(session, name=wf.name)
    if db_workflow:
        raise HTTPException(
            status_code=st.HTTP_302_FOUND,
            detail="Workflow already registered in observe database.",
        )
    return crud.create_workflow(session=session, workflow=wf)


@workflow.post("/{name}/release", response_model=ReleaseLog)
def create_workflow_release(
    name: str, rl: ReleaseLogCreate, session: Session = Depends(get_session)
):
    db_workflow = crud.get_workflow_by_name(session, name=name)
    if not db_workflow:
        raise HTTPException(
            status_code=st.HTTP_302_FOUND,
            detail="Workflow does not registered in observe database.",
        )
    return crud.create_release_log(
        session=session,
        workflow_id=db_workflow.id,
        release_log=rl,
    )
