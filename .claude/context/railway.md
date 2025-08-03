# Railway Platform Context

## Platform Overview

### Core Features
- Cloud deployment platform supporting multiple languages and frameworks
- Quick deployment for various tech stacks (Next.js, Django, Rails, FastAPI, React)
- Pre-configured templates for popular applications
- Configuration as code approach
- Developer-friendly with emphasis on simplicity

### Key Capabilities
- **Multi-language Support**: Python, Node.js, Go, Ruby, Java, etc.
- **Database Services**: PostgreSQL, MySQL, MongoDB, Redis
- **Auto-deployment**: Git-based continuous deployment
- **Environment Management**: Multiple environments (dev, staging, production)
- **Monitoring**: Built-in logging and metrics
- **Networking**: Custom domains, load balancing, SSL certificates

## Deployment Process

### From Template
```bash
# 1. Choose template from Railway marketplace
# 2. Click "Deploy Now"  
# 3. Configure required variables
# 4. Click "Deploy"

# Template ejection (to create your own repo)
railway service:eject --repo-name my-app
```

### From Git Repository
```bash
# Initialize Railway project
railway login
railway init

# Link to existing service
railway link

# Deploy
railway up
```

### Configuration Files

#### railway.toml
```toml
[build]
  builder = "nixpacks"
  watchPatterns = ["**/*.py", "**/*.js", "**/*.ts"]

[environments.production]
  [environments.production.variables]
    NODE_ENV = "production"
    DATABASE_URL = "${{PostgreSQL.DATABASE_URL}}"

[environments.staging]
  [environments.staging.variables]
    NODE_ENV = "staging"
    DATABASE_URL = "${{PostgreSQL.DATABASE_URL}}"

[[services]]
  name = "backend"
  source = "src/"
  build = "pip install -r requirements.txt"
  start = "uvicorn main:app --host 0.0.0.0 --port $PORT"

[[services]]
  name = "frontend" 
  source = "frontend/"
  build = "npm install && npm run build"
  start = "npm start"
```

#### FastAPI Deployment
```python
# main.py
from fastapi import FastAPI
import os

app = FastAPI()

# Railway provides PORT environment variable
port = int(os.environ.get("PORT", 8000))

@app.get("/")
def read_root():
    return {"message": "Hello from Railway!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
psycopg2-binary==2.9.7
python-dotenv==1.0.0
langchain==0.0.340
openai==1.3.5
anthropic==0.5.0
langfuse==2.6.3
```

#### React Deployment
```json
{
  "name": "la-factoria-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "start": "vite preview --host 0.0.0.0 --port $PORT"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0"
  }
}
```

## Database Setup

### PostgreSQL Service
```bash
# Add PostgreSQL to project
railway add postgresql

# Get connection details
railway variables
```

### Database Configuration
```python
# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

# Handle Railway's postgres:// vs postgresql:// URL format
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Database Models
```python
# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    contents = relationship("Content", back_populates="user")

class Content(Base):
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content_type = Column(String, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="contents")
```

## Environment Variables

### Variable Management
```bash
# Set environment variables
railway variables set DATABASE_URL=$DATABASE_URL
railway variables set OPENAI_API_KEY=$OPENAI_API_KEY
railway variables set ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY

# View all variables
railway variables

# Set variables for specific environment
railway variables set --environment production REDIS_URL=$REDIS_URL
```

### Environment Configuration
```python
# config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
    
    # API Keys
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    
    # Langfuse
    langfuse_secret_key: str = os.environ.get("LANGFUSE_SECRET_KEY", "")
    langfuse_public_key: str = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    langfuse_host: str = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    # App Configuration
    debug: bool = os.environ.get("DEBUG", "False").lower() == "true"
    secret_key: str = os.environ.get("SECRET_KEY", "dev-secret-key")
    
    # Railway-specific
    port: int = int(os.environ.get("PORT", 8000))
    railway_environment: str = os.environ.get("RAILWAY_ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Monitoring and Logging

### Built-in Monitoring
```python
# logging_config.py
import logging
import os

def setup_logging():
    level = logging.DEBUG if os.environ.get("DEBUG") == "true" else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()  # Railway captures stdout/stderr
        ]
    )

# Usage in FastAPI
from fastapi import FastAPI
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response
```

### Health Checks
```python
# health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import os

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "unknown"),
        "service": "la-factoria-backend"
    }

@router.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    try:
        # Simple database query
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {str(e)}")

@router.get("/health/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    checks = {}
    
    # Database check
    try:
        db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # API keys check
    checks["openai_key"] = "configured" if os.environ.get("OPENAI_API_KEY") else "missing"
    checks["anthropic_key"] = "configured" if os.environ.get("ANTHROPIC_API_KEY") else "missing"
    
    return {
        "status": "healthy" if all(check == "healthy" or check == "configured" for check in checks.values()) else "degraded",
        "checks": checks,
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "unknown")
    }
```

## Networking and Domains

### Custom Domain Setup
```bash
# Add custom domain
railway domain add mydomain.com

# Generate SSL certificate (automatic)
railway ssl:generate mydomain.com
```

### CORS Configuration
```python
# cors.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Configure CORS for Railway deployment
allowed_origins = [
    "https://la-factoria-frontend.railway.app",
    "https://mydomain.com",
]

# Add localhost for development
if os.environ.get("RAILWAY_ENVIRONMENT") != "production":
    allowed_origins.extend([
        "http://localhost:3000",
        "http://localhost:5173"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Scaling and Performance

### Horizontal Scaling
```toml
# railway.toml
[[services]]
  name = "backend"
  replicas = 2  # Scale to 2 instances
  
  [services.resources]
    memory = "1Gi"
    cpu = "1000m"
```

### Caching with Redis
```bash
# Add Redis service
railway add redis
```

```python
# redis_client.py
import redis
import os
import json

redis_client = redis.from_url(
    os.environ.get("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

def cache_content(key: str, content: dict, expire_time: int = 3600):
    """Cache generated content."""
    redis_client.setex(key, expire_time, json.dumps(content))

def get_cached_content(key: str):
    """Retrieve cached content."""
    cached = redis_client.get(key)
    return json.loads(cached) if cached else None

def cache_key_for_content(topic: str, content_type: str, user_id: str) -> str:
    """Generate consistent cache key."""
    return f"content:{user_id}:{content_type}:{hash(topic)}"
```

## CI/CD and Git Integration

### Automatic Deployments
```bash
# Connect to GitHub repository
railway link

# Set up auto-deployment on push to main
railway environment production
railway service:deploy --source github
```

### Environment-based Deployments
```yaml
# .github/workflows/railway.yml
name: Deploy to Railway
on:
  push:
    branches: [main, staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Staging
        if: github.ref == 'refs/heads/staging'
        run: |
          curl -X POST "https://api.railway.app/v1/projects/$PROJECT_ID/environments/staging/deployments" \
          -H "Authorization: Bearer $RAILWAY_TOKEN" \
          -H "Content-Type: application/json"
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
          PROJECT_ID: ${{ secrets.PROJECT_ID }}
          
      - name: Deploy to Production
        if: github.ref == 'refs/heads/main'
        run: |
          curl -X POST "https://api.railway.app/v1/projects/$PROJECT_ID/environments/production/deployments" \
          -H "Authorization: Bearer $RAILWAY_TOKEN" \
          -H "Content-Type: application/json"
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
          PROJECT_ID: ${{ secrets.PROJECT_ID }}
```

## Cost Optimization

### Resource Management
```toml
# railway.toml - Cost-optimized configuration
[[services]]
  name = "backend"
  
  [services.resources]
    memory = "512Mi"  # Start small
    cpu = "500m"      # 0.5 CPU
  
  [services.scaling]
    min_replicas = 1
    max_replicas = 3
    target_cpu = 70   # Scale when CPU > 70%
```

### Database Connection Pooling
```python
# database.py - Optimized for Railway
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,  # Small pool for cost optimization
    max_overflow=10,
    pool_recycle=3600,  # 1 hour
    pool_pre_ping=True,  # Verify connections
)
```

## Migration and Best Practices

### Database Migrations
```python
# alembic_config.py
from alembic.config import Config
from alembic import command
import os

def run_migrations():
    """Run database migrations on Railway startup."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", os.environ.get("DATABASE_URL"))
    command.upgrade(alembic_cfg, "head")

# In main.py
@app.on_event("startup")
async def startup_event():
    if os.environ.get("RAILWAY_ENVIRONMENT") == "production":
        run_migrations()
```

### Security Best Practices
```python
# security.py
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer
import os

security = HTTPBearer()

def verify_api_key(credentials = Security(security)):
    """Verify API key for Railway deployment."""
    expected_key = os.environ.get("API_SECRET_KEY")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured"
        )
    
    if credentials.credentials != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials
```

### Monitoring Integration
```python
# monitoring.py
import os
import httpx
from datetime import datetime

class RailwayMonitoring:
    def __init__(self):
        self.webhook_url = os.environ.get("WEBHOOK_URL")
        self.service_name = os.environ.get("RAILWAY_SERVICE_NAME", "la-factoria")
    
    async def send_alert(self, message: str, level: str = "info"):
        """Send alert to monitoring service."""
        if not self.webhook_url:
            return
        
        payload = {
            "service": self.service_name,
            "environment": os.environ.get("RAILWAY_ENVIRONMENT"),
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(self.webhook_url, json=payload)
            except Exception as e:
                print(f"Failed to send alert: {e}")
```

## Sources
21. Railway Platform Documentation
22. Railway Deployment and Template Guides
23. Railway Database and Environment Configuration
24. Railway Scaling and Performance Optimization
25. Railway Security and Monitoring Best Practices