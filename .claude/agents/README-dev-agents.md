# La Factoria Development Agents Usage Guide

## 🎯 Complete Development Agent System

This guide covers the **development agents** for building La Factoria (different from the production content generation agents that will be deployed to LangChain).

### Agent Architecture Overview

**Important**: Agents are organized using `agent-[xxxx]-[xxxx]` naming convention for file organization, but invoked using shorter names in Claude Code (e.g., `@dev-orchestrator` not `@agent-dev-orchestrator`).

#### Core Workflow Agents (High Priority)
- `@dev-orchestrator` (file: agent-dev-orchestrator.md) - Master coordinator with meta prompt enhancement
- `@dev-explorer` (file: agent-dev-explorer.md) - Codebase discovery and analysis
- `@dev-planner` (file: agent-dev-planner.md) - Architecture planning and TDD task breakdown
- `@dev-implementer` (file: agent-dev-implementer.md) - Test-driven development specialist
- `@dev-validator` (file: agent-dev-validator.md) - Quality gates and compliance enforcement
- `@dev-deployer` (file: agent-dev-deployer.md) - Railway deployment orchestration

#### Specialized Technical Agents (Medium Priority)
- `@fastapi-dev` (file: agent-fastapi-dev.md) - Backend API development specialist
- `@frontend-dev` (file: agent-frontend-dev.md) - Vanilla JS frontend builder
- `@db-dev` (file: agent-db-dev.md) - Railway Postgres database designer
- `@security-dev` (file: agent-security-dev.md) - Security auditing and GDPR compliance
- `@perf-dev` (file: agent-perf-dev.md) - Performance monitoring and optimization

## 🚀 Quick Start: Complete Development Workflow

### 1. **Project Discovery and Planning**
```bash
# Start with project exploration
@dev-orchestrator "Analyze the current La Factoria codebase and create a comprehensive implementation plan for the simplification architecture following .claude/memory/simplification_plan.md"

# This will automatically use meta prompt enhancement to:
# 1. Coordinate @dev-explorer for codebase analysis
# 2. Coordinate @dev-planner for TDD task breakdown
# 3. Apply simplification constraints (≤200 lines per file, ≤20 dependencies)
# 4. Create quality gate checkpoints
```

### 2. **TDD Implementation Phase**
```bash
# Implement backend with TDD methodology
@dev-orchestrator "Implement the FastAPI backend for La Factoria following TDD red-green-refactor cycles. Ensure all code meets simplification constraints and quality standards."

# This coordinates:
# - @fastapi-dev for API implementation
# - @db-dev for database design
# - @dev-implementer for TDD methodology
# - @dev-validator for quality gates
```

### 3. **Frontend Development**
```bash
# Build vanilla JS frontend
@dev-orchestrator "Create the frontend interface for La Factoria using vanilla HTML, CSS, and JavaScript. Integrate with the FastAPI backend and ensure responsive design."

# This coordinates:
# - @frontend-dev for UI implementation
# - @perf-dev for performance optimization
# - @security-dev for frontend security
```

### 4. **Security and Performance Validation**
```bash
# Comprehensive security and performance audit
@dev-orchestrator "Conduct complete security audit and performance optimization for La Factoria. Ensure GDPR compliance and Railway deployment readiness."

# This coordinates:
# - @security-dev for security audit
# - @perf-dev for performance validation
# - @dev-validator for compliance checks
```

### 5. **Production Deployment**
```bash
# Deploy to Railway platform
@dev-orchestrator "Deploy La Factoria to Railway platform with full production configuration including monitoring, health checks, and environment management."

# This coordinates:
# - @dev-deployer for Railway deployment
# - @perf-dev for production monitoring
# - @security-dev for production security
```

## 🧠 Meta Prompt Enhancement System

The `@dev-orchestrator` automatically enhances all sub-agent instructions using meta prompts:

### Meta Prompt Pattern Examples

