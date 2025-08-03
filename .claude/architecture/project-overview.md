# La Factoria: Complete Project Architecture Overview

**Single Source of Truth for La Factoria Educational Content Generation Platform**

---

## 🎯 Executive Summary

La Factoria is an AI-powered educational content generation platform that transforms textual input into comprehensive educational materials. The system generates 8 different content types from a master outline, creating cohesive educational experiences.

**Architecture Philosophy**: Simple implementation with comprehensive AI context
- **Codebase**: <1500 lines, Railway deployment, minimal dependencies
- **Context System**: Full `.claude/` directory with all domain knowledge for optimal AI assistance

---

## 🏗️ System Architecture

### High-Level Architecture

```mermaid
graph TB
    UI[React Frontend] --> API[FastAPI Backend]
    API --> AI[AI Content Service]
    API --> DB[(Railway Postgres)]
    AI --> VERTEX[Vertex AI]
    AI --> OPENAI[OpenAI]
    AI --> ANTHROPIC[Anthropic]
    AI --> PROMPTS[Prompt Templates]
    API --> QUALITY[Quality Assessment]
    API --> EXPORT[Export Service]
```

### Component Breakdown

#### 1. Frontend Layer (React + TypeScript)
- **Purpose**: User interface for content generation requests and management
- **Technology**: React with TypeScript, Vite build system, simple CSS styling
- **Key Components**:
  - Content generation forms (8 content types)
  - Generated content display and management
  - User authentication and API key management
  - Export functionality interface

#### 2. API Layer (FastAPI)
- **Purpose**: RESTful API for content generation and management
- **Technology**: FastAPI with Python 3.11+, Pydantic for validation
- **Key Endpoints**:
  - `POST /api/v1/generate` - Generate educational content
  - `GET /api/v1/content-types` - List available content types
  - `GET /api/v1/content/{id}` - Retrieve generated content
  - `DELETE /api/v1/user/{id}` - GDPR-compliant user deletion
  - `GET /health` - Health check and monitoring

#### 3. AI Content Service
- **Purpose**: Orchestrate AI models for educational content generation
- **Technology**: Multi-provider integration (OpenAI, Anthropic, Vertex AI)
- **Key Features**:
  - Prompt template management and formatting
  - Multi-provider failover and load balancing
  - Content quality assessment and validation
  - Token usage tracking and optimization

#### 4. Database Layer (Railway Postgres)
- **Purpose**: Persistent storage for users, content, and metadata
- **Technology**: PostgreSQL managed by Railway
- **Key Tables**:
  - `users` - User accounts and API keys
  - `content` - Generated educational content with metadata
  - `quality_scores` - Content quality assessment results
  - `usage_analytics` - Generation statistics and performance metrics

#### 5. Quality Assessment System
- **Purpose**: Ensure educational content meets pedagogical standards
- **Technology**: Python-based assessment algorithms
- **Quality Metrics**:
  - Educational value (≥0.75 threshold)
  - Factual accuracy (≥0.85 threshold)
  - Age appropriateness (target audience alignment)
  - Structural clarity and organization
  - Overall quality score (≥0.70 minimum)

---

## 📚 Educational Content System

### Content Types (8 Total)

1. **Master Content Outline**
   - Foundation structure with learning objectives
   - Follows Bloom's taxonomy principles
   - Provides scaffolding for other content types

2. **Podcast Script**
   - Conversational audio content with speaker notes
   - Includes timing and production guidance
   - Integrates with ElevenLabs for audio generation

3. **Study Guide**
   - Comprehensive educational material with key concepts
   - Interactive exercises and practice problems
   - Assessment questions and rubrics

4. **One-Pager Summary**
   - Concise overview with essential takeaways
   - Visual hierarchy and clear information design
   - Quick reference format

5. **Detailed Reading Material**
   - In-depth content with examples and exercises
   - Extended explanations and context
   - Progressive difficulty structure

6. **FAQ Collection**
   - Question-answer pairs covering common topics
   - Anticipates student questions and concerns
   - Supports different learning styles

