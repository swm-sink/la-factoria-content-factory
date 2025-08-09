# Technical Domain Context

**Domain Focus**: Technology stack, infrastructure, and implementation patterns for La Factoria's simple yet robust architecture.

## Context Imports (Anthropic-Compliant)

### Claude Code Integration
@.claude/context/claude-code.md
@.claude/context/claude-code/README.md

### Backend Development
@.claude/context/fastapi.md
@.claude/examples/backend/fastapi-setup/main.py
@.claude/prp/PRP-002-Backend-API-Architecture.md

### Frontend Development  
@static/index.html
@.claude/prp/PRP-003-Frontend-User-Interface.md

### Infrastructure & Deployment
@.claude/context/railway.md
@.claude/prp/PRP-005-Deployment-Operations.md
@.claude/domains/operations/README.md

### Educational Integration
@.claude/context/la-factoria-educational-schema.md
@.claude/components/la-factoria/educational-standards.md

## 🧭 Claude Code Integration

**Primary Development Tool**: Complete AI-assisted development patterns specifically optimized for La Factoria's technical stack.

### Essential Workflows
```bash
# Initialize technical development context
claude /init

# Technical-specific context building  
claude "# Use FastAPI with Railway, React with TypeScript"

# Backend development workflow
claude "Implement educational content API following established patterns"
```

## 🔧 Domain Contents

### Backend Architecture (FastAPI)
- **Application Structure**: Minimal yet complete FastAPI application patterns
- **API Design**: RESTful endpoints for educational content generation and management
- **Data Models**: Pydantic schemas for validation and type safety
- **Authentication**: API key-based authentication and authorization patterns
- **Database Integration**: Railway Postgres integration and data persistence

### Frontend Architecture (Vanilla HTML/CSS/JavaScript)
- **Static File Serving**: FastAPI serves HTML directly from `/static/` directory
- **Client-Side Scripting**: ES6 JavaScript with local state management and localStorage
- **Form Handling**: Native HTML forms with JavaScript validation and API integration
- **Styling Approach**: Simple CSS3 styling without build tools or frameworks
- **Architecture**: Single-page application pattern with vanilla JavaScript

### Database Design
- **Schema Design**: Optimized for educational content storage and retrieval
- **Railway Postgres**: Managed database service integration patterns
- **Data Relationships**: User content, quality scores, and analytics relationships
- **Performance Optimization**: Indexing and query optimization for content operations
- **GDPR Compliance**: Data deletion and privacy-compliant storage patterns

### Development Workflow
- **Code Organization**: Comprehensive project structure (18,003 lines total: 16,811 Python + 1,192 frontend)
- **Testing Strategy**: pytest for backend, vanilla JavaScript testing for frontend
- **Quality Assurance**: Pre-commit hooks, linting, and automated testing
- **Version Control**: Git workflows and atomic commit patterns
- **Documentation**: Code documentation and API specification standards

## 🏗️ Implementation Philosophy

### Comprehensive Implementation Principle
Following the "comprehensive implementation, extensive context" philosophy:

- **Production Dependencies**: Full-featured dependency stack for production-ready platform
- **Railway Deployment**: Zero-configuration deployment and scaling with production readiness
- **Robust Architecture**: Well-structured, scalable code patterns with service layer design
- **Production Ready**: Comprehensive implementation suitable for real users and scaling

### Technology Choices Rationale

#### Backend: FastAPI
- **Fast Development**: Automatic API documentation and validation
- **Type Safety**: Python type hints and Pydantic integration
- **Performance**: High-performance async capabilities for AI integration
- **Ecosystem**: Rich ecosystem for AI service integration

#### Frontend: Vanilla HTML/CSS/JavaScript
- **Simplicity**: Direct HTML/CSS/JS without build complexity or dependencies
- **Performance**: Fast loading with no framework overhead for content display
- **Maintainability**: Straightforward code patterns easy to understand and modify
- **Deployment**: Static files served directly by FastAPI with zero build process

#### Database: Railway Postgres
- **Managed Service**: Zero-configuration database management
- **Reliability**: Automatic backups and high availability
- **Scaling**: Seamless scaling as user base grows
- **Cost Efficiency**: Predictable pricing for sustainable operations

## 🔗 Integration Patterns

### API Integration Architecture
```
Frontend (Vanilla JS) → FastAPI Backend → AI Services
                              ↓
                      Railway Postgres
```

### Content Generation Flow
1. **User Request**: Frontend form submission with content parameters
2. **API Validation**: FastAPI endpoint validates request and authentication
3. **AI Orchestration**: Content service coordinates with AI providers
4. **Quality Assessment**: Educational quality evaluation and scoring
5. **Data Persistence**: Storage of content and metadata in PostgreSQL
6. **Response Delivery**: Structured response with content and quality metrics

### Error Handling Strategy
- **Graceful Degradation**: Fallback mechanisms for AI service failures
- **User-Friendly Errors**: Clear error messages for common issues
- **Monitoring Integration**: Error tracking and alerting for operational awareness
- **Recovery Mechanisms**: Automatic retry logic for transient failures

## 📊 Performance and Monitoring

### Performance Targets
- **API Response Time**: <200ms average for content generation requests
- **Frontend Load Time**: <2 seconds initial page load
- **Database Query Performance**: <50ms average query response time
- **Uptime Requirement**: 99%+ availability with minimal downtime

### Monitoring and Analytics
- **Application Performance**: Response times, error rates, and resource utilization
- **User Experience**: Content generation success rates and user satisfaction
- **Infrastructure Health**: Database performance, service availability, and scaling metrics
- **Cost Optimization**: Resource usage tracking and cost-per-generation metrics

## 🛡️ Security and Compliance

### Security Framework
- **HTTPS Enforcement**: Railway automatic SSL/TLS for all communications
- **API Authentication**: Bearer token authentication with rate limiting
- **Input Validation**: Comprehensive input sanitization and validation
- **Secret Management**: Secure handling of API keys and sensitive configuration

### Data Protection
- **Privacy by Design**: Minimal data collection and user privacy protection
- **GDPR Compliance**: User data deletion and consent management
- **Content Security**: Generated content sanitization and safety measures
- **Audit Logging**: Security event tracking and compliance reporting

## 🔄 Development Best Practices

### Code Quality Standards
- **Type Safety**: TypeScript frontend, Python type hints backend
- **Testing Coverage**: 80%+ test coverage for core functionality
- **Code Review**: Peer review process for all changes
- **Documentation**: Clear API documentation and code comments

### Deployment Strategy
- **Git-Based Deployment**: Automatic deployment from version control
- **Environment Management**: Clear separation of development and production
- **Health Checks**: Automated health verification and rollback capabilities
- **Zero-Downtime Updates**: Seamless deployment without service interruption

---

*This technical domain provides the implementation foundation for La Factoria, ensuring a simple yet robust architecture that supports educational excellence while maintaining operational efficiency and developer productivity.*