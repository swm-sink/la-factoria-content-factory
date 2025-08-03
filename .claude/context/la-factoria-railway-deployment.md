# La Factoria Railway Deployment Context

## Educational Platform Specific Railway Configuration

### railway.toml for La Factoria
```toml
[build]
  builder = "nixpacks"
  watchPatterns = ["**/*.py", "requirements.txt", "pyproject.toml"]

[deploy]
  healthcheckPath = "/health"
  healthcheckTimeout = 60
  restartPolicyType = "ON_FAILURE"

[environments.production]
  [environments.production.variables]
    ENVIRONMENT = "production"
    LA_FACTORIA_API_KEY = "${{LA_FACTORIA_API_KEY}}"
    DATABASE_URL = "${{Postgres.DATABASE_URL}}"
    LANGFUSE_SECRET_KEY = "${{LANGFUSE_SECRET_KEY}}"
    LANGFUSE_PUBLIC_KEY = "${{LANGFUSE_PUBLIC_KEY}}"
    LANGFUSE_HOST = "https://cloud.langfuse.com"
    OPENAI_API_KEY = "${{OPENAI_API_KEY}}"
    ANTHROPIC_API_KEY = "${{ANTHROPIC_API_KEY}}"
    ELEVENLABS_API_KEY = "${{ELEVENLABS_API_KEY}}"
    REDIS_URL = "${{Redis.REDIS_URL}}"

[environments.staging]
  [environments.staging.variables]
    ENVIRONMENT = "staging"
    LA_FACTORIA_API_KEY = "${{LA_FACTORIA_API_KEY_STAGING}}"
    DATABASE_URL = "${{Postgres_Staging.DATABASE_URL}}"
    LANGFUSE_SECRET_KEY = "${{LANGFUSE_SECRET_KEY_STAGING}}"
    LANGFUSE_PUBLIC_KEY = "${{LANGFUSE_PUBLIC_KEY_STAGING}}"
    
[[services]]
  name = "la-factoria-api"
  source = "."
  build = "pip install -r requirements.txt"
  start = "uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1"
  
  [services.healthcheck]
    path = "/health"
    interval = 30
    timeout = 10
    retries = 3

[[services]]
  name = "la-factoria-frontend"
  source = "static/"
  build = "echo 'Static files ready'"
  start = "python -m http.server $PORT"
```

### Environment Variables Template
```bash
# .env.template for La Factoria
# Educational Platform Configuration

# Core API Configuration
LA_FACTORIA_API_KEY=your_secure_api_key_here
ENVIRONMENT=development
DEBUG=true
PORT=8000

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/la_factoria
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# AI Provider Configuration
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Langfuse Configuration (Prompt Management)
LANGFUSE_SECRET_KEY=sk-lf-your_secret_key_here
LANGFUSE_PUBLIC_KEY=pk-lf-your_public_key_here
LANGFUSE_HOST=https://cloud.langfuse.com

# Educational Platform Specific
DEFAULT_AGE_GROUP=general
MAX_CONTENT_LENGTH=10000
MIN_QUALITY_SCORE=0.7
COGNITIVE_LOAD_THRESHOLD=0.8

# Caching Configuration
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=3600
ENABLE_CONTENT_CACHING=true

# Monitoring and Logging
LOG_LEVEL=INFO
ENABLE_LANGFUSE_TRACING=true
METRICS_ENABLED=true
SENTRY_DSN=your_sentry_dsn_here

# Rate Limiting (Educational Platform)
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000

# Content Generation Limits
MAX_CONCURRENT_GENERATIONS=5
GENERATION_TIMEOUT_SECONDS=180
MAX_TOKENS_PER_REQUEST=4000
```

### Railway-Optimized Dockerfile
```dockerfile
# Dockerfile optimized for Railway deployment
FROM python:3.11-slim

# Set environment variables for Railway
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Create app directory
WORKDIR /app

# Install system dependencies for educational platform
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash la_factoria
RUN chown -R la_factoria:la_factoria /app
USER la_factoria

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Expose port
EXPOSE $PORT

# Start application
CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1
```

### Railway Deployment Scripts

#### deploy.sh
```bash
#!/bin/bash
# La Factoria Railway deployment script

set -e

echo "🚀 Deploying La Factoria to Railway..."

# Check required environment variables
required_vars=(
    "LA_FACTORIA_API_KEY"
    "DATABASE_URL" 
    "LANGFUSE_SECRET_KEY"
    "OPENAI_API_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set"
        exit 1
    fi
done

# Run database migrations
echo "📊 Running database migrations..."
railway run alembic upgrade head

# Deploy to Railway
echo "🚢 Deploying to Railway..."
railway up

# Run health check
echo "🏥 Running health check..."
sleep 30
curl -f "$RAILWAY_STATIC_URL/health" || {
    echo "❌ Health check failed"
    exit 1
}

echo "✅ La Factoria deployed successfully!"
```

