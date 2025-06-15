# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, Query, Request
from fastapi.templating import Jinja2Templates

from ...auth.deps import required_current_active_user
from ...deps import get_templates
from .crud import WorkflowCRUD
from .schemas import (
    WorkflowView,
    WorkflowViews,
)

logger = logging.getLogger("uvicorn.error")

# NOTE: This route require authentication step first.
workflow = APIRouter(
    prefix="/workflow",
    tags=["workflow", "frontend"],
    dependencies=[Depends(required_current_active_user)],
)


@workflow.get("/")
async def workflow_read_all(
    request: Request,
    crud: WorkflowCRUD = Depends(WorkflowCRUD),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Return all workflows."""
    workflows: list[WorkflowView] = WorkflowViews.validate_python(
        [wf async for wf in crud.get_all(include_release=True)]
    )
    return templates.TemplateResponse(
        request=request,
        name="workflow/workflow.html",
        context={
            "workflows": workflows,
            "search_text": "",
        },
    )


@workflow.get("/runs")
async def workflow_runs_view(
    request: Request,
    workflow_name: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    crud: WorkflowCRUD = Depends(WorkflowCRUD),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Workflow runs view similar to Airflow DAG runs."""
    # Set default date range (last 30 days)
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    # Get workflow runs data
    runs_data = await crud.get_workflow_runs(
        workflow_name=workflow_name,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )

    # Get all workflows for filter dropdown
    workflows = [wf async for wf in crud.get_all()]

    return templates.TemplateResponse(
        request=request,
        name="workflow/workflow-runs.html",
        context={
            "runs_data": runs_data,
            "workflows": workflows,
            "selected_workflow": workflow_name,
            "start_date": start_date,
            "end_date": end_date,
            "selected_status": status,
            "statuses": [
                "pending",
                "running",
                "success",
                "failed",
                "cancelled",
            ],
        },
    )


@workflow.get("/detail/{name}/page")
async def workflow_detail_page(
    name: str,
    request: Request,
    crud: WorkflowCRUD = Depends(WorkflowCRUD),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Workflow detail page similar to Airflow DAG page."""
    # Get workflow details
    _workflow_model = await crud.get_by_name(name)
    if _workflow_model is None:
        raise ValueError(f"Workflow name {name} does not exist")

    workflow = WorkflowView.model_validate(_workflow_model)

    # Get workflow statistics
    stats = await crud.get_workflow_stats(name)

    # Get recent runs (last 10)
    recent_runs = await crud.get_workflow_runs(workflow_name=name, limit=10)

    # Get all runs for the workflow
    all_runs = await crud.get_workflow_runs(workflow_name=name, limit=100)

    # Get stage details for the workflow
    stage_details = await crud.get_workflow_stage_details(name, limit=10)

    # Get duration data for charts
    duration_data = await crud.get_workflow_duration_data(name, limit=50)

    # Get task performance data
    task_performance = await crud.get_task_performance_data(name, limit=100)

    # Determine workflow status
    workflow_status = "active" if workflow.on else "inactive"

    # Calculate next and last run times
    next_run_time = await crud.get_workflow_next_run(name)
    last_run_time = recent_runs[0]["execution_date"] if recent_runs else None

    # Pre-serialize workflow data for JavaScript
    workflow_data = {
        "name": workflow.name,
        "desc": workflow.desc or "",
        "params": workflow.params,
        "on": workflow.on,
        "jobs": workflow.jobs,
        "delete_flag": workflow.delete_flag,
        "valid_start": (
            workflow.valid_start.isoformat() if workflow.valid_start else None
        ),
        "valid_end": (
            workflow.valid_end.isoformat() if workflow.valid_end else None
        ),
        "update_date": (
            workflow.update_date.isoformat() if workflow.update_date else None
        ),
    }

    return templates.TemplateResponse(
        request=request,
        name="workflow/workflow-detail.html",
        context={
            "workflow": workflow,
            "workflow_data": workflow_data,
            "workflow_status": workflow_status,
            "stats": stats,
            "recent_runs": recent_runs,
            "all_runs": all_runs,
            "stage_details": stage_details,
            "duration_data": duration_data,
            "task_performance": task_performance,
            "next_run_time": next_run_time,
            "last_run_time": last_run_time,
        },
    )


@workflow.get("/detail/{name}")
async def workflow_read_detail(
    name: str,
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    crud: WorkflowCRUD = Depends(WorkflowCRUD),
    templates: Jinja2Templates = Depends(get_templates),
):
    _workflow_model = await crud.get_by_name(name)
    if _workflow_model is None:
        raise ValueError(f"Workflow name {name} does not exists")
    _workflow: Optional[WorkflowView] = WorkflowView.model_validate(
        _workflow_model,
    )
    if hx_request:
        return templates.TemplateResponse(
            request=request,
            name="workflow/partials/workflow-detail.html",
            context={
                "workflow": _workflow,
            },
        )
    raise NotImplementedError(
        "Get the detail does not support for get directly"
    )


@workflow.get("/run/{run_id}")
async def workflow_run_detail(
    run_id: str,
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    crud: WorkflowCRUD = Depends(WorkflowCRUD),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Get details of a specific workflow run."""
    run_detail = await crud.get_run_detail(run_id)
    if not run_detail:
        raise ValueError(f"Workflow run {run_id} does not exist")

    if hx_request:
        return templates.TemplateResponse(
            request=request,
            name="workflow/partials/run-detail.html",
            context={
                "run": run_detail,
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="workflow/run-detail.html",
        context={
            "run": run_detail,
        },
    )


@workflow.get("/search/")
async def workflow_read_all_by_search(
    request: Request,
    search_text: str,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    crud: WorkflowCRUD = Depends(WorkflowCRUD),
    templates: Jinja2Templates = Depends(get_templates),
):
    workflows: list[WorkflowView] = WorkflowViews.validate_python(
        await crud.search(search_text=search_text)
    )
    if hx_request:
        return templates.TemplateResponse(
            request=request,
            name="workflow/partials/workflow-row.html",
            context={"workflows": workflows},
        )
    return templates.TemplateResponse(
        request=request,
        name="workflow/workflow.html",
        context={
            "workflows": workflows,
            "search_text": search_text,
        },
    )
