# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.sql.expression import select
from sqlalchemy.types import (
    JSON,
    Boolean,
    DateTime,
    Integer,
    String,
)
from typing_extensions import Self

from ...auth.models import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String(128), index=True)
    desc = mapped_column(String)
    params: Mapped[dict[str, Any]] = mapped_column(JSON)
    on: Mapped[dict[str, Any]] = mapped_column(JSON)
    jobs: Mapped[dict[str, Any]] = mapped_column(JSON)
    delete_flag = mapped_column(Boolean, default=False)
    valid_start = mapped_column(DateTime)
    valid_end = mapped_column(DateTime)

    releases: Mapped[list[WorkflowRelease]] = relationship(
        "WorkflowRelease",
        back_populates="workflow",
    )

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

        async for row in (
            (await session.stream(stmt.order_by(cls.id))).scalars().all()
        ):
            yield row


class WorkflowRelease(Base):
    __tablename__ = "workflow_releases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    release: Mapped[int] = mapped_column(Integer, index=True)
    workflow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflows.id")
    )

    workflow: Mapped[Workflow] = relationship(
        "Workflow", back_populates="releases"
    )
    logs: Mapped[list[WorkflowLog]] = relationship(
        "WorkflowLog",
        back_populates="release",
    )


class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    run_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    context: Mapped[dict] = mapped_column(JSON)
    release_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflow_releases.id")
    )

    release: Mapped[WorkflowRelease] = relationship(
        "WorkflowRelease",
        back_populates="logs",
    )