#### Enhanced Task Delegation
```bash
# Before: Basic instruction
@fastapi-dev "Build the backend API"

# After: Meta-enhanced instruction
@fastapi-dev "/meta-prompt-context La Factoria educational content platform with 8 content types targeting Railway deployment with strict simplification: ≤200 lines per file, ≤20 total dependencies.

/meta-prompt-standards Implement FastAPI backend with:
- TDD methodology (write tests first)
- 80% minimum test coverage
- Production-ready error handling
- Railway-optimized configuration
- Anthropic Claude integration for content generation

/meta-prompt-simplify Follow single-file architecture where possible:
- main.py (≤200 lines) - FastAPI app and endpoints
- models.py (≤50 lines) - Pydantic models
- content_service.py (≤100 lines) - AI integration

Build the core FastAPI backend for La Factoria educational content generation."
```

### Available Meta Prompt Commands

#### Context Enhancement
- `/meta-prompt-context` - Add La Factoria project context and constraints
- `/meta-prompt-educational` - Add educational content requirements
- `/meta-prompt-railway` - Add Railway platform optimization context

#### Standards Injection
- `/meta-prompt-standards` - Inject quality and compliance requirements
- `/meta-prompt-tdd` - Add test-driven development methodology
- `/meta-prompt-security` - Add security and GDPR requirements

#### Simplification Enforcement
- `/meta-prompt-simplify` - Apply simplification constraints
- `/meta-prompt-constraints` - Enforce file size and dependency limits
- `/meta-prompt-optimize` - Add performance optimization requirements

## 📋 Specific Agent Usage Patterns

### Core Development Workflow

#### Discovery and Analysis
```bash
# Comprehensive codebase analysis
@dev-explorer "Analyze the current La Factoria project structure, identify implementation gaps, and assess compliance with the simplification plan in .claude/memory/simplification_plan.md. Focus on file sizes, dependency count, and architecture alignment."

# Create implementation roadmap
@dev-planner "Using the explorer analysis, create a detailed TDD implementation plan for La Factoria simplification. Break down all features into test-first development tasks with clear acceptance criteria and quality gates."
```

#### TDD Implementation
```bash
# Backend development with TDD
@dev-implementer "Implement the FastAPI health check endpoint using TDD methodology. Write failing tests first, implement minimal code to pass tests, then refactor for quality. Ensure file size ≤200 lines and follow Railway optimization patterns."

# Quality validation
@dev-validator "Validate the health check implementation against quality gates: test coverage ≥80%, file size ≤200 lines, no security vulnerabilities, Railway deployment readiness."
```

#### Specialized Development
```bash
# Database schema design
@db-dev "Design the minimal PostgreSQL schema for La Factoria educational content storage. Focus on 5 core tables maximum, Railway Postgres optimization, and GDPR compliance with CASCADE deletion."

# Security implementation
@security-dev "Implement API key authentication with rate limiting for La Factoria. Include input validation, XSS prevention, SQL injection protection, and GDPR user data export/deletion capabilities."

# Performance optimization
@perf-dev "Implement performance monitoring for La Factoria with Railway-specific optimizations. Ensure ≤2s API response times, ≤1s frontend load times, and efficient resource usage within Railway constraints."
```

### Advanced Coordination Patterns

#### Multi-Agent Workflows
```bash
# Parallel development coordination
@dev-orchestrator "Coordinate parallel development of backend (@fastapi-dev + @db-dev) and frontend (@frontend-dev) while ensuring API contract compatibility and shared security standards (@security-dev)."

# Quality assurance pipeline
@dev-orchestrator "Establish continuous quality pipeline with @dev-validator running automated checks after each @dev-implementer cycle, feeding results back to @dev-planner for task refinement."
```

#### Integration Testing
```bash
# End-to-end integration
@dev-orchestrator "Conduct full integration testing across frontend, backend, database, and deployment layers. Validate complete user workflow from content request to generation and delivery."
```

