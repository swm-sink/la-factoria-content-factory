from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import os
from datetime import datetime
import uuid

from .routers import content, history
from .core.config import settings
from .core.security import verify_api_key

app = FastAPI(
    title="AI Content Factory API",
    description="API for generating educational content using AI",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key dependency
async def get_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or not verify_api_key(x_api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )
    return x_api_key

# Include routers
app.include_router(
    content.router,
    prefix="/api",
    tags=["content"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    history.router,
    prefix="/api",
    tags=["history"],
    dependencies=[Depends(get_api_key)],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error_id": str(uuid.uuid4()),
        },
    )

# @app.on_event("startup")
# async def startup_event():
#     # Placeholder for initializing clients/services (e.g., Vertex, ElevenLabs, Redis)
#     pass

# Remove the old main execution block if present
# if __name__ == "__main__":
#    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True) 