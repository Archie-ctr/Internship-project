# Minimal frontend page layout

Every page uses the root `app/layout.tsx`, which provides the same lightweight shell:

```text
┌──────────────────────────────────────────────────────────┐
│ BizReg                                  Services | Sign in │
│                                             Create account │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                  Page-specific content                   │
│                                                          │
├──────────────────────────────────────────────────────────┤
│             BizReg learning platform · SecureAI Labs     │
└──────────────────────────────────────────────────────────┘
```

## Current page structure

```text
/
├── /                         Landing page
├── /register                 Citizen account creation
├── /login                    OAuth2 password-flow sign-in
├── /dashboard                Protected citizen overview and application list
└── /services
    ├── /                     Protected service catalogue
    └── /business-registration Protected business registration form
```

`SiteHeader` is intentionally just navigation. It does not decide who may access a page; `ProtectedRoute` improves client-side navigation and the FastAPI JWT/RBAC dependencies enforce access on the server.
