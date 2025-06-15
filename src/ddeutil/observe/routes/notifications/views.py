# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, Request
from fastapi.templating import Jinja2Templates

from ...auth.deps import required_current_active_user
from ...deps import get_templates
from .service import NotificationService

logger = logging.getLogger("uvicorn.error")

# NOTE: This route require authentication step first.
notification = APIRouter(
    prefix="/notifications",
    tags=["notifications", "frontend"],
    dependencies=[Depends(required_current_active_user)],
)


def get_notification_service() -> NotificationService:
    """Dependency to get notification service."""
    return NotificationService()


@notification.get("/")
async def notification_page(
    request: Request,
    service: NotificationService = Depends(get_notification_service),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Render notifications page."""
    user_id = "observe"  # Get from auth context in real implementation
    notifications_data = await service.get_notifications(
        user_id=user_id, limit=50
    )

    return templates.TemplateResponse(
        request=request,
        name="notifications/notifications.html",
        context={
            "notifications": notifications_data.notifications,
            "metadata": notifications_data.metadata,
        },
    )


@notification.get("/dropdown")
async def notification_dropdown(
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    service: NotificationService = Depends(get_notification_service),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Render notification dropdown content."""
    user_id = "observe"  # Get from auth context in real implementation
    notifications_data = await service.get_notifications(
        user_id=user_id, limit=10
    )

    if hx_request:
        return templates.TemplateResponse(
            request=request,
            name="notifications/partials/notification-dropdown.html",
            context={
                "notifications": notifications_data.notifications,
                "metadata": notifications_data.metadata,
            },
        )

    # Redirect to full page if not HTMX request
    return await notification_page(request, service, templates)


@notification.post("/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: str,
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    service: NotificationService = Depends(get_notification_service),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Mark a notification as read."""
    user_id = "observe"  # Get from auth context in real implementation

    from .schemas import NotificationUpdate

    await service.update_notification(
        notification_id=notification_id,
        user_id=user_id,
        update_data=NotificationUpdate(is_read=True),
    )

    if hx_request:
        # Return updated dropdown
        return await notification_dropdown(
            request, hx_request, service, templates
        )

    # Return JSON response for API
    return {"success": True, "message": "Notification marked as read"}


@notification.post("/{notification_id}/mark-unread")
async def mark_notification_unread(
    notification_id: str,
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    service: NotificationService = Depends(get_notification_service),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Mark a notification as unread."""
    user_id = "observe"  # Get from auth context in real implementation

    from .schemas import NotificationUpdate

    await service.update_notification(
        notification_id=notification_id,
        user_id=user_id,
        update_data=NotificationUpdate(is_read=False),
    )

    if hx_request:
        # Return updated dropdown
        return await notification_dropdown(
            request, hx_request, service, templates
        )

    # Return JSON response for API
    return {"success": True, "message": "Notification marked as unread"}


@notification.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    service: NotificationService = Depends(get_notification_service),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Delete a notification."""
    user_id = "observe"  # Get from auth context in real implementation

    success = await service.delete_notification(notification_id, user_id)

    if hx_request and success:
        # Return updated dropdown
        return await notification_dropdown(
            request, hx_request, service, templates
        )

    # Return JSON response for API
    return {
        "success": success,
        "message": (
            "Notification deleted" if success else "Notification not found"
        ),
    }


@notification.post("/mark-all-read")
async def mark_all_notifications_read(
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    service: NotificationService = Depends(get_notification_service),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Mark all notifications as read."""
    user_id = "observe"  # Get from auth context in real implementation

    count = await service.mark_all_as_read(user_id)

    if hx_request:
        # Return updated dropdown
        return await notification_dropdown(
            request, hx_request, service, templates
        )

    # Return JSON response for API
    return {"success": True, "message": f"Marked {count} notifications as read"}


@notification.get("/list")
async def notification_list_partial(
    request: Request,
    service: NotificationService = Depends(get_notification_service),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Render partial notifications list for auto-refresh."""
    user_id = "observe"  # Get from auth context in real implementation
    notifications_data = await service.get_notifications(
        user_id=user_id, limit=50
    )

    return templates.TemplateResponse(
        request=request,
        name="notifications/partials/notifications-list.html",
        context={
            "notifications": notifications_data.notifications,
            "metadata": notifications_data.metadata,
        },
    )


@notification.get("/count")
async def get_notification_count(
    service: NotificationService = Depends(get_notification_service),
):
    """Get unread notification count."""
    user_id = "observe"  # Get from auth context in real implementation
    count = await service.get_unread_count(user_id)
    return {"unread_count": count}
