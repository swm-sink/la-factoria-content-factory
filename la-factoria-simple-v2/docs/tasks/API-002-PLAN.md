# API-002: Content Generation Endpoint - PLAN

## Objective

Create POST /api/generate endpoint structure with proper validation and error handling.

## Requirements

1. Accept JSON payload with topic and content_type
2. Validate input (topic required, content_type from allowed list)
3. Require API key authentication
4. Return 400 for invalid input
5. Return 401 for missing/invalid auth
6. Return structured response format

## Input Schema

```json
{
  "topic": "string, required, min 10 chars, max 500 chars",
  "content_type": "string, optional, default: study_guide",
  "options": {
    "audience": "string, optional",
    "length": "string, optional"
  }
}
```

## Allowed Content Types

- study_guide (default)
- flashcards
- podcast_script
- one_pager
- detailed_reading
- faq
- quiz
- reading_questions

## Response Schema

```json
{
  "content": "string",
  "content_type": "string",
  "topic": "string",
  "generated_at": "ISO timestamp",
  "request_id": "uuid"
}
```

## Error Responses

- 400: Invalid input (missing topic, invalid content_type, topic too short/long)
- 401: Missing or invalid API key
- 422: Validation error details
- 500: Server error

## Test Cases to Write

1. Test endpoint exists and accepts POST
2. Test requires authentication (401 without key)
3. Test validates required topic field
4. Test validates topic length (min 10, max 500)
5. Test validates content_type is from allowed list
6. Test default content_type is study_guide
7. Test successful request returns correct schema
8. Test request_id is unique per request

## Implementation Notes

- No actual AI generation yet (return mock for now)
- Focus on structure and validation
- Use Pydantic for request/response models
- Simple in-memory API key check for now
