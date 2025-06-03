# Changelog

All notable changes to the AI Content Factory project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-06-01

### Added
- Created `app/utils/lightweight_nlp.py` - Pure Python implementation of NLP utilities
- Added `docs/CURRENT_STATUS.md` - Honest assessment of project state
- Created comprehensive test for lightweight NLP functionality

### Changed
- Refactored `app/services/semantic_validator.py` to use lightweight NLP instead of sklearn
- Updated `tests/unit/test_app.py` to match actual API endpoints (`/healthz` and `/api/v1/content/generate`)
- Modified content generation tests to use correct API paths

### Fixed
- Resolved sklearn dependency issues blocking test execution
- Fixed all 5 tests in `test_enhanced_multi_step_content_generation_service.py`
- Corrected API endpoint paths in test files
- Fixed attribute naming issues (ContentMetadata vs QualityMetrics)

### Removed
- Removed sklearn from requirements.txt
- Eliminated heavyweight ML dependencies

### Security
- Maintained all sensitive data handling protocols
- No credentials or secrets exposed in refactoring

## [0.1.0] - 2025-05-31

### Added
- Initial project structure
- FastAPI backend with content generation pipeline
- React frontend with authentication
- Terraform infrastructure as code
- Docker containerization
- CI/CD pipelines with GitHub Actions

### Known Issues
- Test coverage at 51.8% (121 failures, 162 passed, 30 errors)
- API routing integration incomplete
- Configuration/settings validation errors
- Production deployment blockers remain

---

*Note: Despite claims in some documentation, the project is NOT production-ready as of June 1, 2025.*
