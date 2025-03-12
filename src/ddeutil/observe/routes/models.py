# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
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
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )


class ScheduleWorkflow(Base):
    __tablename__ = "schedule_workflows"

    id = mapped_column(Integer, primary_key=True, index=True)
    schedule_id = mapped_column(Integer, ForeignKey("schedules.id"))
    alias = mapped_column(String(128), index=True)
    on = mapped_column(String(128), index=True)
    params = mapped_column(String(128), index=True)
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    desc: Mapped[str] = mapped_column(String)
    params: Mapped[dict[str, Any]] = mapped_column(JSON)
    on: Mapped[dict[str, Any]] = mapped_column(JSON)
    jobs: Mapped[dict[str, Any]] = mapped_column(JSON)

    # NOTE: The SCD Columns
    delete_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    valid_start: Mapped[datetime] = mapped_column(DateTime)
    valid_end: Mapped[datetime] = mapped_column(DateTime)
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    audits: Mapped[list[Audit]] = relationship(
        "Audit",
        back_populates="workflow",
    )


class Audit(Base):
    __tablename__ = "audits"

    release_id: Mapped[str] = mapped_column(
        Integer, primary_key=True, index=True
    )
    release: Mapped[datetime] = mapped_column(DateTime)
    data: Mapped[dict] = mapped_column(JSON)
    workflow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workflows.id")
    )
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    workflow: Mapped[Workflow] = relationship(
        "Workflow",
        back_populates="audits",
    )

    logs: Mapped[AuditLog] = relationship(
        "AuditLog",
        back_populates="audit",
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    release_id: int = mapped_column(Integer, ForeignKey("Audit.release_id"))
    workflow_name: str
    release: datetime
    type: str
    context: dict
    parent_run_id: str
    run_id: str
    release_create_date: datetime
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    audit: Mapped[Audit] = relationship(
        "Audit",
        back_populates="logs",
    )

    trace: Mapped[list[Trace]] = relationship(
        "Trace",
        back_populates="audit_log",
    )


class Trace(Base):
    __tablename__ = "traces"

    run_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    audit_log_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("audit_logs.run_id")
    )
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    audit_log: Mapped[AuditLog] = relationship(
        "AuditLog",
        back_populates="trace",
    )

    meta: Mapped[TraceMeta] = relationship("TraceMeta", back_populates="trace")


class TraceMeta(Base):
    __tablename__ = "trace_meta"

    run_id: Mapped[str] = mapped_column(String, ForeignKey("traces.run_id"))
    trace_id: Mapped[int] = mapped_column(String)
    mode: Mapped[str]
    datetime: Mapped[datetime]
    process: Mapped[int]
    thread: Mapped[int]
    message: Mapped[str]
    filename: Mapped[str]
    lineno: Mapped[int]
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    trace: Mapped[Trace] = relationship(
        "Trace",
        back_populates="meta",
    )
