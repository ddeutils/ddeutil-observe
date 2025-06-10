# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as st

from .schemas import Notification, NotificationResponse, NotificationUpdate
from .service import NotificationService

notification = APIRouter(
    prefix="/notifications",
    tags=["api", "notifications"],
    responses={st.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def get_notification_service() -> NotificationService:
    """Dependency to get notification service."""
    return NotificationService()


@notification.get("/", response_model=NotificationResponse)
async def api_get_notifications(
    user_id: str = "observe",
    limit: int = 50,
    service: NotificationService = Depends(get_notification_service),
):
    """Get notifications for a user."""
    return await service.get_notifications(user_id=user_id, limit=limit)


@notification.get("/count")
async def api_get_unread_count(
    user_id: str = "observe",
    service: NotificationService = Depends(get_notification_service),
):
    """Get unread notification count."""
    count = await service.get_unread_count(user_id=user_id)
    return {"unread_count": count}


@notification.get("/{notification_id}", response_model=Notification)
async def api_get_notification(
    notification_id: str,
    user_id: str = "observe",
    service: NotificationService = Depends(get_notification_service),
):
    """Get a specific notification."""
    notification_obj = await service.get_notification(notification_id, user_id)
    if not notification_obj:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    return notification_obj


@notification.patch("/{notification_id}", response_model=Notification)
async def api_update_notification(
    notification_id: str,
    update_data: NotificationUpdate,
    user_id: str = "observe",
    service: NotificationService = Depends(get_notification_service),
):
    """Update a notification."""
    notification_obj = await service.update_notification(
        notification_id, user_id, update_data
    )
    if not notification_obj:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    return notification_obj


@notification.delete("/{notification_id}")
async def api_delete_notification(
    notification_id: str,
    user_id: str = "observe",
    service: NotificationService = Depends(get_notification_service),
):
    """Delete a notification."""
    success = await service.delete_notification(notification_id, user_id)
    if not success:
        raise HTTPException(
            status_code=st.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    return {"message": "Notification deleted successfully"}


@notification.post("/mark-all-read")
async def api_mark_all_as_read(
    user_id: str = "observe",
    service: NotificationService = Depends(get_notification_service),
):
    """Mark all notifications as read."""
    count = await service.mark_all_as_read(user_id)
    return {"message": f"Marked {count} notifications as read"}
