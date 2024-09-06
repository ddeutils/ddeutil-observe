# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql import false

from ...crud import BaseCRUD
from ...utils import get_logger
from . import models, schemas

logger = get_logger("ddeutil.observe")


def get_workflow(session: Session, workflow_id: int) -> models.Workflows:
    return (
        session.query(models.Workflows)
        .filter(models.Workflows.id == workflow_id)
        .first()
    )


def get_workflow_by_name(session: Session, name: str) -> models.Workflows:
    return (
        session.query(models.Workflows)
        .filter(
            models.Workflows.name == name,
            models.Workflows.delete_flag == false(),
        )
        .first()
    )


def create_workflow(
    session: Session,
    workflow: schemas.WorkflowCreate,
) -> models.Workflows:
    db_workflow = models.Workflows(
        name=workflow.name,
        desc=workflow.desc,
        params=workflow.params,
        on=workflow.on,
        jobs=workflow.jobs,
        valid_start=datetime.now(),
        valid_end=datetime(2999, 12, 31),
    )
    session.add(db_workflow)
    session.commit()
    session.refresh(db_workflow)
    return db_workflow


def list_workflows(
    session: Session,
    skip: int = 0,
    limit: int = 1000,
) -> list[models.Workflows]:
    return (
        session.query(models.Workflows)
        .filter(models.Workflows.delete_flag == false())
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_workflow(
    session: Session,
    search_text: str,
) -> list[models.Workflows]:
    if len(search_text) > 0:
        if not (search_text := search_text.strip().lower()):
            return []

        results = []
        for workflow in list_workflows(session=session):
            text: str = f"{workflow.name} {workflow.desc or ''}".lower()
            logger.debug(f"Getting text: {text} | Search {search_text}")
            if search_text in text:
                results.append(workflow)
        return results
    return list_workflows(session=session)


def get_release(
    session: Session,
    release: datetime,
) -> models.WorkflowReleases:
    return (
        session.query(models.WorkflowReleases)
        .filter(models.WorkflowReleases.release == release)
        .first()
    )


def create_release_log(
    session: Session,
    workflow_id: int,
    release_log: schemas.ReleaseLogCreate,
):
    db_release = models.WorkflowReleases(
        release=release_log.release,
        workflow_id=workflow_id,
    )
    session.add(db_release)
    session.commit()
    session.refresh(db_release)
    for log in release_log.logs:
        db_log = models.WorkflowLogs(
            run_id=log.run_id,
            context=log.context,
            release_id=db_release.id,
        )
        session.add(db_log)
        session.commit()
        session.refresh(db_log)
    return db_release


def get_log(session: Session, run_id: str) -> models.WorkflowLogs:
    return (
        session.query(models.WorkflowLogs)
        .filter(models.WorkflowLogs.run_id == run_id)
        .first()
    )


class WorkflowsCRUD(BaseCRUD):

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> AsyncIterator[schemas.Workflow]:
        async for wf in models.Workflows.get_all(
            self.async_session,
            skip=skip,
            limit=limit,
            include_release=True,
        ):
            yield schemas.Workflow.model_validate(wf)
