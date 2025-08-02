"""
La Factoria Simple - Minimal API
Total lines goal: <200
"""
from datetime import datetime, timezone
from fastapi import FastAPI

# Create simple app
app = FastAPI(
    title="La Factoria Simple",
    description="AI content generation without complexity",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Simple health check endpoint - no auth required."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }