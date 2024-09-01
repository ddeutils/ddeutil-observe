# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from ...db import Base


class WorkflowLogs(Base):
    __tablename__ = "workflow_logs"

    run_id = Column(String, primary_key=True, index=True)
    log = Column(JSON)
    release_id = Column(DateTime, ForeignKey("workflow_releases.id"))

    release = relationship("WorkflowReleases", back_populates="logs")
