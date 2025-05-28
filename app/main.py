"""
Main application entry point for the AI Content Factory.
"""

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
import logging
import os
from prometheus_client import start_http_server
from app.core.config.settings import get_settings
from app.api.routes import api_router

# Get settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format=settings.log_format
)

logger = logging.getLogger(__name__)

# API Key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or api_key != settings.api_key:
        logger.warning(f"Invalid or missing API key attempt. Provided key: '{api_key[:10]}...' if any.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key.")
    return api_key

# FastAPI app
app = FastAPI(
    title=settings.project_name,
    version="1.0.0"
)

# Include API router with version prefix
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Start Prometheus metrics server if not in testing mode
if os.getenv('PROMETHEUS_DISABLE') != 'true':
    try:
        start_http_server(8000)
        logger.info("Prometheus metrics server started on port 8000")
    except OSError as e:
        logger.warning(f"Could not start Prometheus metrics server: {e}")

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")
    pass

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown...")
    pass

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
