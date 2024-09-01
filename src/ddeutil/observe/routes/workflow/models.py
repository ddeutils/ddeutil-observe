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


class Workflows(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    desc = Column(String)
    params = Column(JSON)
    on = Column(JSON)
    jobs = Column(JSON)
    delete_flag = Column(Boolean, default=False)
    valid_start = Column(DateTime)
    valid_end = Column(DateTime)

    releases = relationship("WorkflowReleases", back_populates="workflow")


class WorkflowReleases(Base):
    __tablename__ = "workflow_releases"

    id = Column(Integer, primary_key=True, index=True)
    release = Column(DateTime, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))

    workflow = relationship("Workflows", back_populates="releases")
    logs = relationship("WorkflowLogs", back_populates="release")
