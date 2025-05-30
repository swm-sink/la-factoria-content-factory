"""
API router for synchronous content generation, intended for internal worker use,
and a health check endpoint.

Note: These routes might be inactive if this router is not explicitly included
in the main application setup in `app/main.py`. The `/api/v1/jobs` endpoint
is the primary user-facing way to initiate content generation.
The health check here might be redundant if one is provided by the main `api_router`.
"""

from fastapi import Request  # Added Request
import logging
from fastapi import APIRouter, Depends, HTTPException, status

# from pydantic import BaseModel # No longer defining models locally
# from typing import Optional # Already imported by models below

from app.core.config.settings import get_settings
from app.services.multi_step_content_generation import (
    EnhancedMultiStepContentGenerationService,
)

# from app.main import get_api_key # Unused import
from app.models.pydantic.content import (
    ContentRequest,
    ContentResponse,
)  # Import shared models
from app.models.pydantic.job import (
    Job,
)  # Assuming Job model might be needed for job_id if API-2.6 returns it


# Placeholder for OIDC token verifier dependency
async def verify_oidc_token_for_cloud_task(
    request: Request,
) -> bool:  # Added return type
    """Placeholder: Verifies OIDC token from Cloud Tasks.
    In a real implementation, this would:
    1. Extract the Authorization: Bearer token (OIDC token).
    2. Verify it against Google's public keys.
    3. Check claims like 'aud' (audience) and 'iss' (issuer).
    4. Ensure the 'email' claim matches the expected Cloud Task invoker service account.
    If verification fails, raise HTTPException(status_code=401/403).
    """
    # Simulating token verification for now
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # This check is very basic. Real OIDC validation is much more involved.
        # logger.warning("Missing or malformed OIDC token for internal worker endpoint.")
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid OIDC token for worker")
        pass  # For MVP, allow passthrough if no token, but log a warning
    logger.info("Placeholder OIDC token verifier called.")
    return (
        True  # Assume valid for now if present, or proceed if not strictly enforced yet
    )


logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(
    prefix="/api/v1",  # Consistent prefix from project rules
    tags=["Content Generation"],  # Tag for this router
)

# Initialize the service
# TODO: Consider using FastAPI's Depends for service injection for better testability and management.
content_service = EnhancedMultiStepContentGenerationService()

# Removed local Pydantic model definitions for ContentRequest and ContentResponse
# They are now imported from app.models.pydantic.content


@router.post(
    "/generate-content",
    response_model=ContentResponse,
    summary="Generate Content (Internal Worker Endpoint)",
)
async def generate_content_endpoint(
    request: ContentRequest,
    _worker_auth: bool = Depends(verify_oidc_token_for_cloud_task),
):
    """
    Internal synchronous endpoint to generate long-form educational content.
    This endpoint is intended to be called by a Cloud Task worker as part of an asynchronous job (API-2.5).
    It directly calls the content generation service.
    Clients should typically use the `/api/v1/jobs` endpoint to initiate content generation.
    """
    logger.info(
        f"Internal /generate-content endpoint called with format: {request.target_format}"
    )
    try:
        # The service method returns: (content_dict, status_code, job_id_or_None)
        # For this internal worker, job_id might be passed in via request or known context if needed.
        # Assuming it might return a job_id if one was associated with this specific call.
        generated_data_dict, status_code, job_id_from_service = (
            content_service.generate_long_form_content(
                syllabus_text=request.syllabus_text,
                target_format=request.target_format,
                target_duration=request.target_duration,
                target_pages=request.target_pages,
                use_parallel=request.use_parallel,
                use_cache=request.use_cache,
            )
        )

        if status_code != 200:
            error_detail = generated_data_dict.get(
                "error", "Unknown error during content generation by service."
            )
            logger.error(
                f"Content generation service returned error {status_code}: {error_detail}"
            )
            raise HTTPException(status_code=status_code, detail=error_detail)

        # Map the dictionary from the service to the ContentResponse Pydantic model
        # The GeneratedContent base class in ContentResponse expects specific keys.
        # Ensure generated_data_dict from the service aligns with these fields.
        response_data = ContentResponse(
            title=generated_data_dict.get("title", "Untitled Content"),
            content=generated_data_dict.get(
                "content", ""
            ),  # Main content for the target_format
            content_outline=generated_data_dict.get("content_outline"),
            podcast_script=generated_data_dict.get("podcast_script"),
            study_guide=generated_data_dict.get("study_guide"),
            one_pager_summary=generated_data_dict.get("one_pager_summary"),
            detailed_reading_material=generated_data_dict.get(
                "detailed_reading_material"
            ),
            faqs=generated_data_dict.get("faqs", []),
            flashcards=generated_data_dict.get("flashcards", []),
            reading_guide_questions=generated_data_dict.get(
                "reading_guide_questions", []
            ),
            metadata=generated_data_dict.get(
                "metadata", {}
            ),  # This should map to ContentMetadata model
            quality_metrics=generated_data_dict.get(
                "quality_metrics"
            ),  # This to QualityMetrics
            version_id=generated_data_dict.get("version_id"),
            job_id=job_id_from_service,  # If service provides it for this sync call
            status="completed",  # For a direct successful response
        )
        return response_data

    except HTTPException:  # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.exception(
            f"Unhandled error in /generate-content endpoint: {e}"
        )  # Log full details internally
        # Return a generic error message to the client for 5xx errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal server error occurred.",
        )


@router.get("/health", tags=["Health"], summary="Application Health Check")
async def health_check_endpoint():
    """Provides a basic health check for the application."""
    logger.info("Health check endpoint called.")
    return {"status": "ok"}
