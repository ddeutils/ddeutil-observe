# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from ...auth.deps import required_current_active_user
from ...deps import get_templates
from ..notifications.service import NotificationService

profile = APIRouter(
    prefix="/profile",
    tags=["profile"],
    dependencies=[Depends(required_current_active_user)],
)


@profile.get("/", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    templates=Depends(get_templates),
):
    """Display the user profile page with notifications."""
    # For now, use hardcoded user data like other routes do
    # TODO: Get actual user from session/auth context
    user_id = "observe"

    # Create a mock user object for template rendering
    from types import SimpleNamespace

    # Mock created date (30 days ago for example)
    mock_created_at = datetime.now().replace(
        day=1
    )  # First day of current month
    days_active = (datetime.now() - mock_created_at).days

    mock_user = SimpleNamespace(
        id=1,
        username="observe",
        email="observe@example.com",
        profile_image_url="/static/img/profile.svg",
        is_active=True,
        role=SimpleNamespace(name="admin"),
        created_at=mock_created_at,
        days_active=days_active,
        last_login=SimpleNamespace(strftime=lambda fmt: "10:30"),
    )

    # Get user notifications for the profile page
    notification_service = NotificationService()
    response = await notification_service.get_notifications(
        user_id=user_id, limit=10
    )
    notifications = response.notifications
    notification_metadata = response.metadata

    return templates.TemplateResponse(
        "profile/profile.html",
        {
            "request": request,
            "user": mock_user,
            "notifications": notifications,
            "notification_metadata": notification_metadata,
        },
    )


@profile.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    templates=Depends(get_templates),
):
    """Display the user settings page."""
    # Create a mock user object for template rendering
    from types import SimpleNamespace

    # Mock created date (30 days ago for example)
    mock_created_at = datetime.now().replace(
        day=1
    )  # First day of current month
    days_active = (datetime.now() - mock_created_at).days

    mock_user = SimpleNamespace(
        id=1,
        username="observe",
        email="observe@example.com",
        profile_image_url="/static/img/profile.svg",
        is_active=True,
        role=SimpleNamespace(name="admin"),
        created_at=mock_created_at,
        days_active=days_active,
        last_login=SimpleNamespace(strftime=lambda fmt: "10:30"),
    )

    return templates.TemplateResponse(
        "profile/settings.html",
        {
            "request": request,
            "user": mock_user,
        },
    )
