# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from ...db import Base


class PipelineLogs(Base):
    __tablename__ = "pipeline_logs"

    run_id = Column(String, primary_key=True, index=True)
    log = Column(JSON)
    release_id = Column(DateTime, ForeignKey("pipeline_releases.id"))

    release = relationship("PipelineReleases", back_populates="logs")
