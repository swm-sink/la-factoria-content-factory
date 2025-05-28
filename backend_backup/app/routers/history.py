from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from ..services.history import HistoryService
from ..models.content import ContentHistory

router = APIRouter()
history_service = HistoryService()

@router.get("/content-history", response_model=List[ContentHistory])
async def get_content_history(
    skip: int = 0,
    limit: int = 10
) -> List[ContentHistory]:
    """
    Retrieve a paginated list of content generation history.
    """
    try:
        history = await history_service.get_history(skip=skip, limit=limit)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve content history: {str(e)}"
        )

@router.delete("/content-history/{content_id}")
async def delete_content(content_id: str):
    """
    Delete a specific content entry from history.
    """
    try:
        success = await history_service.delete_content(content_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Content not found"
            )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete content: {str(e)}"
        ) 