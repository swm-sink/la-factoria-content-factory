---
name: /project
description: "La Factoria construction orchestrator - build educational content platform step-by-step with TDD"
usage: "[build-step] [options]"
tools: Read, Write, Edit, Bash, Grep, Task
---
# /project - La Factoria Construction Orchestrator

Step-by-step builder for La Factoria educational content generation platform, following TDD principles and atomic task breakdown from implementation roadmap.

## Instructions

Use this command to build La Factoria educational platform incrementally. Each step follows TDD methodology with quality gates to ensure production readiness.

**Quick Start:**

```bash
/project init          # Start with foundation setup
/project content-generation    # Add AI content generation
/project langfuse      # Set up prompt management
```

**TDD Workflow:**

```bash
/project test [task-name]       # Write tests first
/project implement [task-name]  # Implement to pass tests
/project quality-gate [task-name]  # Verify quality standards
```

## La Factoria Construction Steps

```bash
# SPRINT 1: Foundation (Days 1-5)
/project init                               # TASK-001: Initialize La Factoria structure + Railway
/project content-generation                 # TASK-002: Basic content generation with AI
/project langfuse                          # TASK-003: External prompt management

# SPRINT 2: Data & Frontend (Days 6-10)  
/project postgres                          # TASK-004: Railway PostgreSQL for content storage
/project frontend                          # TASK-005: Minimal vanilla JS frontend

# SPRINT 3: Essential Features (Days 11-15)
/project gdpr                              # TASK-006: Simple user deletion compliance
/project monitoring                        # TASK-007: Basic stats and uptime tracking

# TDD Commands - Write Tests First
/project test [task-name]                   # Write tests before implementation
/project implement [task-name]             # Implement after tests pass
/project quality-gate [task-name]          # Verify coverage + complexity gates

# Status and Progress
/project status                            # Show current construction progress
/project next                              # Show next recommended build step
/project rollback [task-name]              # Rollback specific construction step

# CI/CD Operations
/project run ci                             # Run CI pipeline  
/project run tests                          # Run test suite
/project deploy railway                     # Deploy to Railway platform
```

## Construction Implementation

Each construction step follows **TDD methodology**:

1. **Write Tests First** - Define expected behavior
2. **Implement Minimal Code** - Make tests pass
3. **Quality Gates** - Verify coverage, complexity, line limits
4. **Atomic Commits** - Single feature per commit

### TASK-001: Initialize La Factoria Structure

```bash
/project init
```

**TDD Process:**

- Write tests for: FastAPI health endpoint, project structure validation, Railway deployment
- Implement: Minimal FastAPI app, basic project structure, Railway configuration
- Quality Gates: All tests pass, Railway deployment successful, health endpoint responds

### TASK-002: Basic Content Generation  

```bash
/project content-generation
```

**TDD Process:**

- Write tests for: Content endpoint exists, successful generation, API key validation
- Implement: Simple content generation endpoint, basic auth, AI provider integration
- Quality Gates: >80% coverage, <100 lines code, no complex abstractions

### TASK-003: Langfuse Prompt Management

```bash
/project langfuse
```

**TDD Process:**

- Write tests for: Langfuse connection, prompt retrieval, variable compilation
- Implement: Langfuse client setup, basic prompts in UI, replace hardcoded prompts
- Quality Gates: All prompts managed externally, zero prompt code in repo

### TASK-004: Railway PostgreSQL Storage

```bash
/project postgres
```

**TDD Process:**

- Write tests for: Database connection, content storage, content retrieval
- Implement: Railway Postgres setup, simple schema (users, content), basic CRUD
- Quality Gates: DB operations <50 lines, no ORM complexity, all tests pass

### TASK-005: Minimal Frontend Interface

```bash
/project frontend
```

**TDD Process:**

- Write tests for: HTML loads, form submission, content display
- Implement: Single HTML file, vanilla JavaScript, simple CSS
- Quality Gates: Frontend <500 lines total, no build process, mobile responsive

### TASK-006: GDPR User Deletion

```bash
/project gdpr
```

**TDD Process:**

- Write tests for: User deletion endpoint, cascade deletion, deletion logging
- Implement: DELETE /api/user/{id}, simple cascade delete, basic logging
- Quality Gates: Implementation <30 lines, no complex audit trail

### TASK-007: Basic Monitoring

```bash
/project monitoring
```

**TDD Process:**

- Write tests for: Stats endpoint, metric calculations, uptime tracking
- Implement: /api/stats endpoint, count queries, simple uptime calculation
- Quality Gates: No external tools, <50 lines, <100ms response time

## La Factoria Construction Implementation

This command executes the step-by-step construction of La Factoria following TDD methodology and quality gates from the implementation roadmap.
