# Phase 3 — Authentication and authorisation

## Passwords

Registration validates input with Pydantic then hashes the password using bcrypt before it reaches PostgreSQL. A bcrypt hash includes a unique salt and work factor, so the same password produces different stored values. Login calls bcrypt verification; BizReg never decrypts or returns a password.

## Tokens and OAuth2 password flow

`POST /api/v1/auth/token` accepts the standard OAuth2 form fields `username` and `password`; BizReg treats `username` as an email address. A successful login returns a short-lived access JWT and a longer-lived refresh JWT. Tokens are signed with `JWT_SECRET_KEY`, contain an expiry and token type, and expose the user UUID as `sub` rather than the email address.

`GET /api/v1/auth/me` requires `Authorization: Bearer <access-token>`. The server verifies the JWT and then reloads the user and role from the database. This means disabled accounts and changed roles take effect even if an old token still has time remaining.

## RBAC

Use `Depends(require_role("officer", "admin"))` on every officer/admin endpoint added in later phases. The frontend route guard only improves the user experience; it is not trusted for security. The backend dependency is the enforcement point.

## Run and test

Apply Phase 2's migration first, then start the API and frontend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000/register`, create an account using a 12+ character password, and confirm you land at `/dashboard`. You can also use `http://localhost:8000/docs` to call `POST /api/v1/auth/token` and authorize the `/me` endpoint.
