"""
Main API router for the AI Content Factory.

This module aggregates all versioned, user-facing API routes.
It is included in `app/main.py` with the `/api/v1` prefix.
Internal or non-versioned routes (like worker endpoints) are handled separately in `app/main.py`.
"""

from fastapi import APIRouter, Depends
from app.main import get_api_key

# Import individual route modules
# from app.api.routes.content import router as content_router # Legacy, consider removing if fully deprecated
from app.api.routes.jobs import router as jobs_router
from app.api.routes.auth import router as auth_router
from app.api.routes.feedback import router as feedback_router

# worker_router is intentionally not included here as it's for internal use.

# Create the main API router instance
# Global API key dependency is removed from here and applied selectively.
api_router = APIRouter()

# Apply API key dependency to specific routers that need protection
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"], dependencies=[Depends(get_api_key)])
api_router.include_router(feedback_router, prefix="/feedback", tags=["Feedback"], dependencies=[Depends(get_api_key)])

# Auth router does NOT get the API key dependency
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include route modules with appropriate prefixes and tags for OpenAPI documentation
# api_router.include_router(content_router, prefix="/content", tags=["Content (Legacy)"]) # If still needed
# Note: The actual path for feedback_router endpoints will be /api/v1/feedback + path_in_feedback_router.
# For example, if feedback.py defines a route for "/content/{content_id}/feedback",
# the full path will be /api/v1/feedback/content/{content_id}/feedback.


@api_router.get("/health", tags=["Health"], dependencies=[Depends(get_api_key)]) # Health check for protected API part
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for the API (protected part).
    Returns the operational status of the API.
    """
    return {"status": "healthy", "message": "API (v1) is up and running."}
