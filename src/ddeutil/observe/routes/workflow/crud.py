# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql import false

from . import models, schemas


def get_workflow(db: Session, workflow_id: int) -> models.Workflows:
    return (
        db.query(models.Workflows)
        .filter(models.Workflows.id == workflow_id)
        .first()
    )


def get_workflow_by_name(db: Session, name: str) -> models.Workflows:
    return (
        db.query(models.Workflows)
        .filter(
            models.Workflows.name == name,
            models.Workflows.delete_flag == false(),
        )
        .first()
    )


def create_workflow(
    db: Session,
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
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


def list_workflows(
    db: Session,
    skip: int = 0,
    limit: int = 1000,
) -> list[models.Workflows]:
    return (
        db.query(models.Workflows)
        .filter(models.Workflows.delete_flag == false())
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_workflow(
    db: Session,
    search_text: str,
) -> list[models.Workflows]:
    if len(search_text) > 1:
        if not (search_text := search_text.strip().lower()):
            return []

        results = []
        for workflow in list_workflows(db=db):
            text: str = f"{workflow.name} {workflow.desc or ''}".lower()
            if search_text in text:
                results.append(workflow)
        return results
    return list_workflows(db=db)


def get_release(
    db: Session,
    release: datetime,
) -> models.WorkflowReleases:
    return (
        db.query(models.WorkflowReleases)
        .filter(models.WorkflowReleases.release == release)
        .first()
    )


def create_release(
    db: Session,
    workflow: schemas.Workflow,
    release: schemas.ReleaseCreate,
) -> schemas.ReleaseCreate:
    db_release = models.WorkflowReleases(
        release=release.release,
        workflow_id=workflow.id,
    )
    db.add(db_release)
    db.commit()
    db.refresh(db_release)
    return db_release


def get_log(db: Session, run_id: str) -> models.WorkflowLogs:
    return (
        db.query(models.WorkflowLogs)
        .filter(models.WorkflowLogs.run_id == run_id)
        .first()
    )


def create_log(
    db: Session,
    log: schemas.LogCreate,
) -> models.WorkflowLogs:
    db_log = models.WorkflowLogs(
        run_id=log.run_id,
        log=log.log,
        release_id=log.release_id,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def list_logs(
    db: Session,
    skip: int = 0,
    limit: int = 1000,
) -> list[models.WorkflowLogs]:
    return db.query(models.WorkflowLogs).offset(skip).limit(limit).all()


def list_logs_by_release(
    db: Session,
    release_id: datetime,
) -> list[models.WorkflowLogs]:
    return (
        db.query(models.WorkflowLogs)
        .filter(models.WorkflowLogs.release_id == release_id)
        .all()
    )
