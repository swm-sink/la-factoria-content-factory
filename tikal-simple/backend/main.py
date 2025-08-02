"""
Simplified Tikal Backend - Entire API in ~150 lines
For 1-10 users who need content generation without enterprise complexity
"""
import os
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import httpx

# Simple environment-based config (Railway handles secrets)
API_KEYS = os.getenv("API_KEYS", "test-key-123,admin-key-123").split(",")
ADMIN_KEYS = os.getenv("ADMIN_KEYS", "admin-key-123").split(",")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # or "anthropic"
AI_API_KEY = os.getenv("AI_API_KEY", "")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")

# Initialize simple app
app = FastAPI(
    title="Tikal Simple",
    description="Content generation made simple",
    version="1.0.0"
)

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Models (Pydantic) ---
class ContentRequest(BaseModel):
    topic: str
    content_type: str = "study_guide"

class ContentResponse(BaseModel):
    content: str
    generated_at: str
    content_type: str

# --- Simple Auth ---
async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Simple API key verification"""
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

async def verify_admin_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Admin API key verification"""
    if not x_api_key or x_api_key not in ADMIN_KEYS:
        raise HTTPException(status_code=401, detail="Admin access required")
    return x_api_key

# --- Simplified AI Generation ---
async def generate_with_ai(prompt: str) -> str:
    """Simple AI content generation - no complex orchestration"""
    try:
        if AI_PROVIDER == "openai":
            # OpenAI implementation
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {AI_API_KEY}"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 2000
                    }
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        else:
            # Anthropic implementation
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": AI_API_KEY,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 2000
                    }
                )
                response.raise_for_status()
                return response.json()["content"][0]["text"]
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        raise HTTPException(status_code=500, detail="Content generation failed")

# --- Endpoints ---
@app.get("/health")
async def health_check():
    """Simple health check for Railway"""
    return {"status": "healthy"}

@app.post("/api/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generate educational content - dramatically simplified"""
    logger.info(f"Generating {request.content_type} for topic: {request.topic}")
    
    # In real implementation, fetch prompt from Langfuse
    # For now, simple prompt
    prompt = f"Create a {request.content_type} about {request.topic}. Be concise and educational."
    
    # Generate content
    content = await generate_with_ai(prompt)
    
    # Return response (no complex caching or versioning)
    return ContentResponse(
        content=content,
        generated_at=datetime.utcnow().isoformat(),
        content_type=request.content_type
    )

@app.delete("/api/user/{user_id}")
async def delete_user(
    user_id: str,
    api_key: str = Depends(verify_admin_key)
):
    """GDPR compliance - simple user deletion"""
    # In production: Delete from Railway Postgres
    # For demo: Just log and return success
    logger.info(f"Deleting user {user_id} and all associated content")
    
    # await db.execute("DELETE FROM content WHERE user_id = ?", user_id)
    # await db.execute("DELETE FROM users WHERE id = ?", user_id)
    
    return {"status": "deleted", "user_id": user_id}

@app.get("/api/stats")
async def get_stats(api_key: str = Depends(verify_api_key)):
    """Simple stats - no Prometheus needed"""
    # In production: Query Railway Postgres
    # For demo: Return mock data
    return {
        "total_generations": 42,
        "active_users": 8,
        "uptime_hours": 168,
        "last_generation": datetime.utcnow().isoformat()
    }

# --- Error Handler ---
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Simple error handling - no complex middleware"""
    logger.error(f"Unhandled error: {exc}")
    return {"error": "Something went wrong", "detail": str(exc)}

# That's it! Entire backend in <150 lines
# No complex services, no middleware madness, no over-engineering