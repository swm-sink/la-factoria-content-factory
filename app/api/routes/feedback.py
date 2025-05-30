"""
API Endpoints for content feedback.
"""

import logging
from uuid import uuid4, UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1.async_client import AsyncClient as FirestoreAsyncClient  # type: ignore

from app.models.pydantic.feedback import FeedbackCreate, FeedbackResponse
from app.services.job.firestore_client import get_firestore_client
from app.api.deps import get_current_active_user  # Import the actual dependency
from app.models.pydantic.user import User  # User model for type hinting

router = APIRouter()
logger = logging.getLogger(__name__)

FEEDBACK_COLLECTION = "feedback"
# Assuming content is identified by a job_id which is a UUID, or a specific content piece ID.
# For simplicity, let's assume content_id is the job_id for now.


@router.post(
    "/content/{content_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback for a piece of content",
    tags=["Feedback"],
)
async def submit_content_feedback(
    content_id: str,  # Could be job_id or a more specific content part ID
    feedback_data: FeedbackCreate,
    db: FirestoreAsyncClient = Depends(get_firestore_client),
    current_user: User = Depends(get_current_active_user),
):
    """
    Allows an authenticated user to submit feedback (like/dislike and optional comment)
    for a specific piece of generated content.

    - **content_id**: The ID of the content (e.g., job ID or specific content part ID).
    - **feedback_data**: The feedback payload including rating and optional comment.
    """
    user_id = current_user.id  # Get user ID from the User model

    feedback_id = uuid4()
    timestamp = datetime.utcnow()

    feedback_doc = {
        "id": str(feedback_id),
        "content_id": content_id,
        "user_id": user_id,
        "rating": feedback_data.rating,
        "comment": feedback_data.comment,
        "created_at": timestamp,
    }

    try:
        feedback_ref = db.collection(FEEDBACK_COLLECTION).document(str(feedback_id))
        await feedback_ref.set(feedback_doc)
        logger.info(
            f"Feedback {feedback_id} for content {content_id} by user {user_id} stored successfully."
        )

        # Prepare response data matching FeedbackResponse model
        response_data = {
            "id": feedback_id,
            "content_id": content_id,
            "user_id": user_id,
            "rating": feedback_data.rating,
            "comment": feedback_data.comment,
            "created_at": timestamp,
        }
        return FeedbackResponse(**response_data)

    except Exception as e:
        logger.error(
            f"Error storing feedback for content {content_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store feedback due to an internal server error.",
        )


# Example of how to potentially retrieve feedback (not part of the task, but for completeness)
# @router.get("/content/{content_id}/feedback", response_model=List[FeedbackResponse], tags=["Feedback"])
# async def get_content_feedback(
#     content_id: str,
#     db: FirestoreAsyncClient = Depends(get_firestore_client),
#     # current_user: User = Depends(get_current_active_user) # For authorization if needed
# ):
#     """Retrieve all feedback for a specific piece of content."""
#     feedback_list = []
#     try:
#         query = db.collection(FEEDBACK_COLLECTION).where("content_id", "==", content_id).stream()
#         async for doc in query:
#             feedback_list.append(FeedbackResponse(**doc.to_dict()))
#         return feedback_list
#     except Exception as e:
#         logger.error(f"Error retrieving feedback for content {content_id}: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve feedback."
#         )
