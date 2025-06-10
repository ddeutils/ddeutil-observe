# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    """Base notification schema."""

    id: str = Field(..., description="Unique notification identifier")
    user_id: str = Field(..., description="User identifier")
    type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    workflow_name: Optional[str] = Field(
        None, description="Related workflow name"
    )
    timestamp: datetime = Field(..., description="Notification timestamp")
    is_read: bool = Field(False, description="Read status")
    priority: str = Field("medium", description="Priority level")
    icon: str = Field("bx-bell", description="Icon class")
    color: str = Field("info", description="Color theme")


class Notification(NotificationBase):
    """Complete notification schema."""

    pass


class NotificationUpdate(BaseModel):
    """Schema for updating notification."""

    is_read: Optional[bool] = Field(None, description="Read status")


class NotificationResponse(BaseModel):
    """Response schema for notifications."""

    notifications: list[Notification]
    metadata: dict = Field(default_factory=dict)


class NotificationMetadata(BaseModel):
    """Notification metadata schema."""

    total_count: int = Field(0, description="Total notification count")
    unread_count: int = Field(0, description="Unread notification count")
    last_updated: datetime = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )
