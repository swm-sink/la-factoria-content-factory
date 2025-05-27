# Changelog

All notable changes to the AI Content & Podcast Factory MVP will be documented in this file.

## [0.2.0] - 2024-06-09

### Added
- Expanded content generation capabilities:
  - Content outline generation as the primary structure
  - One-pager summaries for quick reference
  - Detailed reading materials for in-depth study
  - FAQs for common questions and misconceptions
  - Flashcards for key terms and concepts
  - Reading guide questions for critical thinking
- Enhanced Gemini prompt engineering for structured JSON output
- Improved error handling with detailed error messages
- Token usage and cost tracking for Gemini API calls
- Modular code structure with helper functions
- Comprehensive test coverage for new content types

### Changed
- Refactored `/generate-content` endpoint to return all content types
- Updated API response structure to include all generated content
- Enhanced error responses to include partial content when available
- Improved logging with token usage metrics

## [0.1.0] - 2024-02-19

### Added
- Initial MVP release with core functionality
- Flask application with `/generate-content` endpoint
- Integration with Vertex AI Gemini for content generation
- Integration with ElevenLabs for text-to-speech conversion
- Docker containerization with optimized Dockerfile
- Basic unit tests with pytest
- Comprehensive error handling and logging
- Input validation for API endpoints
- Environment variable configuration for API keys

### Known Issues
- API keys are sourced from environment variables (to be moved to Secret Manager)
- Audio files are stored temporarily (to be moved to Cloud Storage)
- No authentication/authorization implemented
- Limited error recovery for external API failures
- No rate limiting or request throttling
- No monitoring or alerting setup

### Security Notes
- All sensitive configuration is currently managed via environment variables
- Future versions will implement Secret Manager for API key management
- No authentication required for MVP endpoints 