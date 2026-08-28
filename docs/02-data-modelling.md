# Phase 2 — Database and data modelling

## Why relational models?

PostgreSQL is the system of record for BizReg. Foreign keys make invalid relationships impossible at the database level: an application must belong to a real citizen, service and status; a document must belong to a real application. The ORM gives Python code an expressive interface while still producing parameterised SQL.

The `Application` table stores the relationships that the platform must query and protect as normal columns. The business form itself is `form_data` JSON because its precise fields arrive in Phase 4 and may grow over time. This is a practical hybrid: relational integrity for the workflow, flexible data for service-specific forms.

`ApplicationStatus` is a seeded reference table containing every valid workflow label. It does not decide which transition is legal; Phase 6 will do that in a dedicated state-machine module. `AuditLog` is append-only evidence of each action and transition, while `WorkflowTask` represents work assigned to officers.

## Migrations and seed data

Alembic records each schema change in the `alembic_version` table. The first migration creates all ten domain tables and seeds these stable reference records in the same database transaction:

- Roles: `citizen`, `officer`, `admin`
- Service: `business-registration`
- Workflow status labels: from `submitted` to `completed`

This makes a new database usable immediately and avoids undocumented, manual SQL setup.

## Apply and inspect the migration

Start Docker Desktop first, then from the repository root:

```powershell
docker compose up -d
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

Check the migration version and seeded data:

```powershell
alembic current
docker compose exec postgres psql -U bizreg -d bizreg -c "SELECT id, name FROM roles;"
docker compose exec postgres psql -U bizreg -d bizreg -c "SELECT code, name FROM services;"
```

To study the generated schema, open `alembic/versions/20260827_0001_initial_schema.py`. Do not run `alembic downgrade base` against data you want to keep: it drops all Phase 2 tables.
