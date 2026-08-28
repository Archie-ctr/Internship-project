# Phase 4 — Service catalogue and application form

## Catalogue first

`GET /api/v1/services` returns active public services from the database. The browser does not hard-code the service catalogue, so adding a future public service is a data/API change rather than a redesign of the portal.

## Form validation has two layers

The Next.js form uses browser constraints such as `required` and `minLength` for fast feedback. Those constraints are never a security boundary: a caller can bypass the browser entirely. FastAPI validates the JSON body again through `CreateBusinessRegistrationRequest`, including permitted business-type values and sensible length/pattern limits.

## Safe application creation

Only a `citizen` can call `POST /api/v1/applications`. The server looks up the active `business-registration` service itself and sets `status_code` to `submitted`; neither value comes from the client. It writes the application and `application_created` AuditLog entry in one transaction. `GET /applications/me` and `GET /applications/{id}` derive ownership from the JWT, never a user ID supplied by the client.

## Try it

After completing Phase 2 and Phase 3 setup, restart the API and frontend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn app.main:app --reload
```

```powershell
cd frontend
npm run dev
```

1. Sign in as a citizen at `http://localhost:3000/login`.
2. Open **Start a business registration** on the dashboard.
3. Submit the form and confirm the dashboard shows it with `submitted` status.
4. Inspect the API contract at `http://localhost:8000/docs`.