## 🎯 Quality Standards Enforcement

### Simplification Compliance
- **File Size Limits**: ≤200 lines per file (strict enforcement)
- **Dependency Limits**: ≤20 total project dependencies
- **Total Code Size**: <1500 lines across entire project
- **Architecture**: Single-file implementations where possible

### Development Standards
- **TDD Methodology**: Tests written before implementation
- **Test Coverage**: ≥80% for all production code
- **Security Compliance**: ≥0.95 security score (no high/critical issues)
- **Performance**: ≤2s API response times, ≤1s frontend load

### Railway Optimization
- **Deploy Time**: ≤2 minutes from git push to live
- **Resource Usage**: Optimized for Railway hobby plan limits
- **Health Checks**: Comprehensive monitoring and alerting
- **Environment Management**: Proper secrets and configuration

## ⚡ Orchestrator Meta Prompt Patterns

### Project Initialization
```bash
@dev-orchestrator "/meta-prompt-optimize project-setup 'Initialize La Factoria development environment with complete tooling and agent coordination'

/meta-prompt-context Set up development environment for La Factoria educational content platform following simplification plan:
- Target: FastAPI backend + vanilla JS frontend
- Platform: Railway deployment
- Constraints: ≤200 lines per file, ≤20 dependencies, <1500 total lines
- Content: 8 educational content types with AI generation

/meta-prompt-standards Initialize with:
- TDD development methodology setup
- Quality gate automation (@dev-validator)
- Security scanning (@security-dev)
- Performance monitoring (@perf-dev)
- Railway deployment pipeline (@dev-deployer)

/meta-prompt-coordinate Agent workflow:
1. @dev-explorer - Project structure analysis
2. @dev-planner - TDD task breakdown
3. Specialized agents - Parallel development
4. @dev-validator - Continuous quality gates
5. @dev-deployer - Production deployment

Initialize complete La Factoria development environment with agent coordination."
```

### Feature Development
```bash
@dev-orchestrator "/meta-prompt-context Implement educational content generation feature for La Factoria with 8 content types (study guides, flashcards, etc.) targeting ages 6-18+.

/meta-prompt-standards Feature requirements:
- TDD implementation with ≥80% test coverage
- API endpoint: POST /api/generate with topic, content_type, audience
- Integration: Anthropic Claude API for content generation
- Database: PostgreSQL storage with metadata
- Frontend: Simple form interface with content display
- Performance: ≤2s generation time, ≤1s UI response

/meta-prompt-coordinate Development sequence:
1. @dev-planner - Break into TDD tasks
2. @db-dev - Design content storage schema
3. @fastapi-dev - Implement API endpoints with tests
4. @frontend-dev - Build user interface
5. @security-dev - Input validation and auth
6. @perf-dev - Optimize for speed requirements
7. @dev-validator - Quality gates at each phase

/meta-prompt-simplify Maintain constraints:
- Each file ≤200 lines
- Minimal dependencies (prefer built-ins)
- Single-purpose, focused modules
- Railway-optimized deployment

Implement complete content generation feature using coordinated agent workflow."
```

## 🔄 Continuous Development Workflow

### Daily Development Cycle
1. **Morning Planning**: `@dev-orchestrator` coordinates daily priorities
2. **TDD Implementation**: `@dev-implementer` with specialized agents
3. **Quality Gates**: `@dev-validator` continuous validation
4. **Performance Monitoring**: `@perf-dev` ongoing optimization
5. **Security Scanning**: `@security-dev` automated checks
6. **Deployment**: `@dev-deployer` Railway updates

### Integration Points
- **Code Quality**: All agents coordinate through `@dev-validator`
- **Performance**: All implementations validated by `@perf-dev`
- **Security**: All code reviewed by `@security-dev`
- **Deployment**: All changes managed by `@dev-deployer`

The development agent system ensures La Factoria is built with maximum quality while maintaining simplification goals through coordinated, meta-enhanced agent workflows.