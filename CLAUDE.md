# Claude Code Configuration

This file contains project-specific instructions and standards for Claude Code to follow when working with this repository.

## Project Overview

This is Tikal, a content generation service built with FastAPI (Python backend) and React/TypeScript (frontend). The application generates educational content using AI models and supports various output formats.

## Code Standards

### Python Backend

- Use FastAPI framework patterns
- Follow PEP 8 style guidelines
- Use type hints throughout
- Implement proper error handling with custom exceptions
- Use Pydantic models for data validation
- Follow the existing service layer architecture

### Frontend (React/TypeScript)

- Use TypeScript with strict mode
- Follow React hooks patterns
- Use Tailwind CSS for styling
- Implement proper error boundaries
- Use the existing context patterns for state management

### Testing

- Write unit tests for new functionality
- Use pytest for Python tests
- Run tests with: `pytest`
- Ensure all tests pass before committing

### Documentation

- Update relevant documentation when making changes
- Follow existing documentation patterns
- Keep CHANGELOG.md updated for significant changes

## Dependencies

- Backend: Python 3.11+, FastAPI, Pydantic, Google Cloud libraries
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Infrastructure: Google Cloud Platform, Terraform

## Project Structure

- `/app` - Python backend application
- `/frontend` - React frontend application  
- `/tests` - Test files
- `/docs` - Documentation
- `/iac` - Infrastructure as Code (Terraform)

## Development Guidelines

- Keep services modular and loosely coupled
- Use dependency injection patterns
- Implement proper logging and monitoring
- Follow security best practices for API development
- Use environment variables for configuration

## Memory System & Analysis Standards

### MANDATORY: Context-First Analysis

- **NEVER** make architectural recommendations without understanding business/legal requirements
- **ALWAYS** discover compliance obligations (GDPR, SLA, audit requirements) before suggesting simplifications
- **VERIFY** all claims with specific file references and line numbers
- **DOCUMENT** findings in `.claude/memory/` before proceeding

### No Hallucination Policy

- **ZERO TOLERANCE** for unverified claims
- **ALL** assertions must reference specific files with line numbers
- **IMMEDIATE** correction required when evidence contradicts assumptions
- **MANDATORY** verification of regulatory/compliance context

### Memory System Structure

Located in `.claude/memory/`:

- `analysis_learnings.md` - Major findings and corrections
- `decision_rationale.md` - Context and justification for all decisions  
- `git_commit_patterns.md` - Atomic commit standards and patterns

### Atomic Commit Requirements

- **ONE** logical change per commit
- **CLEAR** commit messages with file references
- **IMMEDIATE** memory system updates for significant findings
- **TRACEABLE** decision rationale for all architectural changes

### Analysis Methodology

1. **Context Discovery**: Understand business/legal requirements FIRST
2. **Evidence Gathering**: Reference specific files and line numbers
3. **Risk Assessment**: Identify compliance/contractual obligations
4. **Memory Documentation**: Update `.claude/memory/` with findings
5. **Selective Recommendations**: Distinguish required vs. optional complexity

## Prompt Engineering System

### Overview

Tikal uses a modular prompt engineering system located in `.claude/` to optimize AI content generation. This system provides:

- Optimized prompt templates for all 8 content types
- Context-aware prompt generation
- Quality validation frameworks
- Educational standards compliance

### Tikal-Specific Commands

Located in `.claude/commands/tikal/`:

- `/tikal-optimize-prompts` - Analyze and optimize existing prompts
- `/tikal-validate-quality` - Validate content quality against educational standards
- `/tikal-generate` - Generate content using optimized templates
- `/tikal-analyze-prompts` - Analyze prompts for optimization opportunities

### Prompt Templates

Optimized templates in `.claude/templates/tikal/`:

- `study-guide-optimized.md` - Enhanced study guide generation
- `flashcards-optimized.md` - Cognitive science-based flashcard creation
- Additional templates for all content types

### Context System

- **Project Context**: `.claude/context/tikal-project.md` - Comprehensive project understanding
- **Educational Standards**: `.claude/components/tikal/educational-standards.md`
- **Quality Assessment**: `.claude/components/tikal/quality-assessment.md`

### Prompt Optimization Principles

1. **Token Efficiency**: 20-40% reduction through consolidation and clarity
2. **Educational Focus**: Explicit learning objectives and audience targeting
3. **Quality Requirements**: Specific, measurable quality criteria
4. **Consistency**: Standardized structure across all content types
5. **Validation**: Built-in quality checks and educational standards

### Using the Prompt System

1. For prompt analysis: `/tikal-analyze-prompts app/core/prompts/v1/`
2. For content validation: `/tikal-validate-quality [content-type] [audience]`
3. For optimized generation: `/tikal-generate [content-type] [topic] [audience]`
4. For prompt optimization: `/tikal-optimize-prompts [content-type]`

### Best Practices

- Always specify audience level (elementary, middle-school, high-school, university)
- Include learning objectives for educational content
- Use quality thresholds (minimum 0.70 overall score)
- Validate content against educational standards
- Apply cognitive science principles for effective learning
