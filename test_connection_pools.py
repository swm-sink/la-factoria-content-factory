#!/usr/bin/env python3
"""Quick test script to verify connection pools are working."""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.redis_pool import get_redis_pool, redis_set, redis_get
from app.utils.firestore_pool import get_firestore_pool


async def test_pools():
    """Test basic pool functionality."""
    print("Testing connection pools...")
    
    try:
        # Test Redis pool
        print("\n1. Testing Redis pool...")
        redis_pool = await get_redis_pool()
        print(f"   ✓ Redis pool initialized: {redis_pool.get_stats()}")
        
        # Test basic operation
        await redis_set("test_key", "test_value", ex=60)
        value = await redis_get("test_key")
        print(f"   ✓ Redis operation successful: {value}")
        
    except Exception as e:
        print(f"   ✗ Redis pool error: {e}")
    
    try:
        # Test Firestore pool
        print("\n2. Testing Firestore pool...")
        firestore_pool = await get_firestore_pool()
        print(f"   ✓ Firestore pool initialized: {firestore_pool.get_stats()}")
        
    except Exception as e:
        print(f"   ✗ Firestore pool error: {e}")
    
    print("\nConnection pools are ready!")


if __name__ == "__main__":
    asyncio.run(test_pools())