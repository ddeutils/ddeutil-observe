# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from ...db import Base


class Pipelines(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    desc = Column(String, index=False)
    jobs = Column(JSON, index=False)

    releases = relationship("PipelineReleases", back_populates="pipeline")
    logs = relationship("PipelineLogs", back_populates="pipeline")


class PipelineReleases(Base):
    __tablename__ = "pipeline_releases"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)
    release = Column(DateTime, index=False)
    delete_flag = Column(Boolean, index=False)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"))

    pipeline = relationship("Pipelines", back_populates="releases")
