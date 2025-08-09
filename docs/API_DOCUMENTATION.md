# La Factoria API Documentation

**Version**: 1.0.0  
**Base URL**: `https://your-domain.com/api/v1`  
**Authentication**: Bearer Token (API Key)

## 🔐 Authentication

All API requests require authentication using an API key in the Authorization header:

```http
Authorization: Bearer your-api-key-here
```

## 📍 Endpoints

### Content Generation

#### Generate Master Content Outline

Create a structured learning framework with objectives.

```http
POST /api/v1/generate/master_content_outline
```

**Request Body:**
```json
{
  "topic": "Photosynthesis in Plants",
  "age_group": "high_school",
  "additional_requirements": "Include lab activities"
}
```

**Response:**
```json
{
  "id": "content_123456",
  "content_type": "master_content_outline",
  "topic": "Photosynthesis in Plants",
  "generated_content": {
    "title": "Photosynthesis in Plants",
    "overview": "...",
    "learning_objectives": [...],
    "sections": [...]
  },
  "quality_metrics": {
    "overall_quality_score": 0.85,
    "educational_effectiveness": 0.88,
    "factual_accuracy": 0.92,
    "age_appropriateness": 0.84
  },
  "metadata": {
    "generation_duration_ms": 3456,
    "tokens_used": 1500,
    "ai_provider": "openai"
  }
}
```

#### Generate Study Guide

Create comprehensive educational material with key concepts.

```http
POST /api/v1/generate/study_guide
```

**Request Body:**
```json
{
  "topic": "The American Revolution",
  "age_group": "middle_school",
  "additional_requirements": "Focus on causes and effects"
}
```

#### Generate Flashcards

Create term-definition pairs for memorization.

```http
POST /api/v1/generate/flashcards
```

**Request Body:**
```json
{
  "topic": "Spanish Vocabulary - Food",
  "age_group": "high_school",
  "additional_requirements": "Include pronunciation guides"
}
```

#### Generate Podcast Script

Create conversational audio content with speaker notes.

```http
POST /api/v1/generate/podcast_script
```

**Request Body:**
```json
{
  "topic": "Introduction to Climate Change",
  "age_group": "general",
  "additional_requirements": "15-minute episode length"
}
```

#### Generate One-Pager Summary

Create a concise overview with essential takeaways.

```http
POST /api/v1/generate/one_pager_summary
```

**Request Body:**
```json
{
  "topic": "Shakespeare's Hamlet",
  "age_group": "college",
  "additional_requirements": "Include major themes"
}
```

#### Generate Detailed Reading Material

Create in-depth content with examples and exercises.

```http
POST /api/v1/generate/detailed_reading_material
```

**Request Body:**
```json
{
  "topic": "Quantum Mechanics Basics",
  "age_group": "college",
  "additional_requirements": "Include mathematical formulas"
}
```

#### Generate FAQ Collection

Create question-answer pairs covering common topics.

```http
POST /api/v1/generate/faq_collection
```

**Request Body:**
```json
{
  "topic": "Python Programming for Beginners",
  "age_group": "adult_learning",
  "additional_requirements": "Cover installation and setup"
}
```

#### Generate Reading Guide Questions

Create discussion questions for comprehension.

```http
POST /api/v1/generate/reading_guide_questions
```

**Request Body:**
```json
{
  "topic": "To Kill a Mockingbird - Chapter 1-5",
  "age_group": "high_school",
  "additional_requirements": "Include character analysis questions"
}
```

#### Batch Content Generation

Generate multiple content types in one request.

```http
POST /api/v1/generate/batch
```

**Request Body:**
```json
{
  "topic": "World War II",
  "age_group": "high_school",
  "content_types": [
    "master_content_outline",
    "study_guide",
    "flashcards",
    "faq_collection"
  ],
  "additional_requirements": "Focus on European theater"
}
```

**Response:**
```json
{
  "batch_id": "batch_789",
  "results": {
    "master_content_outline": {...},
    "study_guide": {...},
    "flashcards": {...},
    "faq_collection": {...}
  },
  "summary": {
    "total_requested": 4,
    "successful": 4,
    "failed": 0,
    "average_quality_score": 0.82
  }
}
```

### System Information

#### Get Content Types

List all available content types.

```http
GET /api/v1/content-types
```

