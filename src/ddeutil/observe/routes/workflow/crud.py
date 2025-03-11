# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import false

from ...crud import BaseCRUD
from ...utils import get_logger
from .. import models as md
from .schemas import Workflow, WorkflowCreate

logger = get_logger("ddeutil.observe")


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
