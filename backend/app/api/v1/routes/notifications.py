"""Notification endpoints and background dispatch stub (Day 8).

Architecture:
  1. Any state transition queues a Notification row with delivery_status='queued'.
  2. The background task `dispatch_queued_notifications` runs on a schedule and
     calls the (mock) delivery provider.
  3. This module exposes:
     - GET  /notifications/me      — citizen's own notification history
     - POST /notifications/dispatch — admin-triggered manual flush (test helper)

The mock delivery provider logs the notification to stdout and marks it
'delivered'. A real provider (SendGrid, Africa's Talking) replaces only the
`_mock_deliver` function.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.notification import Notification
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications")


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    channel: str
    recipient: str
    subject: str
    body: str
    delivery_status: str
    created_at: datetime


# ── Mock delivery provider ────────────────────────────────────────────────────

def _mock_deliver(notification: Notification) -> bool:
    """Simulate sending an email/SMS by logging it.

    Returns True on simulated success. Replace with a real provider call
    (e.g. requests.post to SendGrid) without changing the calling code.
    """
    logger.info(
        "[MOCK %s] To: %s | Subject: %s",
        notification.channel.upper(),
        notification.recipient,
        notification.subject,
    )
    return True


# ── Background task ───────────────────────────────────────────────────────────

def dispatch_queued_notifications(db: Session) -> int:
    """Process all queued notifications; return the count dispatched.

    Called from the background task endpoint and can also be invoked directly
    by a scheduler (e.g., APScheduler or Celery beat) added in a later phase.
    """
    queued = db.scalars(
        select(Notification).where(Notification.delivery_status == "queued")
    ).all()

    dispatched = 0
    for notification in queued:
        try:
            success = _mock_deliver(notification)
            notification.delivery_status = "delivered" if success else "failed"
            dispatched += 1
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to deliver notification %s: %s", notification.id, exc)
            notification.delivery_status = "failed"

    db.commit()
    return dispatched


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=list[NotificationResponse])
def list_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationResponse]:
    """Return the notification history for the authenticated user."""
    notifications = db.scalars(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    ).all()
    return [
        NotificationResponse(
            id=str(n.id),
            channel=n.channel,
            recipient=n.recipient,
            subject=n.subject,
            body=n.body,
            delivery_status=n.delivery_status,
            created_at=n.created_at,
        )
        for n in notifications
    ]


@router.post("/dispatch", status_code=202)
def trigger_dispatch(
    background_tasks: BackgroundTasks,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> dict:
    """Admin endpoint: flush all queued notifications in a background task.

    The 202 Accepted response returns immediately; the delivery runs
    asynchronously so the HTTP response is not held open.
    """
    background_tasks.add_task(dispatch_queued_notifications, db)
    return {"message": "Notification dispatch queued", "status": "accepted"}
