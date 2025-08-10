"""
Service mocks for La Factoria test suite
"""

from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional, List
import uuid
import random
from datetime import datetime


class MockAIProvider:
    """Mock AI provider for testing"""
    
    def __init__(self, provider_name: str = "mock_provider", should_fail: bool = False):
        self.provider_name = provider_name
        self.should_fail = should_fail
        self.call_count = 0
        self.last_request = None
    
    async def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Mock content generation"""
        self.call_count += 1
        self.last_request = {"prompt": prompt, "kwargs": kwargs}
        
        if self.should_fail:
            raise Exception("Mock AI provider error")
        
        return {
            "content": f"Generated content for: {prompt[:50]}...",
            "model": f"{self.provider_name}_model",
            "tokens_used": random.randint(100, 1000),
            "generation_time": random.uniform(0.5, 3.0)
        }
    
    def reset(self):
        """Reset mock state"""
        self.call_count = 0
        self.last_request = None


class MockRedisClient:
    """Mock Redis client for testing"""
    
    def __init__(self, connected: bool = True):
        self.connected = connected
        self.data = {}
        self.call_log = []
    
    async def get(self, key: str) -> Optional[str]:
        """Mock get operation"""
        self.call_log.append(("get", key))
        if not self.connected:
            raise ConnectionError("Redis not connected")
        return self.data.get(key)
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Mock set operation"""
        self.call_log.append(("set", key, value, ex))
        if not self.connected:
            raise ConnectionError("Redis not connected")
        self.data[key] = value
        return True
    
    async def delete(self, key: str) -> int:
        """Mock delete operation"""
        self.call_log.append(("delete", key))
        if not self.connected:
            raise ConnectionError("Redis not connected")
        return 1 if self.data.pop(key, None) else 0
    
    async def exists(self, key: str) -> bool:
        """Mock exists operation"""
        self.call_log.append(("exists", key))
        if not self.connected:
            raise ConnectionError("Redis not connected")
        return key in self.data
    
    async def ping(self) -> bool:
        """Mock ping operation"""
        self.call_log.append(("ping",))
        return self.connected
    
    def reset(self):
        """Reset mock state"""
        self.data.clear()
        self.call_log.clear()


class MockDatabase:
    """Mock database for testing"""
    
    def __init__(self):
        self.data = {
            "users": {},
            "content": {},
            "sessions": {}
        }
        self.transaction_active = False
        self.call_log = []
    
    def begin_transaction(self):
        """Mock transaction begin"""
        self.transaction_active = True
        self.call_log.append("begin_transaction")
    
    def commit(self):
        """Mock transaction commit"""
        self.transaction_active = False
        self.call_log.append("commit")
    
    def rollback(self):
        """Mock transaction rollback"""
        self.transaction_active = False
        self.call_log.append("rollback")
    
    def insert(self, table: str, data: Dict[str, Any]) -> str:
        """Mock insert operation"""
        record_id = str(uuid.uuid4())
        data["id"] = record_id
        data["created_at"] = datetime.utcnow()
        self.data[table][record_id] = data
        self.call_log.append(("insert", table, record_id))
        return record_id
    
    def select(self, table: str, conditions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock select operation"""
        self.call_log.append(("select", table, conditions))
        if conditions is None:
            return list(self.data[table].values())
        
        results = []
        for record in self.data[table].values():
            if all(record.get(k) == v for k, v in conditions.items()):
                results.append(record)
        return results
    
    def update(self, table: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Mock update operation"""
        self.call_log.append(("update", table, record_id))
        if record_id in self.data[table]:
            self.data[table][record_id].update(data)
            self.data[table][record_id]["updated_at"] = datetime.utcnow()
            return True
        return False
    
    def delete(self, table: str, record_id: str) -> bool:
        """Mock delete operation"""
        self.call_log.append(("delete", table, record_id))
        return self.data[table].pop(record_id, None) is not None
    
    def reset(self):
        """Reset mock state"""
        for table in self.data:
            self.data[table].clear()
        self.call_log.clear()
        self.transaction_active = False


class MockRateLimiter:
    """Mock rate limiter for testing"""
    
    def __init__(self, limit: int = 10, window: int = 60):
        self.limit = limit
        self.window = window
        self.requests = {}
        self.blocked = False
    
    async def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit"""
        if self.blocked:
            return False
        
        now = datetime.utcnow()
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [
            req for req in self.requests[key] 
            if (now - req).seconds < self.window
        ]
        
        if len(self.requests[key]) >= self.limit:
            return False
        
        self.requests[key].append(now)
        return True
    
    async def get_remaining(self, key: str) -> int:
        """Get remaining requests"""
        if key not in self.requests:
            return self.limit
        return max(0, self.limit - len(self.requests[key]))
    
    def reset(self):
        """Reset mock state"""
        self.requests.clear()
        self.blocked = False


class MockHTTPClient:
    """Mock HTTP client for testing external API calls"""
    
    def __init__(self):
        self.responses = {}
        self.call_log = []
        self.default_response = {"status": "ok"}
    
    def set_response(self, url: str, response: Dict[str, Any], status_code: int = 200):
        """Set mock response for URL"""
        self.responses[url] = {"data": response, "status_code": status_code}
    
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Mock GET request"""
        self.call_log.append(("GET", url, kwargs))
        if url in self.responses:
            return self.responses[url]
        return {"data": self.default_response, "status_code": 200}
    
    async def post(self, url: str, json: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Mock POST request"""
        self.call_log.append(("POST", url, json, kwargs))
        if url in self.responses:
            return self.responses[url]
        return {"data": self.default_response, "status_code": 200}
    
    def reset(self):
        """Reset mock state"""
        self.responses.clear()
        self.call_log.clear()


def create_mock_fastapi_request(
    method: str = "GET",
    path: str = "/",
    headers: Dict[str, str] = None,
    query_params: Dict[str, str] = None,
    json_body: Dict[str, Any] = None
) -> Mock:
    """Create a mock FastAPI request"""
    request = Mock()
    request.method = method
    request.url.path = path
    request.headers = headers or {}
    request.query_params = query_params or {}
    request.json = AsyncMock(return_value=json_body) if json_body else AsyncMock(side_effect=ValueError)
    request.body = AsyncMock(return_value=b"")
    return request


def create_mock_settings(**overrides) -> Mock:
    """Create mock settings object"""
    settings = Mock()
    settings.API_KEY = None
    settings.ADMIN_API_KEY = "admin_key_123"
    settings.DATABASE_URL = "sqlite:///test.db"
    settings.REDIS_URL = "redis://localhost:6379"
    settings.OPENAI_API_KEY = "mock_openai_key"
    settings.ANTHROPIC_API_KEY = "mock_anthropic_key"
    settings.RATE_LIMIT_PER_MINUTE = 60
    settings.RATE_LIMIT_PER_5MIN = 100
    settings.MAX_REQUEST_SIZE = 1048576
    settings.ENVIRONMENT = "test"
    
    for key, value in overrides.items():
        setattr(settings, key, value)
    
    return settings