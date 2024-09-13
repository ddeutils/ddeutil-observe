# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi import status as st
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import sessionmanager
from ...deps import get_async_session
from . import crud, models
from .crud import WorkflowsCRUD
from .schemas import ReleaseLog, ReleaseLogCreate, Workflow, WorkflowCreate


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan for create workflow tables on target database."""
    async with sessionmanager.connect() as conn:
        # await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)
    yield


workflow = APIRouter(
    prefix="/workflow",
    tags=["api", "workflow"],
    lifespan=lifespan,
    responses={st.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@workflow.get("/", response_model=list[Workflow])
async def read_all(
    skip: int = 0,
    limit: int = 100,
    service: WorkflowsCRUD = Depends(WorkflowsCRUD),
):
    return [wf async for wf in service.get_all(skip=skip, limit=limit)]


@workflow.post("/", response_model=Workflow)
async def create_workflow(
    wf: WorkflowCreate,
    session: AsyncSession = Depends(get_async_session),
):
    db_workflow = await crud.get_workflow_by_name(session, name=wf.name)
    if db_workflow:
        raise HTTPException(
            status_code=st.HTTP_302_FOUND,
            detail="Workflow already registered in observe database.",
        )
    return await crud.create_workflow(session=session, workflow=wf)


@workflow.post("/{name}/release", response_model=ReleaseLog)
async def create_workflow_release(
    name: str,
    rl: ReleaseLogCreate,
    session: AsyncSession = Depends(get_async_session),
):
    db_workflow = await crud.get_workflow_by_name(session, name=name)
    if not db_workflow:
        raise HTTPException(
            status_code=st.HTTP_302_FOUND,
            detail="Workflow does not registered in observe database.",
        )
    return await crud.create_release_log(
        session=session,
        workflow_id=db_workflow.id,
        release_log=rl,
    )
