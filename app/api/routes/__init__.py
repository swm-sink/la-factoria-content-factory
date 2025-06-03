from fastapi import APIRouter, Depends

from app.api.deps import get_api_key
from app.api.routes.auth import router as auth_router
from app.api.routes.content import router as content_router
from app.api.routes.feedback import router as feedback_router

# Use absolute imports from the app's perspective
from app.api.routes.jobs import router as jobs_router

# Ensure worker_router is not part of the main api_router if it's handled separately
# from app.api.routes.worker import router as worker_router # Typically not included here

api_router = APIRouter()

# Apply API key dependency to specific routers that need protection
api_router.include_router(
    jobs_router, prefix="/jobs", tags=["Jobs"], dependencies=[Depends(get_api_key)]
)
api_router.include_router(
    content_router,
    prefix="/content",
    tags=["Content Generation"],
    dependencies=[Depends(get_api_key)],
)
api_router.include_router(
    feedback_router,
    prefix="/feedback",
    tags=["Feedback"],
    dependencies=[Depends(get_api_key)],
)

# Auth router does NOT get the API key dependency
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])


# Include the health check endpoint
@api_router.get(
    "/health", tags=["Health"], dependencies=[Depends(get_api_key)]
)  # Health check for protected API part
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for the API (protected part).
    Returns the operational status of the API.
    """
    return {"status": "healthy", "message": "API (v1) is up and running."}


# The api_router instance defined here will be imported by app.main
