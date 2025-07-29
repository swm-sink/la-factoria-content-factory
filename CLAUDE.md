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