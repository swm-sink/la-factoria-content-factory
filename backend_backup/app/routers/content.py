from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from ..services.content import ContentService
from ..services.audio import AudioService
from ..models.content import ContentRequest, ContentResponse
from ..core.config import settings

router = APIRouter()
content_service = ContentService()
audio_service = AudioService()

@router.post("/generate-content", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    background_tasks: BackgroundTasks
) -> ContentResponse:
    """
    Generate educational content based on the provided request.
    """
    try:
        # Generate content
        content = await content_service.generate_content(
            topic=request.topic,
            content_type=request.content_type,
            target_audience=request.target_audience,
            length=request.length
        )
        
        # Generate audio in background
        audio_url = None
        if request.generate_audio:
            background_tasks.add_task(
                audio_service.generate_audio,
                content.podcast_script,
                f"{uuid.uuid4()}.mp3"
            )
        
        return ContentResponse(
            content=content,
            audio_url=audio_url
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate content: {str(e)}"
        )

@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(content_id: str) -> ContentResponse:
    """
    Retrieve previously generated content by ID.
    """
    try:
        content = await content_service.get_content(content_id)
        if not content:
            raise HTTPException(
                status_code=404,
                detail="Content not found"
            )
        return content
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve content: {str(e)}"
        ) 