# API reference — implemented endpoints

Base URL: `http://localhost:8000/api/v1`

Interactive OpenAPI documentation: `http://localhost:8000/docs`

## Public endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness check |
| GET | `/services` | List active public services |
| POST | `/auth/register` | Register a citizen and return token pair |
| POST | `/auth/token` | OAuth2 password-flow login |
| POST | `/auth/refresh` | Exchange a refresh JWT for a new token pair |

`POST /auth/register` body:

```json
{
  "full_name": "Aline Mukamana",
  "email": "aline@example.com",
  "password": "at-least-twelve-characters"
}
```

`POST /auth/token` uses `application/x-www-form-urlencoded`:

```text
username=aline@example.com&password=at-least-twelve-characters
```

Both successful registration and login return:

```json
{
  "access_token": "<signed JWT>",
  "refresh_token": "<signed JWT>",
  "token_type": "bearer"
}
```

## Citizen-protected endpoints

All endpoints below require `Authorization: Bearer <access_token>` and a database role of `citizen`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/auth/me` | Read the authenticated user's safe profile fields |
| POST | `/applications` | Submit a Business Registration application |
| GET | `/applications/me` | List the current citizen's applications |
| GET | `/applications/{application_id}` | Read one application owned by the current citizen |

`POST /applications` body:

```json
{
  "business_name": "Kigali Coffee Works",
  "business_type": "sole_proprietorship",
  "owner": {
    "full_name": "Aline Mukamana",
    "id_number": "1199980012345678",
    "phone_number": "+250788123456"
  },
  "address": {
    "line1": "KN 1 Avenue",
    "city": "Kigali",
    "district": "Gasabo",
    "country": "Rwanda"
  }
}
```

The API ignores any attempted client-provided status, citizen ID, or service ID because these values are resolved securely on the server.

## Expected HTTP responses

| Status | Meaning |
| --- | --- |
| `200` | Successful read/login/refresh |
| `201` | Account or application created |
| `401` | Missing, expired, malformed, or wrong-type bearer token |
| `403` | Authenticated but lacking the required role |
| `404` | Application does not exist or does not belong to current citizen |
| `409` | Duplicate email registration |
| `422` | Schema validation rejected input |
| `503` | Seeded Business Registration service is unavailable |
