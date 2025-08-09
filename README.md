# La Factoria - Educational Content Generation Platform

An AI-powered educational content generation platform that transforms textual input into comprehensive educational materials. The system generates 8 different content types from a master outline, creating cohesive educational experiences including podcasts, study guides, flashcards, and more.

## 🎯 Core Mission

Transform topics/syllabi into structured educational content with high pedagogical value, leveraging advanced AI models and educational science principles.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (or use Railway managed database)
- API keys for AI providers (OpenAI, Anthropic, etc.)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd la-factoria

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database URL

# Initialize database
alembic upgrade head

# Run the application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the Application
- **Frontend Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **System Monitor**: http://localhost:8000/monitor.html

## 📚 Educational Content Types

La Factoria generates 8 specialized educational content types:

1. **Master Content Outline** - Foundation structure with learning objectives
2. **Podcast Script** - Conversational audio content with speaker notes  
3. **Study Guide** - Comprehensive educational material with key concepts
4. **One-Pager Summary** - Concise overview with essential takeaways
5. **Detailed Reading Material** - In-depth content with examples and exercises
6. **FAQ Collection** - Question-answer pairs covering common topics
7. **Flashcards** - Term-definition pairs for memorization and review
8. **Reading Guide Questions** - Discussion questions for comprehension

## 🏗️ Technology Stack

### Backend (✅ COMPLETE)
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: API key-based authentication
- **Infrastructure**: Railway deployment configured
- **Testing**: Comprehensive pytest test suite

### Frontend (✅ COMPLETE)
- **Framework**: Vanilla HTML/CSS/JavaScript
- **Styling**: Custom CSS (responsive design)
- **State Management**: Local storage and vanilla JS
- **API Integration**: Fetch-based communication with backend

### AI Integration (🔧 IN PROGRESS)
- **Multi-Provider Support**: OpenAI, Anthropic, Vertex AI
- **Prompt Management**: Langfuse integration
- **Quality Assessment**: Educational effectiveness metrics
- **Audio Generation**: ElevenLabs integration (planned)

### Infrastructure (✅ COMPLETE)
- **Deployment**: Railway platform
- **Database**: Railway PostgreSQL
- **Configuration**: Environment-based configuration
- **Monitoring**: Health checks and system monitoring

## 📊 Project Statistics

- **Total Codebase**: ~17,950 lines
  - Backend Python: 4,469 lines
  - Frontend (HTML/CSS/JS): 1,192 lines  
  - Test Suite: 6,917 lines
  - Documentation & Config: ~5,372 lines
- **Files**: 362 total files
- **Test Coverage**: Comprehensive test suite across all components
- **Dependencies**: 20 core production dependencies

## 🗂️ Project Structure

```
la-factoria/
├── src/                      # Backend FastAPI application
│   ├── api/routes/          # API endpoints (content generation, health, admin)
│   ├── core/                # Core utilities (auth, config, database)
│   ├── models/              # Pydantic data models
│   ├── services/            # Business logic (content generation, quality assessment)
│   └── main.py              # FastAPI application entry point
├── static/                   # Frontend assets
│   ├── index.html           # Main application interface
│   ├── monitor.html         # System monitoring dashboard
│   ├── css/style.css        # Application styling
│   └── js/app.js            # Frontend application logic
├── tests/                    # Comprehensive test suite
│   ├── test_api_endpoints.py
│   ├── test_quality_assessment.py
│   ├── test_services.py
│   └── [additional test files]
├── prompts/                  # AI prompt templates (8 content types)
├── migrations/               # Database migrations
├── config/                   # Deployment configuration
│   └── railway.toml         # Railway deployment config
├── docs/                     # Documentation
└── requirements.txt          # Python dependencies
```

## 🔌 API Endpoints

### Content Generation
- `POST /api/content/generate/{content_type}` - Generate specific content type
- `GET /api/content/types` - List available content types
- `GET /api/content/{content_id}` - Retrieve generated content

### System
- `GET /health` - Health check endpoint
- `GET /api/monitoring/stats` - System statistics
- `DELETE /api/user/{user_id}` - GDPR-compliant user deletion

### Administration
- `GET /api/admin/status` - Administrative status
- `POST /api/admin/migrate` - Database migrations

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test categories
pytest tests/test_api_endpoints.py
pytest tests/test_quality_assessment.py
pytest tests/test_services.py
```

## 🚀 Deployment

### Railway Deployment (Recommended)

The application is configured for Railway deployment with automatic builds:

```bash
# Deploy to Railway
railway up

# Set environment variables in Railway dashboard:
# - DATABASE_URL (Railway Postgres)
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
# - LA_FACTORIA_API_KEY
# - SECRET_KEY
```

### Manual Deployment

```bash
# Build for production
pip install -r requirements.txt

# Run with production settings
uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1
```

## 🛡️ Security & Compliance

- **Authentication**: API key-based authentication system
- **GDPR Compliance**: User data deletion endpoints
- **Input Validation**: Comprehensive input sanitization
- **Security Headers**: HTTPS enforcement and security headers
- **Rate Limiting**: Request rate limiting per API key

## 📈 Quality Assessment

La Factoria includes sophisticated educational quality assessment:

- **Educational Value**: Pedagogical effectiveness (≥0.75 threshold)
- **Factual Accuracy**: Information reliability (≥0.85 threshold)  
- **Age Appropriateness**: Language and complexity validation
- **Structural Quality**: Organization and clarity assessment
- **Overall Quality**: Composite score (≥0.70 minimum)

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# AI Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_CLOUD_PROJECT=your_gcp_project

# Application
LA_FACTORIA_API_KEY=your_app_api_key
SECRET_KEY=your_secret_key
ENVIRONMENT=development

# Quality Thresholds
QUALITY_THRESHOLD_OVERALL=0.70
QUALITY_THRESHOLD_EDUCATIONAL=0.75
QUALITY_THRESHOLD_FACTUAL=0.85

# Optional: Prompt Management
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
```

## 🤝 Contributing

1. **Follow TDD Approach**: Write tests before implementation
2. **Maintain Quality**: All code must pass quality checks
3. **Document Changes**: Update documentation for new features
4. **Educational Focus**: Ensure all features serve educational effectiveness

### Development Guidelines

- **Code Standards**: Follow PEP 8 for Python, use type hints
- **Testing**: Maintain 80%+ test coverage
- **Documentation**: Clear docstrings and inline comments
- **Quality**: Educational content must meet quality thresholds

## 📄 License

MIT License - See LICENSE file for details.

## 🆘 Support

- **Documentation**: See `/docs` directory for detailed guides
- **Health Check**: Monitor system status at `/health`
- **System Monitor**: View real-time metrics at `/monitor.html`
- **API Documentation**: Interactive docs at `/docs`

---

**La Factoria** - Transforming education through AI-powered content generation with pedagogical excellence.