# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from .schemas import (
    Notification,
    NotificationMetadata,
    NotificationResponse,
    NotificationUpdate,
)

logger = logging.getLogger("uvicorn.error")


class NotificationService:
    """Service for managing notifications with JSON file storage."""

    def __init__(self, data_file: Optional[Path] = None):
        """Initialize notification service.

        Args:
            data_file: Path to JSON data file. Defaults to static/data/notifications.json
        """
        if data_file is None:
            # Get the project root directory
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent.parent.parent
            data_file = (
                project_root
                / "src"
                / "ddeutil"
                / "observe"
                / "static"
                / "data"
                / "notifications.json"
            )

        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize file if it doesn't exist
        if not self.data_file.exists():
            self._create_initial_data()

    def _create_initial_data(self) -> None:
        """Create initial notification data file."""
        initial_data = {
            "notifications": [],
            "metadata": {
                "total_count": 0,
                "unread_count": 0,
                "last_updated": datetime.now().isoformat(),
            },
        }
        self._save_data(initial_data)

    def _load_data(self) -> dict:
        """Load notification data from JSON file."""
        try:
            with open(self.data_file, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading notification data: {e}")
            self._create_initial_data()
            return self._load_data()

    def _save_data(self, data: dict) -> None:
        """Save notification data to JSON file."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving notification data: {e}")
            raise

    def _update_metadata(self, data: dict) -> None:
        """Update metadata counts."""
        notifications = data.get("notifications", [])
        data["metadata"] = {
            "total_count": len(notifications),
            "unread_count": sum(
                1 for n in notifications if not n.get("is_read", False)
            ),
            "last_updated": datetime.now().isoformat(),
        }

    async def get_notifications(
        self, user_id: str, limit: Optional[int] = None
    ) -> NotificationResponse:
        """Get notifications for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of notifications to return

        Returns:
            NotificationResponse with notifications and metadata
        """
        data = self._load_data()
        notifications = data.get("notifications", [])

        # Filter by user_id
        user_notifications = [
            n for n in notifications if n.get("user_id") == user_id
        ]

        # Sort by timestamp (newest first)
        user_notifications.sort(
            key=lambda x: x.get("timestamp", ""), reverse=True
        )

        # Apply limit if specified
        if limit:
            user_notifications = user_notifications[:limit]

        # Convert to Pydantic models
        notification_objects = [Notification(**n) for n in user_notifications]

        # Get metadata
        metadata = NotificationMetadata(
            total_count=len(
                [n for n in notifications if n.get("user_id") == user_id]
            ),
            unread_count=len(
                [n for n in user_notifications if not n.get("is_read", False)]
            ),
            last_updated=datetime.fromisoformat(
                data.get("metadata", {}).get(
                    "last_updated", datetime.now().isoformat()
                )
            ),
        )

        return NotificationResponse(
            notifications=notification_objects, metadata=metadata.dict()
        )

    async def get_notification(
        self, notification_id: str, user_id: str
    ) -> Optional[Notification]:
        """Get a specific notification.

        Args:
            notification_id: Notification identifier
            user_id: User identifier

        Returns:
            Notification object or None if not found
        """
        data = self._load_data()
        notifications = data.get("notifications", [])

        for notification in notifications:
            if (
                notification.get("id") == notification_id
                and notification.get("user_id") == user_id
            ):
                return Notification(**notification)

        return None

    async def update_notification(
        self,
        notification_id: str,
        user_id: str,
        update_data: NotificationUpdate,
    ) -> Optional[Notification]:
        """Update a notification.

        Args:
            notification_id: Notification identifier
            user_id: User identifier
            update_data: Update data

        Returns:
            Updated notification or None if not found
        """
        data = self._load_data()
        notifications = data.get("notifications", [])

        for _, notification in enumerate(notifications):
            if (
                notification.get("id") == notification_id
                and notification.get("user_id") == user_id
            ):
                # Update fields
                if update_data.is_read is not None:
                    notification["is_read"] = update_data.is_read

                # Update timestamp
                notification["last_modified"] = datetime.now().isoformat()

                # Save changes
                self._update_metadata(data)
                self._save_data(data)

                return Notification(**notification)

        return None

    async def delete_notification(
        self, notification_id: str, user_id: str
    ) -> bool:
        """Delete a notification.

        Args:
            notification_id: Notification identifier
            user_id: User identifier

        Returns:
            True if deleted, False if not found
        """
        data = self._load_data()
        notifications = data.get("notifications", [])

        for i, notification in enumerate(notifications):
            if (
                notification.get("id") == notification_id
                and notification.get("user_id") == user_id
            ):
                notifications.pop(i)
                self._update_metadata(data)
                self._save_data(data)
                return True

        return False

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user.

        Args:
            user_id: User identifier

        Returns:
            Number of notifications marked as read
        """
        data = self._load_data()
        notifications = data.get("notifications", [])

        count = 0
        for notification in notifications:
            if notification.get("user_id") == user_id and not notification.get(
                "is_read", False
            ):
                notification["is_read"] = True
                notification["last_modified"] = datetime.now().isoformat()
                count += 1

        if count > 0:
            self._update_metadata(data)
            self._save_data(data)

        return count

    async def get_unread_count(self, user_id: str) -> int:
        """Get unread notification count for a user.

        Args:
            user_id: User identifier

        Returns:
            Number of unread notifications
        """
        data = self._load_data()
        notifications = data.get("notifications", [])

        return len(
            [
                n
                for n in notifications
                if n.get("user_id") == user_id and not n.get("is_read", False)
            ]
        )
