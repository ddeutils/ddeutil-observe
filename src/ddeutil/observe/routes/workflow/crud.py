# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import logging
from calendar import monthrange
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import and_, case, desc, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import false

from ...crud import BaseCRUD
from .. import models as md
from .schemas import Workflow, WorkflowCreate

logger = logging.getLogger("uvicorn.error")


class WorkflowCRUD(BaseCRUD):

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_release: bool = False,
    ) -> AsyncIterator[Workflow]:
        """Get all workflows"""
        stmt = select(md.Workflow)
        if include_release:
            stmt = stmt.options(selectinload(md.Workflow.audits))
        if skip > 0 and limit > 0:
            stmt = stmt.offset(skip).limit(limit)
        for row in (
            await (
                await self.async_session.stream(stmt.order_by(md.Workflow.id))
            )
            .scalars()
            .all()
        ):
            yield Workflow.model_validate(row)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 1000,
    ) -> list[md.Workflow]:
        return (
            (
                await self.async_session.execute(
                    select(md.Workflow)
                    .filter(md.Workflow.delete_flag == false())
                    .offset(skip)
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )

    async def get(
        self,
        workflow_id: int,
    ) -> md.Workflow:
        return (
            await self.async_session.execute(
                select(md.Workflow)
                .filter(md.Workflow.id == workflow_id)
                .limit(1)
            )
        ).first()

    async def get_by_name(
        self,
        name: str,
    ) -> md.Workflow:
        return (
            await self.async_session.execute(
                select(md.Workflow)
                .filter(
                    md.Workflow.name == name,
                    md.Workflow.delete_flag == false(),
                )
                .limit(1)
            )
        ).scalar_one_or_none()

    async def search(self, search_text: str) -> list[md.Workflow]:
        if len(search_text) > 0:
            if not (search_text := search_text.strip().lower()):
                return []

            results = []
            for workflow in await self.list_all():
                text: str = f"{workflow.name} {workflow.desc or ''}".lower()
                logger.debug(f"Getting text: {text} | Search {search_text}")
                if search_text in text:
                    results.append(workflow)
            return results
        return await self.list_all()

    async def create(
        self,
        workflow: WorkflowCreate,
    ) -> md.Workflow:
        db_workflow = md.Workflow(
            name=workflow.name,
            desc=workflow.desc,
            params=workflow.params,
            on=workflow.on,
            jobs=workflow.jobs,
            valid_start=datetime.now(),
            valid_end=datetime(2999, 12, 31),
        )
        self.async_session.add(db_workflow)
        await self.async_session.flush()
        await self.async_session.commit()
        await self.async_session.refresh(db_workflow)
        return db_workflow

    async def get_workflow_runs(
        self,
        workflow_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get workflow runs data for the runs view."""

        # Build the query
        stmt = (
            select(
                md.Audit.id,
                md.Audit.release_id,
                md.Audit.status,
                md.Audit.start_time,
                md.Audit.end_time,
                md.Audit.execution_date,
                md.Audit.duration,
                md.Audit.error_message,
                md.Workflow.name.label("workflow_name"),
                md.Workflow.desc.label("workflow_desc"),
            )
            .join(md.Workflow, md.Audit.workflow_id == md.Workflow.id)
            .filter(md.Workflow.delete_flag == false())
        )

        # Apply filters
        if workflow_name:
            stmt = stmt.filter(md.Workflow.name == workflow_name)

        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            stmt = stmt.filter(md.Audit.execution_date >= start_dt)

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            stmt = stmt.filter(md.Audit.execution_date <= end_dt)

        if status:
            stmt = stmt.filter(md.Audit.status == status)

        # Order by execution date desc and limit
        stmt = stmt.order_by(desc(md.Audit.execution_date)).limit(limit)

        result = await self.async_session.execute(stmt)
        runs = []

        for row in result:
            run_data = {
                "id": row.id,
                "release_id": row.release_id,
                "workflow_name": row.workflow_name,
                "workflow_desc": row.workflow_desc,
                "status": row.status,
                "start_time": row.start_time,
                "end_time": row.end_time,
                "execution_date": row.execution_date,
                "duration": row.duration,
                "error_message": row.error_message,
            }
            runs.append(run_data)

        return runs

    async def get_workflow_calendar_data(
        self, workflow_name: Optional[str] = None, month: Optional[str] = None
    ) -> dict[str, Any]:
        """Get workflow calendar data for the calendar view."""

        if not month:
            month = datetime.now().strftime("%Y-%m")

        year, month_num = map(int, month.split("-"))
        _, last_day = monthrange(year, month_num)

        start_date = datetime(year, month_num, 1)
        end_date = datetime(year, month_num, last_day, 23, 59, 59)

        # Build the query
        stmt = (
            select(
                func.date(md.Audit.execution_date).label("run_date"),
                func.count(md.Audit.id).label("total_runs"),
                func.sum(
                    case((md.Audit.status == "success", 1), else_=0)
                ).label("success_runs"),
                func.sum(case((md.Audit.status == "failed", 1), else_=0)).label(
                    "failed_runs"
                ),
                func.sum(
                    case((md.Audit.status == "running", 1), else_=0)
                ).label("running_runs"),
                func.sum(
                    case((md.Audit.status == "pending", 1), else_=0)
                ).label("pending_runs"),
            )
            .join(md.Workflow, md.Audit.workflow_id == md.Workflow.id)
            .filter(
                and_(
                    md.Workflow.delete_flag == false(),
                    md.Audit.execution_date >= start_date,
                    md.Audit.execution_date <= end_date,
                )
            )
        )

        if workflow_name:
            stmt = stmt.filter(md.Workflow.name == workflow_name)

        stmt = stmt.group_by(func.date(md.Audit.execution_date))

        result = await self.async_session.execute(stmt)

        calendar_data = {
            "year": year,
            "month": month_num,
            "month_name": start_date.strftime("%B"),
            "days_in_month": last_day,
            "first_weekday": start_date.weekday(),
            "days": {},
        }

        for row in result:
            # row.run_date is a string in 'YYYY-MM-DD' format, extract day
            if isinstance(row.run_date, str):
                day = int(row.run_date.split("-")[2])
            else:
                day = row.run_date.day
            calendar_data["days"][day] = {
                "total_runs": row.total_runs,
                "success_runs": row.success_runs or 0,
                "failed_runs": row.failed_runs or 0,
                "running_runs": row.running_runs or 0,
                "pending_runs": row.pending_runs or 0,
            }

        return calendar_data

    async def get_workflow_stats(self, workflow_name: str) -> dict[str, Any]:
        """Get workflow statistics."""

        stmt = (
            select(
                func.count(md.Audit.id).label("total_runs"),
                func.sum(
                    case((md.Audit.status == "success", 1), else_=0)
                ).label("success_runs"),
                func.sum(case((md.Audit.status == "failed", 1), else_=0)).label(
                    "failed_runs"
                ),
                func.sum(
                    case((md.Audit.status == "running", 1), else_=0)
                ).label("running_runs"),
                func.avg(md.Audit.duration).label("avg_duration"),
            )
            .join(md.Workflow, md.Audit.workflow_id == md.Workflow.id)
            .filter(
                and_(
                    md.Workflow.name == workflow_name,
                    md.Workflow.delete_flag == false(),
                )
            )
        )

        result = await self.async_session.execute(stmt)
        row = result.first()

        if not row:
            return {
                "total_runs": 0,
                "success_runs": 0,
                "failed_runs": 0,
                "running_runs": 0,
                "avg_duration": "0s",
            }

        avg_duration = row.avg_duration
        avg_duration_str = f"{avg_duration:.2f}s" if avg_duration else "0s"

        return {
            "total_runs": row.total_runs or 0,
            "success_runs": row.success_runs or 0,
            "failed_runs": row.failed_runs or 0,
            "running_runs": row.running_runs or 0,
            "avg_duration": avg_duration_str,
        }

    async def get_run_detail(self, run_id: str) -> Optional[dict[str, Any]]:
        """Get detailed information about a specific workflow run."""

        stmt = (
            select(md.Audit, md.Workflow)
            .join(md.Workflow, md.Audit.workflow_id == md.Workflow.id)
            .options(
                selectinload(md.Audit.logs).selectinload(md.AuditLog.trace)
            )
            .filter(md.Audit.id == int(run_id))
        )

        result = await self.async_session.execute(stmt)
        row = result.first()

        if not row:
            return None

        audit, workflow = row

        return {
            "id": audit.id,
            "release_id": audit.release_id,
            "workflow_name": workflow.name,
            "workflow_desc": workflow.desc,
            "status": audit.status,
            "start_time": audit.start_time,
            "end_time": audit.end_time,
            "execution_date": audit.execution_date,
            "duration": audit.duration,
            "error_message": audit.error_message,
            "logs": (
                [
                    {
                        "id": log.id,
                        "workflow_name": log.workflow_name,
                        "release": log.release,
                        "type": log.type,
                        "context": log.context,
                        "run_id": log.run_id,
                        "parent_run_id": log.parent_run_id,
                        "release_create_date": log.release_create_date,
                        "traces": (
                            [
                                {
                                    "run_id": log.trace.run_id,
                                    "meta": (
                                        [
                                            {
                                                "trace_id": meta.trace_id,
                                                "mode": meta.mode,
                                                "datetime": meta.datetime,
                                                "message": meta.message,
                                                "filename": meta.filename,
                                                "lineno": meta.lineno,
                                            }
                                            for meta in log.trace.meta
                                        ]
                                        if log.trace.meta
                                        else []
                                    ),
                                }
                            ]
                            if log.trace
                            else []
                        ),
                    }
                    for log in audit.logs
                ]
                if audit.logs
                else []
            ),
        }
