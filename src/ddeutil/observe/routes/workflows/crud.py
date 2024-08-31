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


def get_pipeline(db: Session, pipeline_id: int):
    return (
        db.query(models.Pipelines)
        .filter(models.Pipelines.id == pipeline_id)
        .first()
    )


def get_pipeline_by_name(db: Session, name: str):
    return (
        db.query(models.Pipelines)
        .filter(
            models.Pipelines.name == name,
            models.Pipelines.delete_flag == false(),
        )
        .first()
    )


def create_pipeline(
    db: Session, pipeline: schemas.PipelineCreate
) -> models.Pipelines:
    db_pipeline = models.Pipelines(
        name=pipeline.name,
        desc=pipeline.desc,
        params=pipeline.params,
        on=pipeline.on,
        jobs=pipeline.jobs,
        valid_start=datetime.now(),
        valid_end=datetime(2999, 12, 31),
    )
    db.add(db_pipeline)
    db.commit()
    db.refresh(db_pipeline)
    return db_pipeline


def list_pipelines(db: Session, skip: int = 0, limit: int = 1000):
    return (
        db.query(models.Pipelines)
        .filter(models.Pipelines.delete_flag == false())
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_pipeline(db: Session, search_text: str):
    if len(search_text) > 1:
        if not (search_text := search_text.strip().lower()):
            return []

        results = []
        for pipeline in list_pipelines(db=db):
            text: str = f"{pipeline.name} {pipeline.desc or ''}".lower()
            if search_text in text:
                results.append(pipeline)
        return results
    return list_pipelines(db=db)
