# FastAPI Best Practices Context

## Framework Overview

### Key Features
- **High Performance**: On par with NodeJS and Go, leverages Starlette and Pydantic
- **Type Safety**: Built on standard Python type hints for automatic validation
- **Developer Experience**: 200-300% faster development, 40% fewer bugs
- **Automatic Documentation**: OpenAPI/Swagger docs generated automatically
- **Modern Python**: Full async/await support, intuitive editor support

### Installation
```bash
# Standard installation with all features
pip install "fastapi[standard]"

# Production dependencies
pip install fastapi uvicorn[standard] python-multipart
```

## Core Application Patterns

### 1. Application Structure
```python
# main.py - Application entry point
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

# Create FastAPI instance with metadata
app = FastAPI(
    title="La Factoria API",
    description="Educational content generation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy", "service": "la-factoria-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Request/Response Models with Pydantic
```python
# models/content.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime

class ContentRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200, description="Content topic")
    content_type: Literal["study_guide", "flashcards", "quiz", "podcast"] = Field(
        ..., description="Type of content to generate"
    )
    audience_level: Literal["elementary", "middle_school", "high_school", "college"] = Field(
        ..., description="Target audience education level"
    )
    additional_requirements: Optional[str] = Field(
        None, max_length=1000, description="Additional content requirements"
    )
    
    @validator("topic")
    def validate_topic(cls, v):
        if not v.strip():
            raise ValueError("Topic cannot be empty")
        return v.strip()

class ContentResponse(BaseModel):
    id: str = Field(..., description="Unique content identifier")
    title: str = Field(..., description="Content title")
    content: str = Field(..., description="Generated content")
    content_type: str = Field(..., description="Type of content")
    audience_level: str = Field(..., description="Target audience level")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ContentListResponse(BaseModel):
    contents: List[ContentResponse]
    total: int
    page: int
    page_size: int
    
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### 3. Dependency Injection System
```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from services.auth import verify_api_key
from models.user import User
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from API key."""
    try:
        api_key = credentials.credentials
        user = await verify_api_key(api_key, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

class RateLimitDependency:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.call_history = {}
    
    async def __call__(self, user: User = Depends(get_current_user)):
        import time
        now = time.time()
        user_history = self.call_history.get(user.id, [])
        
        # Remove old calls
        user_history = [call_time for call_time in user_history if now - call_time < self.period]
        
        if len(user_history) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.calls} calls per {self.period} seconds"
            )
        
        user_history.append(now)
        self.call_history[user.id] = user_history
        return user

# Rate limiting instances
content_rate_limit = RateLimitDependency(calls=10, period=60)  # 10 calls per minute
auth_rate_limit = RateLimitDependency(calls=5, period=300)     # 5 calls per 5 minutes
```

## Advanced Async Patterns

### 1. Async Database Operations
```python
# services/content_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
import asyncio

class ContentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_content(self, content_data: ContentRequest, user_id: str) -> ContentResponse:
        """Create new content asynchronously."""
        
        # Generate content using AI service (async)
        generated_content = await self._generate_content_async(content_data)
        
        # Save to database
        content = Content(
            title=generated_content["title"],
            content=generated_content["content"],
            content_type=content_data.content_type,
            audience_level=content_data.audience_level,
            user_id=user_id,
            metadata=generated_content.get("metadata", {})
        )
        
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)
        
        return ContentResponse.from_orm(content)
    
    async def get_user_contents(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 20,
        content_type: Optional[str] = None
    ) -> ContentListResponse:
        """Get user's content with pagination."""
        
        query = select(Content).where(Content.user_id == user_id)
        
        if content_type:
            query = query.where(Content.content_type == content_type)
        
        # Count total records
        count_query = select(func.count(Content.id)).where(Content.user_id == user_id)
        if content_type:
            count_query = count_query.where(Content.content_type == content_type)
        
        total = await self.db.scalar(count_query)
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Content.created_at.desc())
        
        result = await self.db.execute(query)
        contents = result.scalars().all()
        
        return ContentListResponse(
            contents=[ContentResponse.from_orm(content) for content in contents],
            total=total,
            page=page,
            page_size=page_size
        )
    
    async def _generate_content_async(self, content_data: ContentRequest) -> dict:
        """Generate content using AI service asynchronously."""
        
        # Multiple AI providers with concurrent calls for failover
        providers = ["anthropic", "openai"]
        
        async def try_provider(provider_name: str):
            try:
                provider = get_llm_provider(provider_name)
                return await provider.generate_content(
                    topic=content_data.topic,
                    content_type=content_data.content_type,
                    audience_level=content_data.audience_level,
                    additional_requirements=content_data.additional_requirements
                )
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {str(e)}")
                return None
        
        # Try providers concurrently with timeout
        try:
            results = await asyncio.gather(
                *[try_provider(provider) for provider in providers],
                return_exceptions=True
            )
            
            # Return first successful result
            for result in results:
                if result and not isinstance(result, Exception):
                    return result
            
            raise Exception("All content generation providers failed")
            
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Content generation timed out"
            )
```