**Response:**
```json
{
  "content_types": [
    {
      "id": "master_content_outline",
      "name": "Master Content Outline",
      "description": "Foundation structure with learning objectives"
    },
    {
      "id": "study_guide",
      "name": "Study Guide",
      "description": "Comprehensive educational material"
    },
    ...
  ]
}
```

#### Service Health

Check content service health status.

```http
GET /api/v1/service/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-08T10:30:00Z",
  "services": {
    "ai_providers": "healthy",
    "quality_assessment": "healthy",
    "prompt_templates": "healthy"
  }
}
```

#### Service Information

Get service configuration and capabilities.

```http
GET /api/v1/service/info
```

**Response:**
```json
{
  "version": "1.0.0",
  "supported_content_types": 8,
  "available_ai_providers": ["openai", "anthropic"],
  "quality_thresholds": {
    "overall": 0.70,
    "educational": 0.75,
    "factual": 0.85
  },
  "rate_limits": {
    "requests_per_minute": 100,
    "generations_per_hour": 500
  }
}
```

### Health & Monitoring

#### Basic Health Check

Simple health check for load balancers.

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-08T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "ai_providers": "healthy (2 available)",
    "prompt_templates": "healthy"
  }
}
```

#### Detailed Health Check

Comprehensive health check with metrics.

```http
GET /api/v1/health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-08T10:30:00Z",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 86400,
  "system_metrics": {
    "cpu_usage_percent": 45.2,
    "memory_usage_percent": 62.1,
    "disk_usage_percent": 38.5
  },
  "services": {
    "database": {
      "status": "healthy",
      "connection": "ok",
      "tables_available": 6
    },
    "ai_providers": {
      "openai": "healthy",
      "anthropic": "healthy",
      "vertex_ai": "unavailable"
    },
    "configuration": {
      "environment": "production",
      "debug_mode": false,
      "langfuse_configured": true,
      "redis_configured": false
    }
  }
}
```

#### Readiness Probe

Kubernetes/Railway readiness check.

```http
GET /api/v1/ready
```

**Response (200 - Ready):**
```json
{
  "status": "ready",
  "timestamp": "2025-08-08T10:30:00Z"
}
```

**Response (503 - Not Ready):**
```json
{
  "status": "not ready",
  "timestamp": "2025-08-08T10:30:00Z",
  "reasons": ["database_unavailable"]
}
```

#### Liveness Probe

Kubernetes/Railway liveness check.

```http
GET /api/v1/live
```

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2025-08-08T10:30:00Z",
  "version": "1.0.0"
}
```

### Administration

#### System Information

Get detailed system information.

```http
GET /api/v1/admin/system/info
```

**Headers:**
```http
Authorization: Bearer admin-api-key
```

**Response:**
```json
{
  "platform": "La Factoria Educational Content Platform",
  "version": "1.0.0",
  "environment": "production",
  "system": {
    "python_version": "3.11.5",
    "platform": "linux",
    "cpu_count": 4,
    "memory_gb": 8
  },
  "configuration": {
    "database_connected": true,
    "ai_providers_configured": 2,
    "cache_enabled": false,
    "rate_limiting_enabled": true
  }
}
```

#### Content Statistics

Get content generation statistics.

```http
GET /api/v1/admin/content/stats
```

**Response:**
```json
{
  "total_content_generated": 1543,
  "content_by_type": {
    "study_guide": 412,
    "flashcards": 387,
    "master_content_outline": 234,
    ...
  },
  "average_quality_scores": {
    "overall": 0.82,
    "educational": 0.85,
    "factual": 0.91
  },
  "generation_metrics": {
    "average_duration_ms": 4523,
    "success_rate": 0.94,
    "regeneration_rate": 0.12
  }
}
```

## 📊 Data Models

### ContentRequest

```typescript
interface ContentRequest {
  topic: string;           // 3-500 characters
  age_group: AgeGroup;     // Enum: see below
  additional_requirements?: string;  // Max 1000 characters
}
```

### AgeGroup

```typescript
enum AgeGroup {
  ELEMENTARY = "elementary",
  MIDDLE_SCHOOL = "middle_school",
  HIGH_SCHOOL = "high_school",
  COLLEGE = "college",
  ADULT_LEARNING = "adult_learning",
  GENERAL = "general"
}
```

### ContentType

