"""Admin routes for monitoring and management."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.api.deps import get_api_key
from app.middleware.connection_monitor import get_connection_pool_status
from app.utils.redis_pool import get_redis_pool, check_redis_health
from app.utils.firestore_pool import get_firestore_pool, check_firestore_health

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_api_key)],
)


@router.get("/connection-pools", response_model=Dict[str, Any])
async def get_connection_pools_status() -> Dict[str, Any]:
    """
    Get detailed status of all connection pools.
    
    Returns connection pool statistics, health status, and performance metrics.
    """
    try:
        # Get overall status
        status = await get_connection_pool_status()
        
        # Add detailed pool information
        try:
            redis_pool = await get_redis_pool()
            status["pools"]["redis"]["detailed_stats"] = redis_pool.get_stats()
        except Exception as e:
            status["pools"]["redis"]["error"] = str(e)
        
        try:
            firestore_pool = await get_firestore_pool()
            status["pools"]["firestore"]["detailed_stats"] = firestore_pool.get_stats()
        except Exception as e:
            status["pools"]["firestore"]["error"] = str(e)
        
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get connection pool status: {str(e)}"
        )


@router.get("/health/redis", response_model=Dict[str, Any])
async def check_redis_health_endpoint() -> Dict[str, Any]:
    """
    Check Redis connection pool health.
    
    Returns detailed health information about the Redis pool.
    """
    try:
        health = await check_redis_health()
        return health
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/health/firestore", response_model=Dict[str, Any])
async def check_firestore_health_endpoint() -> Dict[str, Any]:
    """
    Check Firestore connection pool health.
    
    Returns detailed health information about the Firestore pool.
    """
    try:
        health = await check_firestore_health()
        return health
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }