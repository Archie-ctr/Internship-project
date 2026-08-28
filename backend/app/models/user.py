import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Uuid

from app.db.session import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.audit_log import AuditLog
    from app.models.notification import Notification
    from app.models.role import Role
    from app.models.workflow_task import WorkflowTask


class User(TimestampMixin, Base):
    """A platform account. Passwords are stored only as hashes in Phase 3."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    role: Mapped["Role"] = relationship(back_populates="users")
    applications: Mapped[list["Application"]] = relationship(back_populates="citizen")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    assigned_tasks: Mapped[list["WorkflowTask"]] = relationship(back_populates="assigned_officer")
    audit_events: Mapped[list["AuditLog"]] = relationship(back_populates="actor")
