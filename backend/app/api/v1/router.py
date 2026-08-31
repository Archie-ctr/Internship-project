"""Single composition point for versioned routes.

The exposed API surface is easy to audit here: every feature module is listed
once and tagged for the OpenAPI docs grouping.
"""

from fastapi import APIRouter

from app.api.v1.routes import applications, auth, certificate, documents, health, notifications, officer, payments, services

api_router = APIRouter()
api_router.include_router(health.router,       tags=["health"])
api_router.include_router(auth.router,         tags=["authentication"])
api_router.include_router(services.router,     tags=["services"])
api_router.include_router(applications.router, tags=["applications"])
api_router.include_router(certificate.router,  tags=["certificate"])
api_router.include_router(documents.router,    tags=["documents"])
api_router.include_router(payments.router,     tags=["payments"])
api_router.include_router(notifications.router,tags=["notifications"])
api_router.include_router(officer.router,      tags=["officer"])
