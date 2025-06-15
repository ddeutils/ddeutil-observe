# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as st

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


@workflow.get("/{name}/runs")
async def api_workflow_get_runs(
    name: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Get workflow runs with optional filtering."""
    db_workflow = await service.get_by_name(name=name)
    if not db_workflow:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    runs = await service.get_workflow_runs(
        workflow_name=name,
        start_date=start_date,
        end_date=end_date,
        status=status,
        limit=limit,
    )

    return {
        "workflow_name": name,
        "runs": runs,
        "total_runs": len(runs),
    }


@workflow.get("/{name}/logs")
async def api_workflow_get_logs(
    name: str,
    date: Optional[str] = Query(
        None, description="Filter logs by date (YYYY-MM-DD)"
    ),
    limit: int = Query(100, le=500),
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Get workflow logs with optional date filtering."""
    db_workflow = await service.get_by_name(name=name)
    if not db_workflow:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    # Get runs for the specified date or recent runs
    start_date = date
    end_date = date

    runs = await service.get_workflow_runs(
        workflow_name=name,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    # Generate synthetic logs based on run data
    logs = []
    for run in runs:
        # Create multiple audit logs for each run to simulate detailed logging
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

    # Sort logs by timestamp
    logs.sort(key=lambda x: x["timestamp"])

    return {
        "workflow_name": name,
        "logs": logs,
        "total_logs": len(logs),
        "filter_date": date,
    }


@workflow.post("/{name}/run")
async def api_workflow_trigger_run(
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

    # TODO: Implement actual workflow triggering logic
    # For now, we'll just return a success response
    return {
        "message": f"Workflow '{name}' run triggered successfully",
        "run_id": f"run-{name}-{int(time.time())}",
        "status": "pending",
    }


@workflow.get("/run/{run_id}")
async def api_workflow_get_run_detail(
    run_id: str,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Get detailed information about a specific workflow run."""
    try:
        run_detail = await service.get_run_detail(run_id)
        if not run_detail:
            raise ValueError("Run not found")

        return {
            "id": run_detail["id"],
            "release_id": run_detail["release_id"],
            "workflow_name": run_detail["workflow_name"],
            "workflow_desc": run_detail["workflow_desc"],
            "status": run_detail["status"],
            "execution_date": run_detail["execution_date"],
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
async def api_workflow_cancel_run(
    run_id: str,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Cancel a running workflow."""
    try:
        # TODO: Implement actual cancellation logic
        # For now, we'll just return a success response
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
async def api_workflow_retry_run(
    run_id: str,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Retry a failed workflow run."""
    try:
        # TODO: Implement actual retry logic
        # For now, we'll just return a success response with a new run ID
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


@workflow.get("/{name}/audit/{release_id}")
async def api_workflow_get_audit_log(
    name: str,
    release_id: str,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Get audit logs for a specific workflow run."""
    db_workflow = await service.get_by_name(name=name)
    if not db_workflow:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    # TODO: Implement audit trace retrieval
    # For now, return basic information
    return {
        "workflow_name": name,
        "release_id": release_id,
        "audit_trace": {},
    }


@workflow.get("/{name}/duration-data")
async def api_workflow_get_duration_data(
    name: str,
    limit: int = 50,
    service: WorkflowCRUD = Depends(WorkflowCRUD),
):
    """Get workflow execution duration data for charting."""
    db_workflow = await service.get_by_name(name=name)
    if not db_workflow:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND,
            detail="Workflow not found.",
        )

    duration_data = await service.get_workflow_duration_data(
        workflow_name=name, limit=limit
    )

    return {
        "workflow_name": name,
        "data": duration_data,
        "total_records": len(duration_data),
    }
