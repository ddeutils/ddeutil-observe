# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
"""An initial module. This module will contain scripts that should run before
the app starting step for create the super admin user and policies.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi.routing import APIRoute, BaseRoute
from sqlalchemy import insert, select
from sqlalchemy.engine.result import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from .auth.securities import get_password_hash
from .conf import config
from .db import sessionmanager

logger = logging.getLogger("uvicorn.error")
sessionmanager.init(config.sqlalchemy_db_async_url)


async def create_admin(session: AsyncSession) -> None:
    """Create Admin user."""
    from src.ddeutil.observe.auth.models import User

    from .db import sessionmanager

    username: str = config.web_admin_user

    # NOTE: Check this user already exists on the current backend database.
    user: Optional[User] = (
        await session.execute(
            select(User).filter(User.username == username).limit(1)
        )
    ).scalar_one_or_none()

    if user is None:
        password_hash = get_password_hash(config.web_admin_pass)

        async with sessionmanager.connect() as conn:
            await conn.execute(
                insert(User).values(
                    {
                        "username": username,
                        "email": config.web_admin_email,
                        "hashed_password": password_hash,
                        "is_superuser": True,
                    }
                )
            )
            await conn.commit()

        logger.info(f"Admin user {username} created successfully.")
    else:
        logger.warning(f"Admin user {username} already exists.")


async def create_role_policy(
    session: AsyncSession, routes: list[BaseRoute]
) -> None:
    """Create Role and Policy."""
    from src.ddeutil.observe.auth.models import Role

    roles: Optional[ScalarResult[Role]] = (
        await session.execute(select(Role))
    ).scalars()
    logger.info(str(roles))

    policy_routes: list[str] = []
    for route in routes:
        if not isinstance(route, APIRoute):
            continue
        route_path: str = route.path.replace(config.api_prefix, "").strip("/")

        if not route_path:
            continue

        first_path: str = route_path.split("/", maxsplit=1)[0]
        if first_path == "index":
            continue

        policy_routes.append(first_path)

    logger.info(f"{set(policy_routes)}")


async def create_workflows(session: AsyncSession):
    import random

    from src.ddeutil.observe.routes.models import (
        Audit,
        AuditLog,
        Workflow,
        WorkflowLog,
    )
    from src.ddeutil.observe.routes.workflow.schemas import WorkflowCreate

    workflows = (await session.execute(select(Workflow))).scalars().all()
    if len(workflows) > 0:
        logger.warning("Skip initial workflow data because it already existed.")
        return

    # Create workflows
    workflow_data = [
        WorkflowCreate(
            name="wf-data-ingestion",
            desc="Daily data ingestion from external sources",
            params={"asat-dt": {"type": "datetime"}, "source": {"type": "str"}},
            on=[{"cronjob": "0 6 * * *", "timezone": "Asia/Bangkok"}],
            jobs={
                "ingest-job": {
                    "stages": [
                        {"name": "Extract", "timeout": 3600, "retries": 3},
                        {"name": "Load", "timeout": 1800, "retries": 2},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-etl-pipeline",
            desc="Extract, transform, and load data pipeline",
            params={
                "asat-dt": {"type": "datetime"},
                "batch_size": {"type": "int"},
            },
            on=[{"cronjob": "0 8 * * *", "timezone": "Asia/Bangkok"}],
            jobs={
                "etl-job": {
                    "stages": [
                        {"name": "Extract", "timeout": 3600, "retries": 3},
                        {"name": "Transform", "timeout": 7200, "retries": 2},
                        {"name": "Load", "timeout": 1800, "retries": 2},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-report-generation",
            desc="Generate daily business reports",
            params={
                "asat-dt": {"type": "datetime"},
                "report_type": {"type": "str"},
            },
            on=[{"cronjob": "0 10 * * *", "timezone": "Asia/Bangkok"}],
            jobs={
                "report-job": {
                    "stages": [
                        {"name": "Process", "timeout": 1800, "retries": 2},
                        {"name": "Generate", "timeout": 900, "retries": 1},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-ml-training",
            desc="Machine learning model training pipeline",
            params={
                "asat-dt": {"type": "datetime"},
                "model_version": {"type": "str"},
            },
            on=[{"cronjob": "0 2 * * 1", "timezone": "Asia/Bangkok"}],
            jobs={
                "ml-job": {
                    "stages": [
                        {"name": "Prepare", "timeout": 3600, "retries": 2},
                        {"name": "Train", "timeout": 14400, "retries": 1},
                        {"name": "Validate", "timeout": 1800, "retries": 2},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-data-validation",
            desc="Validate data quality and integrity",
            params={
                "asat-dt": {"type": "datetime"},
                "table_name": {"type": "str"},
            },
            on=[{"cronjob": "0 */4 * * *", "timezone": "Asia/Bangkok"}],
            jobs={
                "validation-job": {
                    "stages": [
                        {"name": "Check", "timeout": 1800, "retries": 2},
                        {"name": "Report", "timeout": 900, "retries": 1},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-backup-cleanup",
            desc="Cleanup old backup files and archives",
            params={
                "asat-dt": {"type": "datetime"},
                "retention_days": {"type": "int"},
            },
            on=[{"cronjob": "0 1 * * 0", "timezone": "Asia/Bangkok"}],
            jobs={
                "cleanup-job": {
                    "stages": [
                        {"name": "Scan", "timeout": 1800, "retries": 2},
                        {"name": "Delete", "timeout": 900, "retries": 1},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-data-migration",
            desc="Database migration and schema updates",
            params={
                "asat-dt": {"type": "datetime"},
                "target_version": {"type": "str"},
            },
            on=[{"cronjob": "0 3 * * 0", "timezone": "Asia/Bangkok"}],
            jobs={
                "migration-job": {
                    "stages": [
                        {"name": "Backup", "timeout": 3600, "retries": 2},
                        {"name": "Migrate", "timeout": 7200, "retries": 1},
                        {"name": "Verify", "timeout": 1800, "retries": 2},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-api-sync",
            desc="Synchronize data with external APIs",
            params={
                "asat-dt": {"type": "datetime"},
                "api_endpoint": {"type": "str"},
            },
            on=[{"cronjob": "0 */2 * * *", "timezone": "Asia/Bangkok"}],
            jobs={
                "sync-job": {
                    "stages": [
                        {"name": "Connect", "timeout": 300, "retries": 3},
                        {"name": "Sync", "timeout": 1800, "retries": 2},
                        {"name": "Verify", "timeout": 900, "retries": 1},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-data-archiving",
            desc="Archive historical data to cold storage",
            params={
                "asat-dt": {"type": "datetime"},
                "retention_period": {"type": "int"},
            },
            on=[{"cronjob": "0 4 * * 0", "timezone": "Asia/Bangkok"}],
            jobs={
                "archive-job": {
                    "stages": [
                        {"name": "Identify", "timeout": 1800, "retries": 2},
                        {"name": "Compress", "timeout": 3600, "retries": 1},
                        {"name": "Transfer", "timeout": 7200, "retries": 2},
                        {"name": "Cleanup", "timeout": 1800, "retries": 1},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-performance-test",
            desc="Run performance tests on critical systems",
            params={
                "asat-dt": {"type": "datetime"},
                "test_scenario": {"type": "str"},
            },
            on=[{"cronjob": "0 5 * * 0", "timezone": "Asia/Bangkok"}],
            jobs={
                "test-job": {
                    "stages": [
                        {"name": "Setup", "timeout": 1800, "retries": 2},
                        {"name": "Execute", "timeout": 3600, "retries": 1},
                        {"name": "Analyze", "timeout": 1800, "retries": 2},
                        {"name": "Report", "timeout": 900, "retries": 1},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-security-scan",
            desc="Perform security vulnerability scans",
            params={
                "asat-dt": {"type": "datetime"},
                "scan_type": {"type": "str"},
            },
            on=[{"cronjob": "0 2 * * 0", "timezone": "Asia/Bangkok"}],
            jobs={
                "scan-job": {
                    "stages": [
                        {"name": "Initialize", "timeout": 900, "retries": 2},
                        {"name": "Scan", "timeout": 7200, "retries": 1},
                        {"name": "Analyze", "timeout": 3600, "retries": 2},
                        {"name": "Report", "timeout": 1800, "retries": 1},
                    ]
                }
            },
        ),
        WorkflowCreate(
            name="wf-data-enrichment",
            desc="Enrich raw data with additional attributes",
            params={
                "asat-dt": {"type": "datetime"},
                "enrichment_type": {"type": "str"},
            },
            on=[{"cronjob": "0 7 * * *", "timezone": "Asia/Bangkok"}],
            jobs={
                "enrichment-job": {
                    "stages": [
                        {"name": "Extract", "timeout": 1800, "retries": 2},
                        {"name": "Enrich", "timeout": 3600, "retries": 2},
                        {"name": "Validate", "timeout": 1800, "retries": 1},
                        {"name": "Load", "timeout": 1800, "retries": 2},
                    ]
                }
            },
        ),
    ]

    workflow_models = []
    for workflow in workflow_data:
        db_workflow = Workflow(
            name=workflow.name,
            desc=workflow.desc,
            params=workflow.params,
            on=workflow.on,
            jobs=workflow.jobs,
            valid_start=datetime.now(),
            valid_end=datetime(9999, 12, 31),
        )
        session.add(db_workflow)
        await session.flush()
        workflow_models.append(db_workflow)

    await session.commit()

    # Create realistic workflow runs for the past 30 days
    base_date = datetime.now()
    statuses = ["success", "failed", "running", "pending", "cancelled"]

    for workflow in workflow_models:
        for i in range(30):  # Last 30 days
            execution_date = base_date - timedelta(days=i)

            # Skip some days randomly to make it more realistic
            if random.random() < 0.3:
                continue

            # Create 1-3 runs per day for some workflows
            num_runs = (
                random.randint(1, 3)
                if workflow.name in ["wf-data-ingestion", "wf-etl-pipeline"]
                else 1
            )

            for run_num in range(num_runs):
                status = random.choices(statuses, weights=[70, 20, 3, 5, 2])[0]

                # Calculate realistic start and end times
                start_time = execution_date.replace(
                    hour=random.randint(6, 23),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59),
                )

                duration = None
                end_time = None
                error_message = None

                if status == "success":
                    duration = random.randint(
                        30, 1800
                    )  # 30 seconds to 30 minutes
                    end_time = start_time + timedelta(seconds=duration)
                elif status == "failed":
                    duration = random.randint(
                        10, 600
                    )  # 10 seconds to 10 minutes
                    end_time = start_time + timedelta(seconds=duration)
                    error_message = random.choice(
                        [
                            "Connection timeout to external API",
                            "Insufficient memory allocation",
                            "Data validation failed",
                            "Network connection error",
                            "File not found in source location",
                        ]
                    )
                elif status == "cancelled":
                    duration = random.randint(5, 300)  # 5 seconds to 5 minutes
                    end_time = start_time + timedelta(seconds=duration)
                elif status == "running":
                    # Only for recent runs
                    if i <= 1:
                        start_time = execution_date.replace(
                            hour=datetime.now().hour,
                            minute=datetime.now().minute
                            - random.randint(5, 60),
                            second=datetime.now().second,
                        )

                release_id = f"{workflow.name}-{execution_date.strftime('%Y%m%d')}-{run_num + 1:02d}"

                audit = Audit(
                    release_id=release_id,
                    workflow_id=workflow.id,
                    status=status,
                    start_time=start_time,
                    end_time=end_time,
                    execution_date=execution_date,
                    duration=duration,
                    error_message=error_message,
                )
                session.add(audit)
                await session.flush()

                # Create multiple audit logs for each run to simulate detailed logging
                log_types = (
                    ["start", "task", "end"]
                    if status in ["success", "failed"]
                    else ["start"]
                )

                for idx, log_type in enumerate(log_types):
                    log_time = start_time + timedelta(
                        seconds=idx
                        * (duration // len(log_types) if duration else 10)
                    )

                    if log_type == "start":
                        log_context = {
                            "params": {"asat-dt": execution_date.isoformat()},
                            "status": "running",
                            "stage": "initialization",
                            "progress": "0%",
                            "stage_details": {
                                "name": "initialization",
                                "timeout": 300,
                                "retries": 2,
                                "start_time": log_time.isoformat(),
                                "end_time": None,
                                "duration": None,
                            },
                        }
                    elif log_type == "task":
                        # Get job stages from workflow
                        job_stages = []
                        for _, job in workflow.jobs.items():
                            if isinstance(job, dict) and "stages" in job:
                                job_stages.extend(job["stages"])

                        if not job_stages:
                            # If no stages defined, use default stages
                            job_stages = [
                                {
                                    "name": "Extract",
                                    "timeout": 1800,
                                    "retries": 2,
                                },
                                {
                                    "name": "Transform",
                                    "timeout": 1800,
                                    "retries": 2,
                                },
                                {"name": "Load", "timeout": 1800, "retries": 2},
                            ]

                        current_stage = job_stages[idx % len(job_stages)]

                        log_context = {
                            "params": {"asat-dt": execution_date.isoformat()},
                            "status": "running",
                            "stage": current_stage.get("name", "processing"),
                            "progress": f"{((idx + 1) * 100) // len(log_types)}%",
                            "stage_details": {
                                "name": current_stage.get("name", "processing"),
                                "timeout": current_stage.get("timeout", 1800),
                                "retries": current_stage.get("retries", 2),
                                "start_time": log_time.isoformat(),
                                "end_time": None,
                                "duration": None,
                            },
                        }
                    else:  # end
                        log_context = {
                            "params": {"asat-dt": execution_date.isoformat()},
                            "status": status,
                            "stage": "completion",
                            "progress": "100%",
                            "stage_details": {
                                "name": "completion",
                                "timeout": 300,
                                "retries": 1,
                                "start_time": log_time.isoformat(),
                                "end_time": (
                                    log_time + timedelta(seconds=30)
                                ).isoformat(),
                                "duration": 30,
                            },
                            "duration": duration,
                            "error": error_message,
                        }

                    audit_log = AuditLog(
                        id=f"log-{audit.id}-{idx:02d}-{random.randint(1000, 9999)}",
                        audit_id=str(audit.id),
                        workflow_name=workflow.name,
                        release=execution_date,
                        type=log_type,
                        context=log_context,
                        parent_run_id=None,
                        run_id=release_id,
                        release_create_date=log_time,
                    )
                    session.add(audit_log)

                    # Create workflow logs for each audit log
                    log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
                    log_messages = {
                        "start": [
                            "Workflow execution started",
                            "Initializing workflow parameters",
                            "Loading configuration",
                            "Setting up environment",
                        ],
                        "task": [
                            "Processing stage: {stage}",
                            "Executing task in stage: {stage}",
                            "Running stage: {stage}",
                            "Stage {stage} in progress",
                        ],
                        "end": [
                            "Workflow execution completed",
                            "All stages finished successfully",
                            "Workflow execution failed",
                            "Workflow execution cancelled",
                        ],
                    }

                    # Create 2-4 logs per audit log
                    num_logs = random.randint(2, 4)
                    for log_idx in range(num_logs):
                        log_time_offset = random.randint(1, 10)
                        log_timestamp = log_time + timedelta(
                            seconds=log_idx * log_time_offset
                        )

                        # Select appropriate log level based on status and stage
                        if status == "failed" and log_type == "end":
                            level = "ERROR"
                        elif status == "cancelled" and log_type == "end":
                            level = "WARNING"
                        else:
                            level = random.choices(
                                log_levels, weights=[60, 20, 10, 10]
                            )[0]

                        # Select appropriate message based on log type
                        message_template = random.choice(log_messages[log_type])
                        if log_type == "task":
                            message = message_template.format(
                                stage=log_context["stage"]
                            )
                        else:
                            message = message_template

                        # Add additional context for errors
                        context = None
                        if level == "ERROR":
                            context = {
                                "error_code": f"ERR_{random.randint(1000, 9999)}",
                                "error_details": (
                                    error_message
                                    if error_message
                                    else "Unknown error occurred"
                                ),
                                "stack_trace": "Traceback (most recent call last):\n  File 'workflow.py', line 123, in execute_stage\n    result = stage.run()\nRuntimeError: Operation failed",
                            }

                        workflow_log = WorkflowLog(
                            workflow_id=workflow.id,
                            audit_id=audit.id,
                            level=level,
                            message=message,
                            timestamp=log_timestamp,
                            stage=log_context["stage"],
                            context=context,
                        )
                        session.add(workflow_log)

    await session.commit()


async def main():
    from .deps import get_async_session

    async with get_async_session() as session:
        await create_admin(session)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
