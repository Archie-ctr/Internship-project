"""Import every model here so Alembic can discover the complete schema.

Alembic reads `Base.metadata`, not the filesystem. Centralising imports avoids
the subtle migration bug where a valid model is accidentally omitted simply
because nothing imported it before migration generation.
"""

from app.db.session import Base
from app.models.application import Application, ApplicationStatus
from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.notification import Notification
from app.models.payment import Payment
from app.models.role import Role
from app.models.service import Service
from app.models.user import User
from app.models.workflow_task import WorkflowTask

__all__ = [
    "Base",
    "Application",
    "ApplicationStatus",
    "AuditLog",
    "Document",
    "Notification",
    "Payment",
    "Role",
    "Service",
    "User",
    "WorkflowTask",
]