7. **Flashcards**
   - Term-definition pairs for memorization and review
   - Spaced repetition optimization
   - Multiple difficulty levels

8. **Reading Guide Questions**
   - Discussion questions for comprehension
   - Critical thinking prompts
   - Group activity suggestions

### Content Generation Workflow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AI_Service
    participant Quality
    participant DB

    User->>Frontend: Submit content request
    Frontend->>API: POST /api/v1/generate
    API->>AI_Service: Generate content
    AI_Service->>AI_Service: Load prompt template
    AI_Service->>AI_Service: Format with context
    AI_Service->>AI_Service: Call AI provider
    AI_Service->>Quality: Assess content quality
    Quality->>AI_Service: Return quality score
    AI_Service->>API: Return generated content
    API->>DB: Store content and metadata
    API->>Frontend: Return success response
    Frontend->>User: Display generated content
```

---

## 🤖 AI Integration Architecture

### Multi-Provider Strategy

**Primary Providers**:
- **OpenAI GPT-4**: High-quality content generation
- **Anthropic Claude**: Educational content specialization
- **Google Vertex AI**: Cost-effective scaling option

**Provider Selection Logic**:
1. Content type optimization (Claude for educational content)
2. Cost optimization (Vertex AI for bulk generation)
3. Quality requirements (GPT-4 for complex content)
4. Failover and redundancy

### Prompt Engineering System

**Template Structure**:
```
System Context + Educational Framework + Specific Instructions + Quality Requirements + Output Format
```

**Template Management**:
- Stored in `la-factoria/prompts/` directory
- Version controlled and tested
- Optimized for token efficiency (20-40% reduction)
- Educational standards compliance built-in

**Quality Assessment Integration**:
- Real-time content evaluation
- Multi-dimensional scoring (educational value, accuracy, appropriateness)
- Automatic regeneration for below-threshold content
- Learning feedback loop for prompt optimization

---

## 🚀 Deployment Architecture

### Railway Platform Strategy

**Infrastructure Components**:
- **Application Server**: Railway-managed container deployment
- **Database**: Railway Postgres with automatic backups
- **Domain**: Railway-provided HTTPS domain with custom domain option
- **Monitoring**: Built-in Railway metrics and logging
- **Secrets Management**: Railway environment variables

**Deployment Pipeline**:
1. Git push to main branch
2. Railway automatic build and deploy
3. Health check verification
4. Traffic routing to new version
5. Monitoring and alerting

### Environment Configuration

**Development Environment**:
- Local FastAPI development server
- SQLite for local database
- Mock AI providers for testing
- Hot reload and debugging enabled

**Production Environment**:
- Railway container deployment
- Railway Postgres database
- Full AI provider integration
- Performance monitoring and logging

---

## 🔒 Security & Compliance

### Authentication & Authorization

**API Key Authentication**:
- Bearer token-based authentication
- API keys stored securely in Railway Postgres
- Rate limiting and usage tracking
- Key rotation and revocation support

**Data Protection**:
- HTTPS enforced (Railway automatic)
- Input validation and sanitization
- No PII storage in generated content
- Secure secret management

### GDPR Compliance

**User Data Deletion**:
- `DELETE /api/v1/user/{id}` endpoint
- Cascade deletion of all user content
- Audit logging for compliance
- 30-day deletion verification

**Data Minimization**:
- No unnecessary personal data collection
- Content anonymization where possible
- Opt-in data usage policies
- Clear privacy documentation

---

## 📊 Monitoring & Analytics

### Performance Metrics

**Application Performance**:
- Response time monitoring (<200ms target)
- Error rate tracking (<1% target)
- Uptime monitoring (99%+ target)
- Resource utilization (CPU, memory, database)

**Content Generation Metrics**:
- Generation success rate
- Quality score distribution
- AI provider performance comparison
- Token usage and cost optimization

**User Experience Metrics**:
- Content type popularity
- User satisfaction scores
- Feature usage analytics
- Support request categorization

### Alerting & Incident Response

**Critical Alerts**:
- API downtime or high error rates
- Database connection failures
- AI provider service interruptions
- Quality score degradation

**Response Procedures**:
- Automated health checks and recovery
- Provider failover mechanisms
- Escalation procedures for critical issues
- Post-incident analysis and improvement

---

## 🎓 Educational Quality Framework

### Learning Science Integration

**Pedagogical Principles**:
- Bloom's taxonomy for learning objectives
- Spaced repetition for memory retention
- Multiple learning modalities support
- Progressive difficulty scaffolding

**Content Standards**:
- Age-appropriate language and complexity
- Factual accuracy verification
- Cultural sensitivity and inclusivity
- Accessibility compliance (WCAG guidelines)

### Quality Assurance Process

**Multi-Stage Validation**:
1. **AI Generation**: Content created using optimized prompts
2. **Automated Assessment**: Quality scoring algorithms
3. **Educational Review**: Pedagogical effectiveness evaluation
4. **User Feedback**: Continuous improvement through usage data

**Quality Metrics Dashboard**:
- Real-time quality score monitoring
- Content type performance comparison
- User satisfaction trends
- Educational effectiveness indicators

---

## 🔄 Development Workflow

### Code Organization

**Backend Structure**:
```
app/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models and database schemas
├── content_service.py   # AI content generation orchestration
├── quality_assessment.py # Educational content validation
├── database.py          # Database connection and operations
└── auth.py              # Authentication and authorization
```

**Frontend Structure**:
```
src/
├── components/          # React components
│   ├── ContentForm.tsx  # Content generation forms
│   ├── ContentDisplay.tsx # Generated content presentation
│   └── Dashboard.tsx    # User dashboard and management
├── services/            # API integration and utilities
├── types/               # TypeScript type definitions
└── App.tsx              # Main application component
```

### Testing Strategy

**Backend Testing**:
- Unit tests for all business logic
- Integration tests for AI services
- API endpoint testing with pytest
- Quality assessment algorithm validation

**Frontend Testing**:
- Component testing with React Testing Library
- Integration testing for user workflows
- E2E testing for critical paths
- Accessibility testing compliance

**Quality Assurance**:
- Pre-commit hooks for code quality
- Automated security scanning
- Performance testing and benchmarking
- Educational content validation testing

---

## 📋 Implementation Roadmap

### Phase 1: Core Foundation (Weeks 1-2)
1. FastAPI backend with basic content generation
2. React frontend with content forms
3. AI service integration (single provider)
4. Railway deployment and basic monitoring

### Phase 2: Educational Quality (Weeks 3-4)
1. Quality assessment system implementation
2. All 8 content types support
3. Educational standards validation
4. User feedback and iteration system

### Phase 3: Production Features (Weeks 5-6)
1. Multi-provider AI integration
2. Advanced monitoring and analytics
3. Export functionality and sharing
4. Performance optimization and scaling

### Phase 4: Enhancement & Growth (Weeks 7-8)
1. Audio generation (ElevenLabs integration)
2. Advanced personalization features
3. Batch processing capabilities
4. API documentation and developer tools

---

## 🎯 Success Criteria

### Technical Success Metrics
- **Response Time**: <200ms average API response
- **Uptime**: 99%+ availability
- **Quality Score**: >0.70 average for all generated content
- **Cost Efficiency**: <$0.50 per content generation

### Educational Success Metrics
- **Content Quality**: >0.75 educational value score
- **User Satisfaction**: >4.0/5.0 user rating
- **Learning Effectiveness**: Measurable learning outcomes
- **Accessibility**: WCAG 2.1 AA compliance

### Business Success Metrics
- **User Growth**: Sustainable user acquisition
- **Content Generation Volume**: Scalable content production
- **Cost Management**: Predictable operational costs
- **Market Validation**: Product-market fit indicators

---

*This architecture overview serves as the definitive reference for all La Factoria development decisions and provides comprehensive context for AI-assisted development using Claude Code.*