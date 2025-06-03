# AI Content Factory - Development Best Practices

## Overview

This document outlines the development best practices for the AI Content Factory project, focusing on code quality, testing, and maintenance standards that ensure reliability and scalability.

## Code Quality Standards

### Python Coding Standards

**PEP 8 Compliance**
- All Python code must follow PEP 8 style guidelines
- Use `black` for automatic formatting (line length: 88 characters)
- Use `flake8` for linting with project-specific configuration
- Run formatting and linting as part of pre-commit hooks

**Type Hints**
```python
# ✅ Good: Complete type hints
def generate_content(
    syllabus_text: str,
    target_format: TargetFormat,
    settings: Settings
) -> Optional[GeneratedContent]:
    pass

# ❌ Bad: Missing type hints
def generate_content(syllabus_text, target_format, settings):
    pass
```

**Documentation Standards**
```python
def generate_content_outline(syllabus_text: str) -> ContentOutline:
    """
    Generate a structured content outline from syllabus text.

    This function creates the master outline that serves as the foundation
    for all derivative content types. It uses AI to analyze the input and
    create a hierarchical structure with learning objectives.

    Args:
        syllabus_text: Input text describing the educational content (50-5000 chars)

    Returns:
        ContentOutline: Validated outline with sections and learning objectives

    Raises:
        ValidationError: If syllabus_text doesn't meet length requirements
        ExternalServiceError: If AI service is unavailable

    Example:
        >>> outline = generate_content_outline("Introduction to Python programming...")
        >>> print(outline.title)
        "Python Programming Fundamentals"
    """
```

### Error Handling Patterns

**Custom Exceptions**
```python
# ✅ Good: Specific, actionable exceptions
from app.core.exceptions import ContentGenerationError, JobErrorCode

try:
    content = generate_content(syllabus_text)
except ContentGenerationError as e:
    logger.error(f"Content generation failed: {e.user_message}")
    raise HTTPException(
        status_code=e.status_code,
        detail={"error": e.user_message, "code": e.error_code.name}
    )

# ❌ Bad: Generic exception handling
try:
    content = generate_content(syllabus_text)
except Exception as e:
    return {"error": "Something went wrong"}
```

**Logging Best Practices**
```python
# ✅ Good: Structured logging with context
logger.info(
    "Content generation completed successfully",
    extra={
        "content_type": "podcast_script",
        "duration_seconds": 12.5,
        "token_usage": {"input": 1200, "output": 800},
        "correlation_id": correlation_id
    }
)

# ❌ Bad: Unstructured logging
logger.info("Content generation done")
```

## Testing Standards

### Unit Testing

**Test Structure (AAA Pattern)**
```python
class TestContentGeneration:
    def test_generate_outline_with_valid_input(self):
        # Arrange
        syllabus_text = "Introduction to Machine Learning with 5 key topics..."
        expected_sections = 5

        # Act
        result = generate_content_outline(syllabus_text)

        # Assert
        assert isinstance(result, ContentOutline)
        assert len(result.sections) >= 3
        assert result.title is not None
        assert all(section.title for section in result.sections)
```

**Mocking External Services**
```python
@pytest.fixture
def mock_llm_client():
    with patch('app.services.llm_client.LLMClientService') as mock:
        mock.return_value.call_generative_model.return_value = (
            ContentOutline(title="Test", overview="Test", sections=[...]),
            {"input_tokens": 100, "output_tokens": 200}
        )
        yield mock

def test_content_generation_with_mocked_llm(mock_llm_client):
    # Test using the mocked LLM client
    service = ContentGenerationService()
    result = service.generate_content("test syllabus")

    assert result is not None
    mock_llm_client.return_value.call_generative_model.assert_called_once()
```

### Integration Testing

**API Endpoint Testing**
```python
def test_content_generation_endpoint_success(client, valid_api_key):
    response = client.post(
        "/api/v1/content/generate",
        headers={"X-API-Key": valid_api_key},
        json={
            "syllabus_text": "Valid test content with sufficient length...",
            "target_format": "guide"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "content_outline" in data["content"]
    assert data["content"]["content_outline"]["title"]
```

### Test Data Management

**Fixtures for Consistent Testing**
```python
@pytest.fixture
def sample_syllabus_text():
    return """
    Machine Learning Fundamentals Course

    This course covers the essential concepts of machine learning
    including supervised learning, unsupervised learning, and
    neural networks. Students will learn practical applications
    and implement algorithms using Python and popular libraries.
    """

@pytest.fixture
def sample_content_outline():
    return ContentOutline(
        title="Machine Learning Fundamentals",
        overview="Comprehensive introduction to ML concepts",
        learning_objectives=[
            "Understand supervised vs unsupervised learning",
            "Implement basic ML algorithms",
            "Apply ML to real-world problems"
        ],
        sections=[
            OutlineSection(
                section_number=1,
                title="Introduction to Machine Learning",
                description="Overview of ML concepts and applications",
                key_points=["Definition of ML", "Types of learning", "Applications"]
            )
        ]
    )
```

## Service Architecture Patterns

### Dependency Injection

**Service Dependencies**
```python
# ✅ Good: Clear dependency injection
class ContentGenerationService:
    def __init__(
        self,
        llm_client: LLMClientService,
        cache_service: ContentCacheService,
        quality_validator: QualityValidationService,
        settings: Settings
    ):
        self.llm_client = llm_client
        self.cache_service = cache_service
        self.quality_validator = quality_validator
        self.settings = settings

# FastAPI dependency
def get_content_service(
    llm_client: LLMClientService = Depends(get_llm_client),
    cache_service: ContentCacheService = Depends(get_cache_service),
    settings: Settings = Depends(get_settings)
) -> ContentGenerationService:
    return ContentGenerationService(llm_client, cache_service, settings)
```

