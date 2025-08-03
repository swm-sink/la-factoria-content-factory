"""
FastAPI Application Setup Example for La Factoria
=================================================

This example shows the recommended FastAPI application structure for La Factoria,
following the "simple implementation" principle while maintaining production quality.

Key patterns demonstrated:
- Minimal but complete FastAPI setup
- Educational content generation endpoints
- Proper error handling and logging
- API key authentication
- Pydantic models for validation
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="La Factoria Educational Content Generator",
    description="AI-powered platform for generating educational materials",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security setup
security = HTTPBearer()

# Pydantic models for request/response validation
class ContentRequest(BaseModel):
    """Request model for content generation"""
    topic: str = Field(..., description="The educational topic to generate content for")
    content_type: str = Field(..., description="Type of content (study_guide, flashcards, etc.)")
    target_audience: str = Field(default="high-school", description="Target educational level")
    language: str = Field(default="en", description="Content language")

    class Config:
        schema_extra = {
            "example": {
                "topic": "Python Programming Basics",
                "content_type": "study_guide",
                "target_audience": "high-school",
                "language": "en"
            }
        }

class ContentResponse(BaseModel):
    """Response model for generated content"""
    id: str = Field(..., description="Unique content identifier")
    topic: str = Field(..., description="The educational topic")
    content_type: str = Field(..., description="Type of generated content")
    content: str = Field(..., description="The generated educational content")
    quality_score: float = Field(..., description="Content quality assessment (0-1)")
    created_at: datetime = Field(..., description="Content generation timestamp")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str

# Authentication dependency
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify API key authentication

    In production, this would validate against a database or secure storage.
    For simplicity, we use environment variable validation.
    """
    api_key = credentials.credentials
    valid_api_key = os.getenv("API_KEY", "dev-key-for-testing")

    if api_key != valid_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring and deployment verification
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

# Content generation endpoint
@app.post("/api/v1/generate", response_model=ContentResponse, tags=["Content Generation"])
async def generate_content(
    request: ContentRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate educational content using AI models

    This endpoint demonstrates the core content generation pattern:
    1. Validate request data
    2. Generate content using AI (placeholder for actual implementation)
    3. Assess content quality
    4. Return structured response
    """
    try:
        logger.info(f"Generating {request.content_type} for topic: {request.topic}")

        # Placeholder for actual AI content generation
        # In real implementation, this would:
        # 1. Load appropriate prompt template from la-factoria/prompts/
        # 2. Call AI service (Vertex AI, OpenAI, etc.)
        # 3. Apply quality assessment using .claude/components/
        generated_content = f"""
        # {request.topic} - {request.content_type.title()}

        This is a placeholder for AI-generated educational content.

        ## Learning Objectives
        - Understand core concepts of {request.topic}
        - Apply knowledge through practical examples
        - Assess comprehension through structured exercises

        ## Content
        [AI-generated educational content would appear here]
        """

        # Placeholder quality assessment
        quality_score = 0.85  # Would be calculated by quality assessment pipeline

        # Generate unique content ID
        content_id = f"content_{datetime.utcnow().timestamp()}"

        response = ContentResponse(
            id=content_id,
            topic=request.topic,
            content_type=request.content_type,
            content=generated_content.strip(),
            quality_score=quality_score,
            created_at=datetime.utcnow()
        )

        logger.info(f"Content generated successfully: {content_id}")
        return response

    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

# Content types endpoint
@app.get("/api/v1/content-types", response_model=List[str], tags=["Configuration"])
async def get_content_types():
    """
    Return available content types for generation

    This matches the 8 content types defined in CLAUDE.md:
    1. Master Content Outline
    2. Podcast Script
    3. Study Guide
    4. One-Pager Summary
    5. Detailed Reading Material
    6. FAQ Collection
    7. Flashcards
    8. Reading Guide Questions
    """
    return [
        "master_content_outline",
        "podcast_script",
        "study_guide",
        "one_pager_summary",
        "detailed_reading_material",
        "faq_collection",
        "flashcards",
        "reading_guide_questions"
    ]

# Run application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
