# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from . import models, schemas


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
