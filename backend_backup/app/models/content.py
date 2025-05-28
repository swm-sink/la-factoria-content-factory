from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ContentRequest(BaseModel):
    topic: str
    content_type: str
    target_audience: str
    length: str
    generate_audio: bool = False

class Content(BaseModel):
    outline: str
    podcast_script: str
    study_guide: str
    one_pager_summaries: List[str]
    detailed_reading_materials: List[str]
    faqs: List[dict]
    flashcards: List[dict]
    reading_guide_questions: List[str]

class ContentResponse(BaseModel):
    content: Content
    audio_url: Optional[str] = None

class ContentHistory(BaseModel):
    id: str
    topic: str
    content_type: str
    created_at: datetime
    content: Content
    audio_url: Optional[str] = None 