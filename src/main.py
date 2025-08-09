"""
La Factoria - Educational Content Generation Platform
Main FastAPI Application

Generated using patterns from context/fastapi.md + la-factoria-educational-schema.md
Following the "simple implementation, comprehensive context" philosophy
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import logging
import os
from datetime import datetime, timezone

# Rate limiting setup
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Core configuration
from .core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan event handler (replaces deprecated on_event)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("Starting La Factoria Educational Content Platform")
    yield
    # Shutdown
    logger.info("Shutting down La Factoria platform")

# Rate limiter for AI cost protection
limiter = Limiter(key_func=get_remote_address)

# FastAPI app using exact pattern from context/fastapi.md lines 31-38
app = FastAPI(
    title="La Factoria - Educational Content Platform",
    description="AI-powered educational content generation with learning science integration",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Add rate limiting state and error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
from .api.routes import content_generation, health, admin, monitoring

# Use health.router for all health and monitoring endpoints (includes /ready, /live, etc.)
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(content_generation.router, prefix="/api/v1", tags=["Content Generation"])
# Monitoring router conflicts with health router - using health router for all monitoring
# app.include_router(monitoring.router, prefix="/api/v1", tags=["Monitoring"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administration"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with platform information"""
    return {
        "name": "La Factoria",
        "description": "AI-powered educational content generation platform",
        "version": "1.0.0",
        "supported_content_types": [
            "master_content_outline",
            "podcast_script",
            "study_guide",
            "one_pager_summary",
            "detailed_reading_material",
            "faq_collection",
            "flashcards",
            "reading_guide_questions"
        ],
        "status": "active",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.ENVIRONMENT == "development"
    )
