"""
AirLynk — Notification Endpoints.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.notification.repository.notification_repository import NotificationRepository
from backend.services.notification.schemas.notification import NotificationResponse
from backend.shared.database.session import get_db_session as get_db
from backend.shared.middleware.rbac import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
async def get_notification_history(
    current_user: dict[str, Any] = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retrieve notification history for the authenticated user."""
    repo = NotificationRepository(db)
    user_id = uuid.UUID(current_user["sub"])
    notifications = await repo.list_notifications_for_user(user_id, limit=limit, offset=offset)
    return notifications


@router.get("/unread-count")
async def get_unread_count(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """Get the count of unread notifications for the authenticated user."""
    repo = NotificationRepository(db)
    user_id = uuid.UUID(current_user["sub"])
    count = await repo.get_unread_count(user_id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Mark a specific notification as read."""
    repo = NotificationRepository(db)
    user_id = uuid.UUID(current_user["sub"])

    notification = await repo.mark_as_read(notification_id, user_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification
