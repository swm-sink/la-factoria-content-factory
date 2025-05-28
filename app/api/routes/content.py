"""
API router for content generation and related endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.core.config.settings import get_settings
from app.services.multi_step_content_generation import EnhancedMultiStepContentGenerationService
from app.main import get_api_key # Re-using the auth dependency from main

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()

# Initialize the service (consider dependency injection for larger apps)
# For now, creating an instance here as it was in main.py
content_service = EnhancedMultiStepContentGenerationService()

# Pydantic models (copied from main.py for now, can be moved to a shared schemas location later)
class ContentRequest(BaseModel):
    syllabus_text: str
    target_format: str = "guide"
    target_duration: Optional[float] = None # Added for podcast length, etc.
    target_pages: Optional[int] = None    # Added for guide length, etc.
    use_parallel: bool = False
    use_cache: bool = True

class ContentResponse(BaseModel):
    title: str
    content: str
    metadata: dict
    quality_metrics: dict = None
    version_id: str = None


@router.post("/generate-content", response_model=ContentResponse, tags=["Content Generation"])
async def generate_content_endpoint(request: ContentRequest, api_key: str = Depends(get_api_key)):
    """Endpoint to generate long-form educational content."""
    try:
        # Note: service.generate_long_form_content might not be async yet.
        # If it's purely CPU-bound or internally handles async I/O, this is okay.
        # If it's I/O-bound and synchronous, it would block the event loop.
        # For true async behavior, the service method itself should be async.
        content, status_code, job_id = content_service.generate_long_form_content(
            request.syllabus_text,
            request.target_format,
            use_parallel=request.use_parallel,
            use_cache=request.use_cache
        )
        if status_code != 200:
            # Assuming error content is in content["error"]
            raise HTTPException(status_code=status_code, detail=content.get("error", "Unknown error during content generation"))
        
        return ContentResponse(
            title=content.get("title", ""),
            content=content.get("content", ""),
            metadata=content.get("metadata", {}),
            quality_metrics=content.get("quality_metrics", {}),
            version_id=content.get("version_id", None)
        )
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.exception("Error generating content via API endpoint")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/health", tags=["Health"])
async def health_check_endpoint():
    """Health check endpoint."""
    return {"status": "ok"} 