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
    name = Column(String, index=True)
    desc = Column(String)
    params = Column(JSON)
    on = Column(JSON)
    jobs = Column(JSON)
    delete_flag = Column(Boolean, default=False)
    valid_start = Column(DateTime)
    valid_end = Column(DateTime)

    releases = relationship("PipelineReleases", back_populates="pipeline")


class PipelineReleases(Base):
    __tablename__ = "pipeline_releases"

    id = Column(Integer, primary_key=True, index=True)
    release = Column(DateTime, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"))

    pipeline = relationship("Pipelines", back_populates="releases")
    logs = relationship("PipelineLogs", back_populates="release")
