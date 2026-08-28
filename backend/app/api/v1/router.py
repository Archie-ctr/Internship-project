"""Single composition point for versioned routes.

Feature routers (auth, applications, officer review) join here in later phases,
which makes the exposed API surface easy to audit.
"""

from fastapi import APIRouter

from app.api.v1.routes import applications, auth, health, services

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(services.router, tags=["services"])
api_router.include_router(applications.router, tags=["applications"])
