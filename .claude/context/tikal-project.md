# Tikal AI Content Generation Platform Context

## Project Overview
Tikal is a production-ready AI-powered educational content generation platform that creates high-quality educational materials using advanced AI models.

## Architecture Summary
- **Backend**: FastAPI with Python 3.11+
- **Frontend**: React + TypeScript with Vite
- **AI Integration**: Google Vertex AI (Gemini models)
- **Database**: Firestore for persistence
- **Infrastructure**: Google Cloud Platform with Terraform
- **Audio Generation**: ElevenLabs integration
- **Caching**: Redis for content and performance optimization

## Content Generation Pipeline
Tikal supports 8 content types generated from a master outline:

1. **Master Content Outline** (`master_content_outline.md`)
   - Foundation structure with learning objectives
   - Sections with key points and estimated duration

2. **Podcast Script** (`podcast_script.md`)
   - Conversational format with speaker notes
   - Introduction, main content, and conclusion

3. **Study Guide** (`study_guide.md`) 
   - Comprehensive educational content
   - Key concepts with detailed explanations

4. **One-Pager Summary** (`one_pager_summary.md`)
   - Concise overview with key takeaways
   - Limited length with high information density

5. **Detailed Reading Material** (`detailed_reading_material.md`)
   - In-depth educational content
   - Examples, exercises, and comprehensive coverage

6. **FAQ Collection** (`faq_collection.md`)
   - Question-answer pairs covering common topics
   - Educational focus with clear explanations

7. **Flashcards** (`flashcards.md`)
   - Term-definition pairs for memorization
   - Concise and memorable format

8. **Reading Guide Questions** (`reading_guide_questions.md`)
   - Discussion questions for comprehension
   - Critical thinking and analysis focus

## Current Service Architecture

### Core Services (`/app/services/`)
- **ContentGenerationService**: Main content generation orchestration
- **UnifiedContentService**: Production-ready simplified service
- **MultiStepContentService**: Complex multi-step generation
- **PromptService**: Template management from markdown files
- **QualityMetricsService**: Content quality evaluation
- **AudioGenerationService**: ElevenLabs TTS integration
- **JobManager**: Asynchronous job lifecycle management

### API Endpoints (`/app/api/routes/`)
- `/api/v1/content/generate`: Synchronous content generation
- `/api/v1/jobs/{job_id}`: Job status and result retrieval
- `/api/v1/feedback/`: User feedback submission
- `/api/v1/auth/*`: User authentication endpoints

## Quality Validation System
- **Structural Validation**: JSON schema compliance
- **Content Quality**: Readability scores, engagement metrics  
- **Comprehensive Validation**: Semantic consistency checks
- **Quality Thresholds**: Configurable quality requirements

## Current Pain Points
1. **Static Prompts**: Hardcoded templates with limited flexibility
2. **Manual Optimization**: Prompt improvements require code changes
3. **Inconsistent Quality**: Variable content quality across types
4. **Limited Context**: Basic context handling without optimization
5. **Maintenance Overhead**: Prompt updates require deployments

## Development Standards
- **Python**: FastAPI patterns, PEP 8, type hints, Pydantic models
- **Testing**: pytest with >95% coverage, unit/integration/E2E tests
- **Quality**: black, flake8, mypy for code quality
- **Documentation**: Comprehensive docstrings and API documentation
- **Security**: Input validation, secret management, rate limiting

## File Locations
- **Prompts**: `app/core/prompts/v1/*.md`
- **Services**: `app/services/*.py`
- **Models**: `app/models/pydantic/*.py`
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/e2e/`
- **Infrastructure**: `iac/` (Terraform configurations)
- **Frontend**: `frontend/src/` (React components and pages)

## Key Metrics
- **Response Time**: Currently ~5.2s average
- **Quality Score**: 0.72 average (target: >0.8)
- **Token Efficiency**: Baseline measurement needed
- **Content Types**: 8 supported formats
- **Success Rate**: >95% content generation success

## Integration Points
- **Google Cloud**: Vertex AI, Firestore, Cloud Tasks, Secret Manager
- **External APIs**: ElevenLabs for audio generation
- **Monitoring**: Prometheus metrics, structured logging
- **Caching**: Redis for content and template caching

This context provides essential information for understanding Tikal's architecture, capabilities, and optimization opportunities when working with commands and prompts.