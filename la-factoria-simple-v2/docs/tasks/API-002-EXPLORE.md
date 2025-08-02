# API-002: Content Generation Endpoint - EXPLORE

## Findings from Existing System

### Content Types Available (from prompts/)

1. study_guide - Basic study guide
2. study_guide_enhanced - Enhanced version
3. flashcards - Spaced repetition cards
4. podcast_script - Audio content script
5. one_pager_summary - Executive summary
6. detailed_reading_material - In-depth content
7. faq_collection - Frequently asked questions
8. reading_guide_questions - Discussion questions
9. master_content_outline - Structured outline (used as base)

### Old System Patterns

- Used "syllabus_text" for input (50-5000 chars)
- Had complex validation and quality metrics
- Supported parallel processing (unnecessary for our scale)
- Had caching system (unnecessary for 10 users)

### Simplification Decisions

1. Rename "syllabus_text" to "topic" (clearer)
2. Reduce min length from 50 to 10 chars (more flexible)
3. Support all 9 content types from prompts
4. No parallel processing (synchronous is fine)
5. No complex quality metrics (just generate content)
6. No caching initially (can add if needed)

### API Key Pattern (from current main.py)

```python
API_KEYS = os.getenv("API_KEYS", "test-key-123,admin-key-123").split(",")
```

Simple comma-separated list in environment variable.

## Updated Requirements

- Support all 9 content types from extracted prompts
- Simple validation (topic 10-500 chars)
- Basic API key check from environment
- Return generated content with metadata
