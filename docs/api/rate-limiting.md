# API Rate Limiting

## Overview

La Factoria implements comprehensive rate limiting to ensure fair usage and protect against abuse. Rate limits are enforced per API key or IP address.

## Default Limits

### Unauthenticated Requests
- **Default**: 100 requests per hour
- **Burst**: 150 requests per hour (temporary allowance)

### Authenticated Requests (with API Key)
- **Default**: 200 requests per hour (2x unauthenticated)
- **Burst**: 300 requests per hour

### User Tiers
- **Free**: 1x multiplier
- **Basic**: 2x multiplier
- **Premium**: 5x multiplier
- **Enterprise**: 10x multiplier

## Endpoint-Specific Limits

### Content Generation (Most Restrictive)
| Endpoint | Limit | Cost Units |
|----------|-------|------------|
| `/api/v1/content/generate` | 10/hour | 1-5 based on type |
| `/api/v1/content/generate-outline` | 20/hour | 1 |
| `/api/v1/content/batch` | 5/hour | 20 |
| `/api/v1/audio/generate` | 5/hour | 10 |

#### Content Type Costs
- **Podcast Script**: 5 units
- **Detailed Reading**: 4 units
- **Study Guide**: 3 units
- **One-Pager Summary**: 2 units
- **Flashcards**: 2 units
- **FAQs**: 2 units
- **Reading Questions**: 1 unit

### Authentication Endpoints
| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `/api/v1/auth/login` | 10/minute | Prevent brute force |
| `/api/v1/auth/register` | 5/hour | Prevent spam accounts |
| `/api/v1/auth/forgot-password` | 5/hour | Prevent abuse |
| `/api/v1/auth/reset-password` | 5/hour | Prevent abuse |

### General API Endpoints
| Endpoint | Limit |
|----------|-------|
| `/api/v1/users` | 100/hour |
| `/api/v1/users/me` | 200/hour |
| `/api/v1/content` | 200/hour |
| `/api/v1/content/search` | 100/hour |

### Health & Monitoring
| Endpoint | Limit |
|----------|-------|
| `/health` | 1000/minute |
| `/api/v1/health` | 1000/minute |
| `/metrics` | No limit |

## Rate Limit Headers

All API responses include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

- **X-RateLimit-Limit**: Maximum requests allowed in the window
- **X-RateLimit-Remaining**: Requests remaining in current window
- **X-RateLimit-Reset**: Unix timestamp when the window resets

## Exceeding Rate Limits

When rate limits are exceeded, the API returns:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 300
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please retry after 300 seconds.",
    "details": {
      "limit": "100 per hour",
      "retry_after": 300,
      "key": "api_key:YOUR_KEY"
    }
  }
}
```

## Best Practices

### 1. Handle 429 Responses
```python
import time
import requests

def make_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue
            
        return response
    
    raise Exception("Max retries exceeded")
```

### 2. Monitor Your Usage
```python
response = requests.get('https://api.lafactoria.ai/v1/content')
remaining = response.headers.get('X-RateLimit-Remaining')
print(f"Requests remaining: {remaining}")
```

### 3. Implement Exponential Backoff
```python
import time
import random

def exponential_backoff(attempt):
    """Calculate backoff time with jitter."""
    base_delay = 2 ** attempt
    jitter = random.uniform(0, 1)
    return base_delay + jitter
```

### 4. Use Batch Endpoints
Instead of making multiple individual requests, use batch endpoints when available:

```python
# Instead of this (10 requests = 10 units)
for topic in topics:
    generate_content(topic)

# Do this (1 request = 20 units, but more efficient)
batch_generate_content(topics)
```

## Cost-Based Rate Limiting

Some operations consume more "cost units" than others:

```python
# Low cost (1 unit)
GET /api/v1/content/123

# Medium cost (2-3 units)
POST /api/v1/content/generate
{
  "content_type": "flashcards",
  "topic": "Biology"
}

# High cost (5 units)
POST /api/v1/content/generate
{
  "content_type": "podcast_script",
  "topic": "Climate Change"
}

# Very high cost (10 units)
POST /api/v1/audio/generate
{
  "text": "...",
  "voice": "nova"
}
```

## Distributed Rate Limiting

La Factoria uses Redis for distributed rate limiting across multiple instances:

- **Consistency**: Rate limits are enforced globally across all API servers
- **Performance**: Sub-millisecond latency for rate limit checks
- **Reliability**: Graceful degradation if Redis is unavailable

## Exemptions

The following are exempt from rate limiting:

### Paths
- `/docs`, `/redoc`, `/openapi.json` - API documentation
- `/metrics` - Prometheus metrics
- `/internal/*` - Internal health checks
- Static assets (`/static/*`, `/_next/*`)

### Requests
- Internal service-to-service calls (with `X-Internal-Request: true` header)
- Whitelisted IP addresses (configured by admins)

## Troubleshooting

### Common Issues

1. **"Rate limit exceeded" immediately**
   - Check if you're sharing an IP with other users
   - Verify your API key is being sent correctly
   - Check if you're accounting for operation costs

2. **Different limits than expected**
   - Verify your user tier
   - Check if the endpoint has specific limits
   - Ensure API key is valid and active

3. **Rate limits not resetting**
   - Check the `X-RateLimit-Reset` timestamp
   - Verify your system clock is accurate
   - Contact support if limits persist after reset time

### Support

For rate limit increases or enterprise plans, contact:
- Email: support@lafactoria.ai
- Include your API key and use case details