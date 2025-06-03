import uuid  # For generating job_id

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_api_key  # Assuming API key dependency is defined here
from app.models.pydantic.content import ContentRequest, GeneratedContent

# Using the service router for unified/legacy routing
from app.services.service_router import get_service_router

router = APIRouter()


@router.post(
    "/generate", response_model=GeneratedContent, status_code=status.HTTP_200_OK
)
async def generate_content(
    request: ContentRequest,
    api_key: str = Depends(get_api_key),  # Protect this endpoint
    service_router=Depends(get_service_router),
):
    """
    Initiates the content generation process based on the provided syllabus.
    """
    job_id = "manual-request-" + str(uuid.uuid4())

    # This part would typically be asynchronous and return a job ID
    # For direct testing, we'll call it synchronously.
    # The service router will decide between unified and legacy service
    generated_content, metadata, error = await service_router.generate_content(
        job_id=job_id,
        syllabus_text=request.syllabus_text,
        target_format=request.target_format,
        use_cache=request.use_cache,
    )

    if error:
        raise HTTPException(
            status_code=error.get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
            detail={
                "error": error.get("message", "Content generation failed."),
                "code": error.get("code", "UNKNOWN_ERROR"),
                "details": error.get("details", {}),
            },
        )

    return generated_content
