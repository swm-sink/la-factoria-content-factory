"""
Main API router that aggregates all route modules.

This module serves as the central point for including all API routes
and applying common middleware or dependencies.
"""

from fastapi import APIRouter

from app.api.routes.content import router as content_router
from app.api.routes.jobs import router as jobs_router

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(content_router)
api_router.include_router(jobs_router)

# Add other routers here in the future, e.g.:
# from .jobs import router as jobs_router
# api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"]) 