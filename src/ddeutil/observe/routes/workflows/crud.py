from sqlalchemy.orm import Session

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
        .filter(models.Pipelines.email == name)
        .first()
    )


def create_pipeline(db: Session, pipeline: schemas.PipelineCreate):
    db_pipeline = models.Pipelines(email=pipeline.name, desc="dummy create")
    db.add(db_pipeline)
    db.commit()
    db.refresh(db_pipeline)
    return db_pipeline