### 2. Background Tasks and Async Processing
```python
# services/background_tasks.py
from fastapi import BackgroundTasks
from typing import Callable, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class AsyncBackgroundTaskManager:
    def __init__(self):
        self.running_tasks = {}
    
    async def add_task(
        self, 
        task_id: str, 
        task_func: Callable, 
        *args, 
        **kwargs
    ) -> str:
        """Add async background task."""
        
        if task_id in self.running_tasks:
            raise ValueError(f"Task {task_id} is already running")
        
        async def wrapped_task():
            try:
                logger.info(f"Starting background task: {task_id}")
                result = await task_func(*args, **kwargs)
                logger.info(f"Completed background task: {task_id}")
                return result
            except Exception as e:
                logger.error(f"Background task {task_id} failed: {str(e)}")
                raise
            finally:
                # Clean up task reference
                self.running_tasks.pop(task_id, None)
        
        # Start task
        task = asyncio.create_task(wrapped_task())
        self.running_tasks[task_id] = task
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> dict:
        """Get task status."""
        if task_id not in self.running_tasks:
            return {"status": "not_found"}
        
        task = self.running_tasks[task_id]
        
        if task.done():
            if task.exception():
                return {
                    "status": "failed",
                    "error": str(task.exception())
                }
            else:
                return {
                    "status": "completed",
                    "result": task.result()
                }
        else:
            return {"status": "running"}

# Global task manager instance
task_manager = AsyncBackgroundTaskManager()

# Background task examples
async def generate_bulk_content(topics: List[str], user_id: str, content_type: str):
    """Generate multiple content pieces in background."""
    results = []
    
    for topic in topics:
        try:
            content_data = ContentRequest(
                topic=topic,
                content_type=content_type,
                audience_level="high_school"
            )
            
            # Generate content
            content_service = ContentService(get_async_db())
            result = await content_service.create_content(content_data, user_id)
            results.append({"topic": topic, "status": "success", "content_id": result.id})
            
        except Exception as e:
            results.append({"topic": topic, "status": "failed", "error": str(e)})
    
    return results

async def analyze_content_quality(content_id: str):
    """Analyze content quality in background."""
    # Get content from database
    content = await get_content_by_id(content_id)
    
    # Run quality analysis
    quality_service = ContentQualityService()
    analysis = await quality_service.analyze_content(content.content, content.content_type)
    
    # Update content with quality scores
    await update_content_metadata(content_id, {"quality_analysis": analysis})
    
    return analysis
```

## Error Handling and Validation

### 1. Custom Exception Handlers
```python
# exceptions.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class ContentGenerationError(Exception):
    def __init__(self, message: str, provider: str = None, details: dict = None):
        self.message = message
        self.provider = provider
        self.details = details or {}
        super().__init__(self.message)

class RateLimitExceeded(Exception):
    def __init__(self, limit: int, window: int, retry_after: int = None):
        self.limit = limit
        self.window = window
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded: {limit} requests per {window} seconds")

class DatabaseConnectionError(Exception):
    pass

# Exception handlers
async def content_generation_exception_handler(request: Request, exc: ContentGenerationError):
    logger.error(f"Content generation failed: {exc.message} (Provider: {exc.provider})")
    return JSONResponse(
        status_code=503,
        content={
            "error": "Content generation service unavailable",
            "message": exc.message,
            "provider": exc.provider,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    headers = {}
    if exc.retry_after:
        headers["Retry-After"] = str(exc.retry_after)
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": str(exc),
            "limit": exc.limit,
            "window": exc.window
        },
        headers=headers
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

async def database_exception_handler(request: Request, exc: DatabaseConnectionError):
    logger.error(f"Database connection error: {str(exc)}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "Database service unavailable",
            "message": "Please try again later",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Register exception handlers
app.add_exception_handler(ContentGenerationError, content_generation_exception_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(DatabaseConnectionError, database_exception_handler)
```

