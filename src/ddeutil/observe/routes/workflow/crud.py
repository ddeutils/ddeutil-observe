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


def get_workflow(db: Session, workflow_id: int):
    return (
        db.query(models.Workflows)
        .filter(models.Workflows.id == workflow_id)
        .first()
    )


def get_workflow_by_name(db: Session, name: str):
    return (
        db.query(models.Workflows)
        .filter(
            models.Workflows.name == name,
            models.Workflows.delete_flag == false(),
        )
        .first()
    )


def create_workflow(
    db: Session, workflow: schemas.WorkflowCreate
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


def list_workflows(db: Session, skip: int = 0, limit: int = 1000):
    return (
        db.query(models.Workflows)
        .filter(models.Workflows.delete_flag == false())
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_workflow(db: Session, search_text: str):
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