```typescript
enum ContentType {
  MASTER_CONTENT_OUTLINE = "master_content_outline",
  PODCAST_SCRIPT = "podcast_script",
  STUDY_GUIDE = "study_guide",
  ONE_PAGER_SUMMARY = "one_pager_summary",
  DETAILED_READING_MATERIAL = "detailed_reading_material",
  FAQ_COLLECTION = "faq_collection",
  FLASHCARDS = "flashcards",
  READING_GUIDE_QUESTIONS = "reading_guide_questions"
}
```

### QualityMetrics

```typescript
interface QualityMetrics {
  overall_quality_score: number;      // 0.0-1.0
  educational_effectiveness: number;   // 0.0-1.0
  factual_accuracy: number;           // 0.0-1.0
  age_appropriateness: number;        // 0.0-1.0
  cognitive_load_metrics?: {
    intrinsic_load: number;
    extraneous_load: number;
    germane_load: number;
    total_cognitive_load: number;
  };
  readability_score?: number;
  engagement_score?: number;
}
```

## 🔥 Error Responses

### Error Format

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    }
  }
}
```

### Common Error Codes

| Status Code | Error Code | Description |
|------------|------------|-------------|
| 400 | `INVALID_REQUEST` | Request validation failed |
| 401 | `UNAUTHORIZED` | Invalid or missing API key |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 422 | `UNPROCESSABLE_ENTITY` | Business logic validation failed |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | Temporary unavailability |

### Example Error Response

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Topic must be between 3 and 500 characters",
    "details": {
      "field": "topic",
      "provided_length": 2,
      "min_length": 3,
      "max_length": 500
    }
  }
}
```

## 🚦 Rate Limiting

API rate limits are enforced per API key:

- **Default Limits:**
  - 100 requests per minute
  - 500 content generations per hour
  - 10,000 requests per day

- **Rate Limit Headers:**
  ```http
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1628547840
  ```

- **Rate Limit Exceeded Response (429):**
  ```json
  {
    "error": {
      "code": "RATE_LIMITED",
      "message": "Rate limit exceeded. Please retry after 60 seconds",
      "details": {
        "retry_after": 60,
        "limit": 100,
        "window": "1 minute"
      }
    }
  }
  ```

## 🔄 Versioning

The API uses URL versioning. The current version is `v1`.

- Current: `/api/v1/...`
- Future: `/api/v2/...` (backward compatible)

## 🛠️ SDKs and Libraries

### Python SDK

```python
from lafactoria import LaFactoriaClient

client = LaFactoriaClient(api_key="your-api-key")

# Generate content
result = client.generate_study_guide(
    topic="Python Programming",
    age_group="high_school"
)

print(result.content)
print(f"Quality Score: {result.quality_metrics.overall_quality_score}")
```

### JavaScript/TypeScript SDK

```typescript
import { LaFactoriaClient } from '@lafactoria/sdk';

const client = new LaFactoriaClient({
  apiKey: 'your-api-key'
});

// Generate content
const result = await client.generateFlashcards({
  topic: 'Spanish Vocabulary',
  ageGroup: 'middle_school'
});

console.log(result.generatedContent);
console.log(`Quality Score: ${result.qualityMetrics.overallQualityScore}`);
```

## 📝 Code Examples

### cURL

```bash
# Generate study guide
curl -X POST https://api.lafactoria.edu/api/v1/generate/study_guide \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Photosynthesis",
    "age_group": "high_school",
    "additional_requirements": "Include diagrams"
  }'
```

### Python (requests)

```python
import requests

url = "https://api.lafactoria.edu/api/v1/generate/flashcards"
headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}
data = {
    "topic": "World War II",
    "age_group": "high_school",
    "additional_requirements": "Focus on key dates"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()
```

### JavaScript (fetch)

```javascript
const response = await fetch('https://api.lafactoria.edu/api/v1/generate/podcast_script', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    topic: 'Climate Change',
    age_group: 'general',
    additional_requirements: '10-minute episode'
  })
});

const result = await response.json();
```

## 🔒 Security

- All API communication must use HTTPS
- API keys should never be exposed in client-side code
- Implement proper CORS headers for browser-based access
- Input validation prevents injection attacks
- Rate limiting prevents abuse

## 📞 Support

- **API Status**: https://status.lafactoria.edu
- **Documentation**: https://docs.lafactoria.edu
- **Support Email**: api-support@lafactoria.edu
- **Discord Community**: https://discord.gg/lafactoria

---

*API Version 1.0.0 | Last Updated: August 2025*