### 2. Input Validation and Sanitization
```python
# validators.py
from pydantic import validator, root_validator
import re
from typing import Any, Dict

class ContentRequestValidator(BaseModel):
    topic: str
    content_type: str
    audience_level: str
    additional_requirements: Optional[str] = None
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v or not v.strip():
            raise ValueError('Topic cannot be empty')
        
        # Remove potentially harmful content
        sanitized = re.sub(r'[<>{}]', '', v.strip())
        
        if len(sanitized) < 2:
            raise ValueError('Topic must be at least 2 characters long')
        
        if len(sanitized) > 200:
            raise ValueError('Topic must be less than 200 characters')
        
        # Check for inappropriate content (basic example)
        forbidden_terms = ['hack', 'exploit', 'malware', 'virus']
        if any(term in sanitized.lower() for term in forbidden_terms):
            raise ValueError('Topic contains inappropriate content')
        
        return sanitized
    
    @validator('additional_requirements')
    def validate_additional_requirements(cls, v):
        if v is None:
            return v
        
        # Sanitize and limit length
        sanitized = re.sub(r'[<>{}]', '', v.strip())
        
        if len(sanitized) > 1000:
            raise ValueError('Additional requirements must be less than 1000 characters')
        
        return sanitized if sanitized else None
    
    @root_validator
    def validate_combination(cls, values):
        content_type = values.get('content_type')
        audience_level = values.get('audience_level')
        
        # Business logic validation
        if content_type == 'podcast' and audience_level == 'elementary':
            raise ValueError('Podcast format not suitable for elementary level')
        
        return values

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, le=1000, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    @validator('page_size')
    def validate_page_size(cls, v):
        # Limit page size for performance
        if v > 100:
            raise ValueError('Page size cannot exceed 100')
        return v
```

## API Route Organization

### 1. Modular Route Structure
```python
# routes/content.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import List, Optional
import uuid

router = APIRouter(prefix="/api/v1/content", tags=["content"])

@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_async_db)
):
    """Generate educational content."""
    
    try:
        # Validate request
        validated_request = ContentRequestValidator(**request.dict())
        
        # Create content service
        content_service = ContentService(db)
        
        # Generate content
        result = await content_service.create_content(validated_request, current_user.id)
        
        # Add background task for quality analysis
        task_id = str(uuid.uuid4())
        await task_manager.add_task(
            task_id,
            analyze_content_quality,
            result.id
        )
        
        # Add quality analysis task ID to metadata
        result.metadata["quality_analysis_task"] = task_id
        
        return result
        
    except ContentGenerationError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=ContentListResponse)
async def list_contents(
    pagination: PaginationParams = Depends(),
    content_type: Optional[str] = Query(None, regex="^(study_guide|flashcards|quiz|podcast)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """List user's content with pagination and filtering."""
    
    content_service = ContentService(db)
    
    return await content_service.get_user_contents(
        user_id=current_user.id,
        page=pagination.page,
        page_size=pagination.page_size,
        content_type=content_type
    )

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get specific content by ID."""
    
    content_service = ContentService(db)
    content = await content_service.get_content_by_id(content_id, current_user.id)
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return content

@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete content by ID."""
    
    content_service = ContentService(db)
    success = await content_service.delete_content(content_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return {"message": "Content deleted successfully"}

@router.post("/bulk-generate")
async def bulk_generate_content(
    topics: List[str] = Field(..., min_items=1, max_items=10),
    content_type: str = Field(..., regex="^(study_guide|flashcards|quiz)$"),
    current_user: User = Depends(content_rate_limit),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Generate multiple content pieces in background."""
    
    task_id = str(uuid.uuid4())
    
    await task_manager.add_task(
        task_id,
        generate_bulk_content,
        topics,
        current_user.id,
        content_type
    )
    
    return {
        "message": "Bulk generation started",
        "task_id": task_id,
        "status_endpoint": f"/api/v1/tasks/{task_id}"
    }
```

### 2. Authentication Routes
```python
# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Register a new user."""
    
    auth_service = AuthService(db)
    
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    user = await auth_service.create_user(user_data)
    return UserResponse.from_orm(user)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    """Authenticate user and return access token."""
    
    auth_service = AuthService(db)
    
    # Authenticate user
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )

@router.post("/api-key", response_model=ApiKeyResponse)
async def create_api_key(
    key_request: ApiKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new API key for the user."""
    
    auth_service = AuthService(db)
    api_key = await auth_service.create_api_key(
        user_id=current_user.id,
        name=key_request.name,
        expires_in_days=key_request.expires_in_days
    )
    
    return ApiKeyResponse.from_orm(api_key)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return UserResponse.from_orm(current_user)
```

## Sources
41. FastAPI Core Documentation and Features
42. FastAPI Async Programming and Performance Patterns
43. FastAPI Dependency Injection and Authentication
44. FastAPI Request Validation and Error Handling
45. FastAPI Database Integration with SQLAlchemy
46. FastAPI Background Tasks and Async Processing
47. FastAPI Route Organization and API Design
48. FastAPI Production Deployment Best Practices
49. FastAPI Testing Strategies and Quality Assurance
50. FastAPI Security and CORS Configuration