# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import time

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


@workflow.get("/{name}/logs")
async def api_workflow_get_logs(
    name: str,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Get logs for a specific workflow."""
    db_workflow = await service.get_by_name(name=name)
    if not db_workflow:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    # Get workflow runs and format as logs for now
    runs = await service.get_workflow_runs(workflow_name=name, limit=50)

    # Format logs for terminal display
    logs = []
    for run in runs:
        # Create multiple log entries per run to simulate detailed logging
        log_entries = [
            {
                "timestamp": (
                    run["start_time"].isoformat()
                    if run["start_time"]
                    else run["execution_date"].isoformat()
                ),
                "level": "INFO",
                "message": f"🚀 Starting {run['workflow_name']} execution (Run: {run['release_id']})",
            }
        ]

        if run["status"] in ["success", "failed", "cancelled"]:
            if run["status"] == "success":
                log_entries.append(
                    {
                        "timestamp": (
                            run["end_time"].isoformat()
                            if run["end_time"]
                            else run["execution_date"].isoformat()
                        ),
                        "level": "SUCCESS",
                        "message": f"✅ Completed {run['workflow_name']} successfully in {run['duration']}s",
                    }
                )
            elif run["status"] == "failed":
                log_entries.append(
                    {
                        "timestamp": (
                            run["end_time"].isoformat()
                            if run["end_time"]
                            else run["execution_date"].isoformat()
                        ),
                        "level": "ERROR",
                        "message": f"❌ Failed {run['workflow_name']}: {run['error_message'] or 'Unknown error'}",
                    }
                )
            else:  # cancelled
                log_entries.append(
                    {
                        "timestamp": (
                            run["end_time"].isoformat()
                            if run["end_time"]
                            else run["execution_date"].isoformat()
                        ),
                        "level": "WARNING",
                        "message": f"⚠️  Cancelled {run['workflow_name']} execution",
                    }
                )
        elif run["status"] == "running":
            log_entries.append(
                {
                    "timestamp": run["execution_date"].isoformat(),
                    "level": "INFO",
                    "message": f"⚙️  Processing {run['workflow_name']} - currently running...",
                }
            )

        logs.extend(log_entries)

    # Sort by timestamp descending (newest first)
    logs.sort(key=lambda x: x["timestamp"], reverse=True)

    return logs


@workflow.post("/{name}/run")
async def api_workflow_run(
    name: str,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Trigger a workflow run."""
    db_workflow = await service.get_by_name(name=name)
    if not db_workflow:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    # TODO: Implement actual workflow execution logic
    # For now, return a mock response
    return {
        "message": f"Workflow '{name}' run triggered successfully",
        "run_id": f"run-{name}-{int(time.time())}",
        "status": "pending",
    }


@workflow.get("/run/{run_id}/status")
async def api_workflow_run_status(
    run_id: str,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Get status of a specific workflow run."""
    try:
        run_detail = await service.get_run_detail(run_id)
        if not run_detail:
            raise HTTPException(
                status_code=st.HTTP_404_NOT_FOUND,
                detail="Run not found.",
            )

        return {
            "run_id": run_id,
            "status": run_detail["status"],
            "start_time": run_detail["start_time"],
            "end_time": run_detail["end_time"],
            "duration": run_detail["duration"],
        }
    except ValueError as e:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND,
            detail="Run not found.",
        ) from e


@workflow.post("/run/{run_id}/cancel")
async def api_workflow_run_cancel(
    run_id: str,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Cancel a workflow run."""
    try:
        run_detail = await service.get_run_detail(run_id)
        if not run_detail:
            raise HTTPException(
                status_code=st.HTTP_404_NOT_FOUND,
                detail="Run not found.",
            )

        # TODO: Implement actual cancellation logic
        return {
            "message": f"Run {run_id} cancellation requested",
            "status": "cancelled",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND,
            detail="Run not found.",
        ) from e


@workflow.post("/run/{run_id}/retry")
async def api_workflow_run_retry(
    run_id: str,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Retry a workflow run."""
    try:
        run_detail = await service.get_run_detail(run_id)
        if not run_detail:
            raise HTTPException(
                status_code=st.HTTP_404_NOT_FOUND,
                detail="Run not found.",
            )

        # TODO: Implement actual retry logic
        new_run_id = f"retry-{run_id}-{int(time.time())}"
        return {
            "message": f"Run {run_id} retry triggered",
            "new_run_id": new_run_id,
            "status": "pending",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND,
            detail="Run not found.",
        ) from e


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
