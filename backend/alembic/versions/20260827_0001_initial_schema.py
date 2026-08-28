"""Create BizReg's initial relational schema and reference data.

Revision ID: 20260827_0001
Revises:
Create Date: 2026-08-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260827_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Reference tables precede dependent records so foreign keys are valid from
    # the first deployment. Roles and statuses stay data, not Python constants.
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"])

    op.create_table(
        "application_statuses",
        sa.Column("code", sa.String(length=50), primary_key=True),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
    )

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_services_code", "services", ["code"])

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "applications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("citizen_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("status_code", sa.String(length=50), sa.ForeignKey("application_statuses.code"), nullable=False),
        sa.Column("form_data", sa.JSON(), nullable=False),
        sa.Column("registration_number", sa.String(length=100), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("registration_number"),
    )
    op.create_index("ix_applications_citizen_id", "applications", ["citizen_id"])
    op.create_index("ix_applications_status_code", "applications", ["status_code"])

    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("application_id", sa.Uuid(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("document_type", sa.String(length=80), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_documents_application_id", "documents", ["application_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("application_id", sa.Uuid(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_reference", sa.String(length=150), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="RWF"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("application_id"),
        sa.UniqueConstraint("provider_reference"),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("recipient", sa.String(length=320), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("delivery_status", sa.String(length=30), nullable=False, server_default="queued"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    op.create_table(
        "workflow_tasks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("application_id", sa.Uuid(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("assigned_officer_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("task_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="open"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_workflow_tasks_application_id", "workflow_tasks", ["application_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("application_id", sa.Uuid(), sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("from_state", sa.String(length=50), nullable=True),
        sa.Column("to_state", sa.String(length=50), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_logs_application_id", "audit_logs", ["application_id"])
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])

    # Seed reference data in the same transaction as schema creation. A fresh
    # database is therefore immediately usable and has no hidden manual step.
    op.bulk_insert(
        sa.table("roles", sa.column("id", sa.Integer), sa.column("name", sa.String), sa.column("description", sa.String)),
        [
            {"id": 1, "name": "citizen", "description": "Can create and track their own applications."},
            {"id": 2, "name": "officer", "description": "Can review assigned business-registration applications."},
            {"id": 3, "name": "admin", "description": "Can administer users, services and platform operations."},
        ],
    )
    op.bulk_insert(
        sa.table("application_statuses", sa.column("code", sa.String), sa.column("label", sa.String), sa.column("description", sa.Text)),
        [
            {"code": "submitted", "label": "Submitted", "description": "Citizen submitted an application."},
            {"code": "under_review", "label": "Under review", "description": "Initial completeness review is in progress."},
            {"code": "payment_pending", "label": "Payment pending", "description": "The registration fee is awaiting payment."},
            {"code": "paid", "label": "Paid", "description": "Payment has been confirmed."},
            {"code": "officer_review", "label": "Officer review", "description": "An officer is making the final decision."},
            {"code": "approved", "label": "Approved", "description": "The registration was approved."},
            {"code": "rejected", "label": "Rejected", "description": "The registration was rejected."},
            {"code": "completed", "label": "Completed", "description": "The approved registration and certificate are complete."},
        ],
    )
    op.bulk_insert(
        sa.table("services", sa.column("id", sa.Integer), sa.column("code", sa.String), sa.column("name", sa.String), sa.column("description", sa.Text), sa.column("is_active", sa.Boolean)),
        [{"id": 1, "code": "business-registration", "name": "Business Registration", "description": "Register a new business and receive a digital certificate after approval.", "is_active": True}],
    )


def downgrade() -> None:
    # Reverse dependency order so every foreign key's target still exists when
    # its referencing table is dropped.
    op.drop_index("ix_audit_logs_actor_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_application_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_workflow_tasks_application_id", table_name="workflow_tasks")
    op.drop_table("workflow_tasks")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_table("payments")
    op.drop_index("ix_documents_application_id", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_applications_status_code", table_name="applications")
    op.drop_index("ix_applications_citizen_id", table_name="applications")
    op.drop_table("applications")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_services_code", table_name="services")
    op.drop_table("services")
    op.drop_table("application_statuses")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")
