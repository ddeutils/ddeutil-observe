# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import (
    JSON,
    Boolean,
    DateTime,
    Integer,
    String,
)

from ..auth.models import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String(128), index=True)


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    desc: Mapped[str] = mapped_column(String)
    params: Mapped[dict[str, Any]] = mapped_column(JSON)
    on: Mapped[dict[str, Any]] = mapped_column(JSON)
    jobs: Mapped[dict[str, Any]] = mapped_column(JSON)
    delete_flag = mapped_column(Boolean, default=False)
    valid_start = mapped_column(DateTime)
    valid_end = mapped_column(DateTime)

    audits: Mapped[list[Audit]] = relationship(
        "Audit",
        back_populates="workflow",
    )

    # @classmethod
    # async def get_all(
    #     cls,
    #     session: AsyncSession,
    #     skip: int = 0,
    #     limit: int = 100,
    #     include_release: bool = False,
    # ) -> AsyncIterator[Self]:
    #     stmt = select(cls)
    #     if include_release:
    #         stmt = stmt.options(selectinload(cls.audits))
    #     if skip > 0 and limit > 0:
    #         stmt = stmt.offset(skip).limit(limit)
    #     for row in (
    #         await (await session.stream(stmt.order_by(cls.id))).scalars().all()
    #     ):
    #         yield row


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    release: Mapped[int] = mapped_column(Integer, index=True)
    data: Mapped[dict] = mapped_column(JSON)
    workflow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflows.id")
    )

    workflow: Mapped[Workflow] = relationship(
        "Workflow", back_populates="audits"
    )
    traces: Mapped[list[Trace]] = relationship(
        "Trace",
        back_populates="audit",
    )


class Trace(Base):
    __tablename__ = "traces"

    run_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    context: Mapped[dict] = mapped_column(JSON)
    audit_id: Mapped[int] = mapped_column(Integer, ForeignKey("audits.id"))

    audit: Mapped[Audit] = relationship(
        "Audit",
        back_populates="traces",
    )
