"""
Content Generation API Routes for La Factoria
FastAPI endpoints for all 8 educational content types
Following patterns from FastAPI context and educational requirements
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from typing import List, Dict, Any
import logging
import time

# Simple rate limiting for AI cost protection
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ...core.auth import verify_api_key
from ...models.content import (
    ContentRequest,
    ContentResponse,
    ContentTypesResponse,
    CONTENT_TYPE_CONFIGS
)
from ...models.educational import LaFactoriaContentType, LearningObjectiveModel
from ...services.educational_content_service import EducationalContentService

logger = logging.getLogger(__name__)

# Simple rate limiter for expensive AI operations
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

# Initialize content service (will be done per request for now)
async def get_content_service() -> EducationalContentService:
    """Dependency to get initialized content service"""
    service = EducationalContentService()
    await service.initialize()
    return service

@router.get("/content-types", response_model=ContentTypesResponse)
async def get_content_types():
    """
    Get all available educational content types supported by La Factoria

    Returns information about all 8 supported content types including:
    - Content type identifiers and names
    - Descriptions and use cases
    - Estimated generation times
    """
    try:
        content_types = [
            config for config in CONTENT_TYPE_CONFIGS.values()
        ]

        return ContentTypesResponse(
            content_types=content_types,
            total_count=len(content_types)
        )

    except Exception as e:
        logger.error(f"Failed to get content types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content types"
        )

@router.post("/generate/master_content_outline", response_model=ContentResponse)
@limiter.limit("10/minute")  # Simple: 10 content generations per minute per IP
async def generate_master_content_outline(
    request: Request,
    content_request: ContentRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(get_content_service)
):
    """
    Generate Master Content Outline - Foundation structure with learning objectives

    Creates a comprehensive outline that follows Bloom's taxonomy principles and provides
    scaffolding for other content types. Ideal for course planning and curriculum development.
    """
    try:
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.MASTER_CONTENT_OUTLINE.value,
            topic=content_request.topic,
            age_group=content_request.age_group.value,
            learning_objectives=[obj.to_learning_objective() for obj in content_request.learning_objectives] if content_request.learning_objectives else None,
            additional_requirements=content_request.additional_requirements
        )

        return ContentResponse(**result)

    except Exception as e:
        logger.error(f"Master content outline generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/generate/podcast_script", response_model=ContentResponse)
async def generate_podcast_script(
    request: ContentRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(get_content_service)
):
    """
    Generate Podcast Script - Conversational audio content with speaker notes

    Creates engaging audio content with timing guidance and production notes.
    Includes conversational flow and speaker cues for educational podcasts.
    """
    try:
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.PODCAST_SCRIPT.value,
            topic=request.topic,
            age_group=request.age_group.value,
            learning_objectives=[obj.to_learning_objective() for obj in request.learning_objectives] if request.learning_objectives else None,
            additional_requirements=request.additional_requirements
        )

        return ContentResponse(**result)

    except Exception as e:
        logger.error(f"Podcast script generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/generate/study_guide", response_model=ContentResponse)
@limiter.limit("10/minute")  # Simple: 10 content generations per minute per IP
async def generate_study_guide(
    request: Request,
    content_request: ContentRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(get_content_service)
):
    """
    Generate Study Guide - Comprehensive educational material with key concepts

    Creates detailed study materials with examples, exercises, and practice questions.
    Perfect for exam preparation and comprehensive learning support.
    """
    try:
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.STUDY_GUIDE.value,
            topic=content_request.topic,
            age_group=content_request.age_group.value,
            learning_objectives=[obj.to_learning_objective() for obj in content_request.learning_objectives] if content_request.learning_objectives else None,
            additional_requirements=content_request.additional_requirements
        )

        return ContentResponse(**result)

    except Exception as e:
        logger.error(f"Study guide generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/generate/one_pager_summary", response_model=ContentResponse)
async def generate_one_pager_summary(
    request: ContentRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(get_content_service)
):
    """
    Generate One-Pager Summary - Concise overview with essential takeaways

    Creates a focused, single-page summary with key information and takeaways.
    Ideal for quick reference, executive summaries, and concept overviews.
    """
    try:
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.ONE_PAGER_SUMMARY.value,
            topic=request.topic,
            age_group=request.age_group.value,
            learning_objectives=[obj.to_learning_objective() for obj in request.learning_objectives] if request.learning_objectives else None,
            additional_requirements=request.additional_requirements
        )

        return ContentResponse(**result)

    except Exception as e:
        logger.error(f"One-pager summary generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/generate/detailed_reading_material", response_model=ContentResponse)
async def generate_detailed_reading_material(
    request: ContentRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(get_content_service)
):
    """
    Generate Detailed Reading Material - In-depth content with examples and exercises

    Creates comprehensive reading materials with detailed explanations, examples,
    and practice exercises. Perfect for textbook-style learning resources.
    """
    try:
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.DETAILED_READING_MATERIAL.value,
            topic=request.topic,
            age_group=request.age_group.value,
            learning_objectives=[obj.to_learning_objective() for obj in request.learning_objectives] if request.learning_objectives else None,
            additional_requirements=request.additional_requirements
        )

        return ContentResponse(**result)

    except Exception as e:
        logger.error(f"Detailed reading material generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/generate/faq_collection", response_model=ContentResponse)
async def generate_faq_collection(
    request: ContentRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(get_content_service)
):
    """
    Generate FAQ Collection - Question-answer pairs covering common topics

    Creates comprehensive FAQ addressing common questions and misconceptions.
    Ideal for student support materials and learning troubleshooting.
    """
    try:
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.FAQ_COLLECTION.value,
            topic=request.topic,
            age_group=request.age_group.value,
            learning_objectives=[obj.to_learning_objective() for obj in request.learning_objectives] if request.learning_objectives else None,
            additional_requirements=request.additional_requirements
        )

        return ContentResponse(**result)

    except Exception as e:
        logger.error(f"FAQ collection generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/generate/flashcards", response_model=ContentResponse)
async def generate_flashcards(
    request: ContentRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(get_content_service)
):
    """
    Generate Flashcards - Term-definition pairs for memorization and review

    Creates optimized flashcards for spaced repetition and memory consolidation.
    Perfect for vocabulary learning and fact memorization.
    """
    try:
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.FLASHCARDS.value,
            topic=request.topic,
            age_group=request.age_group.value,
            learning_objectives=[obj.to_learning_objective() for obj in request.learning_objectives] if request.learning_objectives else None,
            additional_requirements=request.additional_requirements
        )

        return ContentResponse(**result)

    except Exception as e:
        logger.error(f"Flashcards generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/generate/reading_guide_questions", response_model=ContentResponse)
async def generate_reading_guide_questions(
    request: ContentRequest,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(get_content_service)
):
    """
    Generate Reading Guide Questions - Discussion questions for comprehension

    Creates thought-provoking questions for reading comprehension and critical thinking.
    Ideal for book clubs, group discussions, and comprehension assessment.
    """
    try:
        result = await content_service.generate_content(
            content_type=LaFactoriaContentType.READING_GUIDE_QUESTIONS.value,
            topic=request.topic,
            age_group=request.age_group.value,
            learning_objectives=[obj.to_learning_objective() for obj in request.learning_objectives] if request.learning_objectives else None,
            additional_requirements=request.additional_requirements
        )

        return ContentResponse(**result)

    except Exception as e:
        logger.error(f"Reading guide questions generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/generate/batch", response_model=Dict[str, Any])
async def generate_batch_content(
    content_types: List[LaFactoriaContentType],
    request: ContentRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(get_content_service)
):
    """
    Generate multiple content types for the same topic concurrently

    Creates a comprehensive educational package with multiple content types.
    Useful for complete course development and educational material creation.
    """
    try:
        if not content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one content type must be specified"
            )

        if len(content_types) > 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 8 content types allowed per batch request"
            )

        logger.info(f"Batch generation requested for {len(content_types)} content types")

        result = await content_service.generate_multiple_content_types(
            topic=request.topic,
            content_types=[ct.value for ct in content_types],
            age_group=request.age_group.value,
            learning_objectives=[obj.to_learning_objective() for obj in request.learning_objectives] if request.learning_objectives else None,
            additional_requirements=request.additional_requirements
        )

        return result

    except Exception as e:
        logger.error(f"Batch content generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch generation failed: {str(e)}"
        )

@router.get("/service/info")
async def get_service_info(
    api_key: str = Depends(verify_api_key),
    content_service: EducationalContentService = Depends(get_content_service)
):
    """
    Get information about the educational content service

    Returns service status, supported content types, and configuration information.
    """
    try:
        return await content_service.get_content_type_info()

    except Exception as e:
        logger.error(f"Failed to get service info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve service information"
        )

@router.get("/service/health")
async def get_service_health():
    """
    Health check for the educational content generation service

    Returns detailed health status for all service components.
    """
    try:
        content_service = EducationalContentService()
        return await content_service.health_check()

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "overall_status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }
