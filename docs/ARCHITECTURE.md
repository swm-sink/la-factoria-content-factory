# AI Content Factory - Architecture Documentation

## Project Structure

The AI Content Factory follows a modern, modular architecture designed for scalability, maintainability, and clear separation of concerns.

```
ai-content-factory/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Application entry point
│   ├── api/                     # API layer
│   │   ├── __init__.py
│   │   └── routes.py            # API route definitions
│   ├── core/                    # Core application components
│   │   ├── __init__.py
│   │   ├── config/              # Configuration management
│   │   │   ├── __init__.py
│   │   │   └── settings.py      # Application settings
│   │   ├── exceptions/          # Custom exceptions
│   │   │   └── __init__.py
│   │   └── prompts/             # AI prompt templates
│   │       ├── __init__.py
│   │       └── v1/              # Version 1 prompts
│   │           ├── __init__.py
│   │           ├── content_generation.py
│   │           └── multi_step_prompts.py
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   └── content_version.py   # Content versioning models
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── audio_generation.py  # Audio generation service
│   │   ├── content_cache.py     # Content caching service
│   │   ├── content_generation.py # Content generation service
│   │   ├── multi_step_content_generation.py # Enhanced content service
│   │   ├── parallel_processor.py # Parallel processing service
│   │   ├── progress_tracker.py  # Progress tracking service
│   │   └── quality_metrics.py   # Quality evaluation service
│   └── utils/                   # Utility functions
│       └── __init__.py
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_app.py
│   │   └── test_elevenlabs.py
│   ├── integration/             # Integration tests
│   │   └── __init__.py
│   └── e2e/                     # End-to-end tests
│       └── __init__.py
├── scripts/                     # Utility scripts
│   └── debug_import.py
├── docs/                        # Documentation
│   ├── api/                     # API documentation
│   ├── user/                    # User guides
│   └── developer/               # Developer documentation
├── deployment/                  # Deployment configurations
│   ├── docker/                  # Docker configurations
│   ├── k8s/                     # Kubernetes manifests
│   └── terraform/               # Infrastructure as Code
├── .cursor/                     # Cursor IDE configuration
│   └── rules/
├── .vscode/                     # VS Code configuration
├── requirements.txt             # Python dependencies
├── tasks.md                     # Project task tracker
└── README.md                    # Project overview
```

## Architecture Principles

### 1. **Separation of Concerns**
- **API Layer** (`app/api/`): Handles HTTP requests and responses
- **Business Logic** (`app/services/`): Contains core application logic
- **Data Models** (`app/models/`): Defines data structures and relationships
- **Configuration** (`app/core/config/`): Manages application settings
- **Prompts** (`app/core/prompts/`): AI prompt templates with versioning

### 2. **Modular Design**
- Each service is self-contained with clear interfaces
- Services can be easily tested, replaced, or extended
- Dependency injection for better testability

### 3. **Scalability**
- Parallel processing capabilities
- Caching layer for performance
- Progress tracking for long-running operations
- Quality metrics for content evaluation

### 4. **Maintainability**
- Clear naming conventions
- Comprehensive documentation
- Version control for prompts
- Structured testing approach

## Key Components

### Services Layer
- **ContentGenerationService**: Basic content generation using Gemini
- **EnhancedMultiStepContentGenerationService**: Advanced multi-step content generation
- **AudioGenerationService**: Text-to-speech conversion using ElevenLabs
- **ContentCacheService**: LRU caching with TTL support
- **ProgressTracker**: Real-time progress monitoring
- **ParallelProcessor**: Concurrent task execution
- **QualityMetricsService**: Content quality evaluation

### Models Layer
- **ContentVersion**: Version control for generated content
- **ContentVersionManager**: Manages content versions and history

### Core Components
- **Settings**: Environment-based configuration management
- **Prompts**: Versioned AI prompt templates

## Development Guidelines

### Adding New Features
1. Create services in `app/services/`
2. Add models in `app/models/`
3. Update API routes in `app/api/routes.py`
4. Add tests in appropriate test directories
5. Update documentation

### Testing Strategy
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user workflows

### Configuration Management
- Use environment variables for configuration
- Validate settings on application startup
- Support different environments (dev, staging, prod)

## Deployment Architecture

The application is designed to be deployed as:
- **Container**: Docker-based deployment
- **Kubernetes**: Scalable orchestration
- **Cloud Run**: Serverless deployment option
- **Infrastructure**: Terraform for IaC

This architecture supports horizontal scaling, monitoring, and observability while maintaining code quality and developer productivity. 