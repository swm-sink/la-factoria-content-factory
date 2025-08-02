"""
La Factoria Simple - Minimal API
Total lines goal: <200
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException

from .models import ContentType, GenerateRequest, GenerateResponse

# Create simple app
app = FastAPI(title="La Factoria Simple", description="AI content generation without complexity", version="1.0.0")


# Simple auth dependency
async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key from header."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    # For testing, accept test-key-* pattern
    # In production, validate against stored keys
    if not x_api_key.startswith("test-key-"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@app.get("/health")
async def health_check():
    """Simple health check endpoint - no auth required."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat(), "version": "1.0.0"}


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest, api_key: str = Depends(verify_api_key)) -> GenerateResponse:
    """Generate educational content based on topic and type."""
    # For now, return mock content - will integrate AI later
    content_templates = {
        "study_guide": f"# Study Guide: {request.topic}\n\n## Overview\nThis guide covers {request.topic}...",
        "study_guide_enhanced": f"# Enhanced Study Guide: {request.topic}\n\n## Overview\nComprehensive guide for {request.topic}...",
        "flashcards": f"Flashcard Set: {request.topic}\n\nQ1: What is {request.topic}?\nA1: ...",
        "podcast_script": f"# Podcast Script: {request.topic}\n\n[Intro Music]\nHost: Welcome to today's episode about {request.topic}...",
        "one_pager_summary": f"# One-Pager: {request.topic}\n\n**Key Points:**\n• Point 1 about {request.topic}\n• Point 2...",
        "detailed_reading_material": f"# Detailed Reading: {request.topic}\n\n## Introduction\nThis material explores {request.topic} in depth...",
        "faq_collection": f"# FAQ: {request.topic}\n\n**Q1: What is {request.topic}?**\nA1: ...\n\n**Q2: Why is it important?**\nA2: ...",
        "reading_guide_questions": f"# Reading Guide Questions: {request.topic}\n\n1. What are the main concepts in {request.topic}?\n2. How does this relate to...",
        "master_content_outline": f"# Master Outline: {request.topic}\n\nI. Introduction\n   A. Overview\n   B. Objectives\nII. Main Content...",
    }

    content = content_templates.get(request.content_type, f"Content for {request.topic}")

    return GenerateResponse.create(content=content, content_type=request.content_type, topic=request.topic)
