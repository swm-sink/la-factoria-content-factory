# Configuration Guide

This document describes all configuration options for the AI Content Factory project.

## Environment Variables

### Core Application Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | None | Yes (for GSM) |
| `GCP_LOCATION` | GCP region for services | `us-central1` | No |
| `APP_PORT` | Port for Uvicorn server | `8080` | No |

### API Keys & Secrets

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_KEY` | Application API key for authentication | None | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS service key | None | Yes |
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars) | None | Yes |
| `SENTRY_DSN` | Sentry error reporting DSN | None | No |

### AI Model Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_MODEL_NAME` | Gemini model to use | `models/gemini-2.5-flash-preview-05-20` | No |

**Valid model names:**
- `models/gemini-1.0-pro[-latest|-001|-002]`
- `models/gemini-1.5-pro[-latest|-001|-002]`
- `models/gemini-1.5-flash[-latest|-001|-002]`
- `models/gemini-2.5-flash-preview-05-20`

### CORS Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `http://localhost:3000,http://localhost:5173,http://localhost:8080` | No |

**Examples:**
```bash
# Comma-separated
CORS_ORIGINS=http://localhost:3000,https://app.example.com

# JSON array format
CORS_ORIGINS='["http://localhost:3000", "https://app.example.com"]'
```

### Frontend Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VITE_API_BASE_URL` | Backend API URL for frontend | `http://localhost:8000` | No |

### Redis Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_HOST` | Redis server hostname | `localhost` | No |
| `REDIS_PORT` | Redis server port | `6379` | No |
| `REDIS_DB` | Redis database number | `0` | No |
| `REDIS_PASSWORD` | Redis password | None | No |
| `REDIS_SSL` | Enable SSL for Redis | `false` | No |
| `REDIS_MAX_CONNECTIONS` | Max Redis connections | `50` | No |

### Cache Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CACHE_TTL_SECONDS` | Default cache TTL | `3600` | No |
| `CACHE_MAX_SIZE` | Maximum cache entries | `1000` | No |
| `ENABLE_CACHE` | Enable content caching | `true` | No |
| `CACHE_MIN_QUALITY_RETRIEVAL` | Min quality for cache retrieval | `0.7` | No |

### Content Generation

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MAX_REFINEMENT_ITERATIONS` | Max quality refinement attempts | `2` | No |
| `ENABLE_PARALLEL_PROCESSING` | Enable parallel generation | `true` | No |

### Monitoring & Tracking

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_COST_TRACKING` | Track API costs | `true` | No |
| `ENABLE_PERFORMANCE_TRACKING` | Track performance metrics | `true` | No |
| `ENABLE_QUALITY_METRICS` | Track quality metrics | `true` | No |
| `PROMETHEUS_PORT` | Prometheus metrics port | `9000` | No |

### Cloud Tasks Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TASKS_QUEUE_NAME` | Cloud Tasks queue name | `content-generation-queue` | No |
| `TASKS_WORKER_SERVICE_URL` | Worker service URL | Auto-generated | No |

## Test Configuration

For testing purposes, these variables can be used to override defaults:

| Variable | Description | Default |
|----------|-------------|---------|
| `TEST_GCP_PROJECT_ID` | Test project ID | `test-project` |
| `TEST_GEMINI_MODEL_NAME` | Test model name | `models/gemini-2.5-flash-preview-05-20` |
| `TEST_API_KEY` | Test API key | `test-api-key` |
| `TEST_ELEVENLABS_API_KEY` | Test ElevenLabs key | `test-elevenlabs-key` |
| `TEST_JWT_SECRET_KEY` | Test JWT secret | `test-jwt-secret-key-minimum-32-chars` |
| `TEST_CORS_ORIGINS` | Test CORS origins | `http://localhost:3000,http://localhost:5173` |
| `TEST_WORKER_URL` | Test worker URL | `https://test-worker.example.com` |

## E2E Test Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `E2E_BASE_URL` | Base URL for E2E tests | `http://localhost:8080` |
| `E2E_API_KEY` | API key for E2E tests | `test-api-key-e2e` |
| `E2E_TIMEOUT` | Request timeout for E2E tests | `30` |
| `E2E_RETRY_ATTEMPTS` | Retry attempts for E2E tests | `3` |

## Configuration Priority

Settings are loaded in the following order (highest to lowest priority):

1. **Google Secret Manager** (if `GCP_PROJECT_ID` is set)
2. **Environment Variables**
3. **`.env` file**
4. **Default values**

## Secret Manager Setup

For production deployments, sensitive values should be stored in Google Secret Manager:

```bash
# Create secrets
echo "your-api-key" | gcloud secrets versions add AI_CONTENT_FACTORY_API_KEY --data-file=-
echo "your-elevenlabs-key" | gcloud secrets versions add AI_CONTENT_FACTORY_ELEVENLABS_KEY --data-file=-
openssl rand -hex 32 | gcloud secrets versions add AI_CONTENT_FACTORY_JWT_SECRET_KEY --data-file=-
```

## Environment File Template

Create a `.env` file in the project root:

```bash
# Copy and customize this template
GCP_PROJECT_ID=your-gcp-project-id
API_KEY=your-application-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
JWT_SECRET_KEY=your-jwt-secret-key-minimum-32-characters-long
GEMINI_MODEL_NAME=models/gemini-2.5-flash-preview-05-20
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000
```

## Validation

The application validates all configuration on startup and will fail with descriptive error messages if required settings are missing or invalid.

Common validation errors:
- `JWT_SECRET_KEY` must be at least 32 characters
- `GEMINI_MODEL_NAME` must match the supported model pattern
- `GCP_PROJECT_ID` must follow GCP naming conventions
- API keys must not be empty
