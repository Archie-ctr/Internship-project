import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Uuid

from app.db.session import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User


class WorkflowTask(TimestampMixin, Base):
    """An officer work item, created by the explicit workflow engine in Phase 6."""

    __tablename__ = "workflow_tasks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id"), nullable=False, index=True)
    assigned_officer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    task_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")
    notes: Mapped[str | None] = mapped_column(Text)

    application: Mapped["Application"] = relationship(back_populates="tasks")
    assigned_officer: Mapped["User | None"] = relationship(back_populates="assigned_tasks")