### Configuration Management

**Environment-Based Configuration**
```python
# ✅ Good: Type-safe configuration with validation
class Settings(BaseModel):
    # Core application settings
    project_name: str = Field(default="AI Content Factory")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # AI service configuration
    gemini_model_name: str = Field(env="GEMINI_MODEL_NAME")
    max_retries: int = Field(default=3, ge=1, le=10)

    # Resource limits
    max_tokens_per_content_type: Optional[int] = Field(default=1000, env="MAX_TOKENS_PER_TYPE")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v
```

## Performance Guidelines

### Caching Strategies

**Quality-Based Caching**
```python
async def generate_with_cache(
    request: ContentRequest,
    cache_service: ContentCacheService
) -> GeneratedContent:
    # Check cache first
    cache_key = create_cache_key(request)
    cached_content = await cache_service.get(cache_key)

    if cached_content and cached_content.quality_metrics.overall_score >= 0.8:
        logger.info(f"Cache hit for high-quality content: {cache_key}")
        return cached_content

    # Generate new content
    content = await generate_content(request)

    # Cache only high-quality content
    if content.quality_metrics.overall_score >= 0.75:
        await cache_service.set(cache_key, content, ttl=3600)

    return content
```

### Async Processing

**Background Job Patterns**
```python
async def process_content_job(job_id: str) -> None:
    """Process content generation job asynchronously."""
    try:
        # Update job status
        await update_job_status(job_id, "processing")

        # Generate content with progress updates
        content = await generate_content_with_progress(
            job_id,
            progress_callback=lambda p: update_job_progress(job_id, p)
        )

        # Store results
        await store_job_results(job_id, content)
        await update_job_status(job_id, "completed")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        await update_job_status(job_id, "failed", error=str(e))
        raise
```

## Security Best Practices

### Input Validation

**Comprehensive Validation**
```python
class ContentRequest(BaseModel):
    syllabus_text: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Educational content input"
    )

    @field_validator("syllabus_text")
    @classmethod
    def validate_content_safety(cls, v: str) -> str:
        # Basic content safety checks
        if any(prohibited in v.lower() for prohibited in PROHIBITED_TERMS):
            raise ValueError("Content contains prohibited terms")

        # Check for potential injection attempts
        if re.search(r'[<>{}]|javascript:|data:', v, re.IGNORECASE):
            raise ValueError("Content contains potentially unsafe characters")

        return v.strip()
```

### API Security

**Rate Limiting & Authentication**
```python
# Authentication dependency
async def get_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    settings: Settings = Depends(get_settings)
) -> str:
    if not settings.api_key or x_api_key != settings.api_key:
        logger.warning(f"Invalid API key attempt: {x_api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return x_api_key

# Rate limiting (example with custom middleware)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    if await is_rate_limited(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    return await call_next(request)
```

## Monitoring & Observability

### Structured Logging

**Correlation IDs**
```python
async def content_generation_endpoint(
    request: ContentRequest,
    correlation_id: str = Depends(get_correlation_id)
):
    logger.info(
        "Content generation request received",
        extra={
            "correlation_id": correlation_id,
            "target_format": request.target_format,
            "syllabus_length": len(request.syllabus_text)
        }
    )

    # Process request with correlation ID context
    result = await process_with_correlation(request, correlation_id)

    logger.info(
        "Content generation completed",
        extra={
            "correlation_id": correlation_id,
            "success": result is not None,
            "processing_time_seconds": result.metadata.processing_time
        }
    )
```

### Metrics Collection

**Prometheus Metrics**
```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
CONTENT_REQUESTS = Counter(
    'content_requests_total',
    'Total content generation requests',
    ['format', 'status']
)

GENERATION_DURATION = Histogram(
    'content_generation_duration_seconds',
    'Time spent generating content',
    ['content_type']
)

ACTIVE_JOBS = Gauge(
    'active_jobs_total',
    'Number of active content generation jobs'
)

# Use metrics in code
@GENERATION_DURATION.labels(content_type='outline').time()
async def generate_outline(syllabus_text: str) -> ContentOutline:
    CONTENT_REQUESTS.labels(format='outline', status='started').inc()
    try:
        result = await _generate_outline_internal(syllabus_text)
        CONTENT_REQUESTS.labels(format='outline', status='success').inc()
        return result
    except Exception as e:
        CONTENT_REQUESTS.labels(format='outline', status='error').inc()
        raise
```

## Code Review Guidelines

### Review Checklist

**Functionality**
- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled appropriately
- [ ] Error conditions are properly managed
- [ ] Business logic is correct and complete

**Code Quality**
- [ ] Code follows project style guidelines
- [ ] Functions and classes have single responsibilities
- [ ] Code is readable and well-documented
- [ ] No unnecessary complexity or clever tricks

**Testing**
- [ ] New functionality has appropriate test coverage
- [ ] Tests are meaningful and test the right things
- [ ] Integration points are properly tested
- [ ] Error conditions are tested

**Security**
- [ ] Input validation is comprehensive
- [ ] No sensitive information in logs or responses
- [ ] Authentication and authorization are proper
- [ ] External dependencies are safely handled

**Performance**
- [ ] No obvious performance bottlenecks
- [ ] Caching is used appropriately
- [ ] Database queries are efficient
- [ ] Resource usage is reasonable

This comprehensive guide ensures that all development work maintains the high standards required for a production-ready AI content generation service.