#### migrate.sh
```bash
#!/bin/bash
# Database migration script for Railway

echo "📊 Starting La Factoria database migration..."

# Check database connection
railway run python -c "
from src.database import async_engine
import asyncio

async def check_connection():
    async with async_engine.connect() as conn:
        await conn.execute('SELECT 1')
        print('Database connection successful')

asyncio.run(check_connection())
"

# Run migrations
echo "🔄 Running Alembic migrations..."
railway run alembic upgrade head

echo "✅ Database migration completed!"
```

### Railway Service Configuration

#### nixpacks.toml
```toml
# Nixpacks configuration for La Factoria
[variables]
    NIXPACKS_PYTHON_VERSION = "3.11"

[phases.setup]
    nixPkgs = ["python311", "postgresql"]

[phases.install]
    cmds = ["pip install -r requirements.txt"]

[phases.build]
    cmds = ["echo 'La Factoria build complete'"]

[start]
    cmd = "uvicorn src.main:app --host 0.0.0.0 --port $PORT"
```

### Railway Monitoring Setup

#### health_check.py
```python
# Health check endpoint for Railway
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from src.database import async_engine
import asyncio
import time

async def comprehensive_health_check():
    """Comprehensive health check for La Factoria educational platform"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Database check
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Educational content schema check
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'educational_content'
            """))
            count = result.scalar()
            if count > 0:
                health_status["checks"]["educational_schema"] = "healthy"
            else:
                health_status["checks"]["educational_schema"] = "missing"
                health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["educational_schema"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Langfuse connectivity check
    try:
        from src.integrations.langfuse_client import langfuse_client
        # Test Langfuse connection
        health_status["checks"]["langfuse"] = "healthy"
    except Exception as e:
        health_status["checks"]["langfuse"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # AI provider checks
    try:
        import openai
        import anthropic
        health_status["checks"]["ai_providers"] = "configured"
    except Exception as e:
        health_status["checks"]["ai_providers"] = f"missing: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/health")
async def health_endpoint():
    """Railway health check endpoint"""
    return await comprehensive_health_check()

@app.get("/health/ready")
async def readiness_check():
    """Kubernetes-style readiness check"""
    health = await comprehensive_health_check()
    if health["status"] == "healthy":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/health/live")
async def liveness_check():
    """Kubernetes-style liveness check"""
    return {"status": "alive", "timestamp": time.time()}
```

### Railway-Specific Performance Optimizations

#### railway_config.py
```python
# Railway-specific configuration for La Factoria
import os

class RailwayConfig:
    """Railway platform specific configuration"""
    
    # Railway environment detection
    IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") is not None
    ENVIRONMENT = os.getenv("RAILWAY_ENVIRONMENT", "development")
    
    # Railway-provided URLs
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    RAILWAY_STATIC_URL = os.getenv("RAILWAY_STATIC_URL")
    
    # Performance settings for Railway
    if IS_RAILWAY:
        # Optimize for Railway's container limits
        DB_POOL_SIZE = 5
        DB_MAX_OVERFLOW = 10
        WORKER_COUNT = 1
        WORKER_CLASS = "uvicorn.workers.UvicornWorker"
    else:
        # Local development settings
        DB_POOL_SIZE = 10
        DB_MAX_OVERFLOW = 20
        WORKER_COUNT = 4
        WORKER_CLASS = "uvicorn.workers.UvicornWorker"
    
    # Educational platform specific settings
    MAX_CONTENT_GENERATION_TIME = 180  # 3 minutes
    CONTENT_CACHE_TTL = 3600  # 1 hour
    ENABLE_EDUCATIONAL_METRICS = True
```

### Railway Database Setup Script
```python
# scripts/setup_railway_db.py
"""Initialize Railway PostgreSQL database for La Factoria"""

import asyncio
import os
from sqlalchemy import text
from src.database import async_engine
from src.models import Base

async def setup_railway_database():
    """Setup Railway PostgreSQL database with La Factoria schema"""
    
    print("🚀 Setting up Railway PostgreSQL for La Factoria...")
    
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Verify educational content table
    async with async_engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'educational_content'
        """))
        
        if result.fetchone():
            print("✅ Educational content table created successfully")
        else:
            print("❌ Failed to create educational content table")
            return False
    
    # Insert initial data
    async with async_engine.connect() as conn:
        await conn.execute(text("""
            INSERT INTO educational_content (
                content_type, topic, learning_objectives, 
                cognitive_load_metrics, generated_content
            ) VALUES (
                'master_content_outline',
                'Sample Educational Topic',
                '{"objectives": ["Learn", "Understand", "Apply"]}',
                '{"intrinsic_load": 0.5, "extraneous_load": 0.3, "germane_load": 0.7}',
                '{"title": "Sample Content", "sections": []}'
            )
        """))
        await conn.commit()
    
    print("✅ Railway database setup complete!")
    return True

if __name__ == "__main__":
    asyncio.run(setup_railway_database())
```