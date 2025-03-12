# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as st

from ..audit.crud import AuditCRUD
from ..audit.schemas import Audit, AuditCreate
from .crud import WorkflowCRUD
from .schemas import Workflow, WorkflowCreate

workflow = APIRouter(
    prefix="/workflow",
    tags=["api", "workflow"],
    responses={st.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@workflow.get("/", response_model=list[Workflow])
async def api_workflow_read_all(
    skip: int = 0,
    limit: int = 100,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    return [wf async for wf in service.get_all(skip=skip, limit=limit)]


@workflow.post("/", response_model=Workflow)
async def api_workflow_create(
    wf: WorkflowCreate,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    db_workflow = await service.get_by_name(name=wf.name)
    if db_workflow:
        raise HTTPException(
            status_code=st.HTTP_302_FOUND,
            detail="Workflow already registered in observe database.",
        )
    return await service.create(workflow=wf)


@workflow.post("/{name}/audit", response_model=Audit)
async def api_workflow_create_audit(
    name: str,
    audit_trace: AuditCreate,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
    service_audit: AuditCRUD = Depends(AuditCRUD),
):
    db_workflow = await service.get_by_name(name=name)
    if not db_workflow:
        raise HTTPException(
            status_code=st.HTTP_302_FOUND,
            detail="Workflow does not registered in observe database.",
        )
    return await service_audit.create_with_trace(
        workflow_id=db_workflow.id,
        audit_trace=audit_trace,
    )
