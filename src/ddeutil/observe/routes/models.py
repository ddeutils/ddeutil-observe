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


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    desc: Mapped[str] = mapped_column(String, nullable=True)
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
    logs: Mapped[list[WorkflowLog]] = relationship(
        "WorkflowLog",
        back_populates="workflow",
    )


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    release_id: Mapped[str] = mapped_column(
        String,
        index=True,
    )
    workflow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflows.id"),
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        index=True,
    )  # pending, running, success, failed, cancelled
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    execution_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)  # in seconds
    error_message: Mapped[str] = mapped_column(String, nullable=True)
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
    workflow_logs: Mapped[list[WorkflowLog]] = relationship(
        "WorkflowLog",
        back_populates="audit",
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        index=True,
    )
    audit_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("audits.id"),
    )
    workflow_name: Mapped[str]
    release: Mapped[datetime]
    type: Mapped[str]
    context: Mapped[dict] = mapped_column(JSON)
    parent_run_id: Mapped[str] = mapped_column(String, nullable=True)
    run_id: Mapped[str]
    release_create_date: Mapped[datetime]
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    audit: Mapped[Audit] = relationship(
        "Audit",
        back_populates="logs",
    )

    trace: Mapped[Trace] = relationship(
        "Trace",
        back_populates="audit_log",
    )


class Trace(Base):
    __tablename__ = "traces"

    run_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("audit_logs.id"),
        primary_key=True,
        index=True,
    )
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    audit_log: Mapped[Trace] = relationship(
        "AuditLog",
        back_populates="trace",
    )

    meta: Mapped[list[TraceMeta]] = relationship(
        "TraceMeta",
        back_populates="trace",
        uselist=True,
    )


class TraceMeta(Base):
    __tablename__ = "trace_meta"

    run_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("traces.run_id"),
        primary_key=True,
        index=True,
    )
    trace_id: Mapped[int] = mapped_column(String, primary_key=True, index=True)
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


class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflows.id"),
        index=True,
    )
    audit_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("audits.id"),
        index=True,
    )
    level: Mapped[str] = mapped_column(
        String(10)
    )  # INFO, WARNING, ERROR, DEBUG
    message: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    stage: Mapped[str] = mapped_column(String, nullable=True)
    context: Mapped[dict] = mapped_column(JSON, nullable=True)
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    workflow: Mapped[Workflow] = relationship(
        "Workflow",
        back_populates="logs",
    )
    audit: Mapped[Audit] = relationship(
        "Audit",
        back_populates="workflow_logs",
    )
