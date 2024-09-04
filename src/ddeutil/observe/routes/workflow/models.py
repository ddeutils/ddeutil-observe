# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.sql.expression import select
from typing_extensions import Self

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

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        include_release: bool = False,
    ) -> AsyncIterator[Self]:
        stmt = select(cls)
        if include_release:
            stmt = stmt.options(selectinload(cls.releases))
        if skip > 0 and limit > 0:
            stmt = stmt.offset(skip).limit(limit)
        stream = await session.stream(stmt.order_by(cls.id))
        async for row in stream.scalars():
            yield row


class WorkflowReleases(Base):
    __tablename__ = "workflow_releases"

    id = Column(Integer, primary_key=True, index=True)
    release = Column(Integer, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))

    workflow = relationship("Workflows", back_populates="releases")
    logs = relationship("WorkflowLogs", back_populates="release")


class WorkflowLogs(Base):
    __tablename__ = "workflow_logs"

    run_id = Column(String, primary_key=True, index=True)
    context = Column(JSON)
    release_id = Column(Integer, ForeignKey("workflow_releases.id"))

    release = relationship("WorkflowReleases", back_populates="logs")
