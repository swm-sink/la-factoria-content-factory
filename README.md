# AI Content & Podcast Factory MVP

An AI-powered service that transforms educational content into comprehensive learning materials.

## Overview

This MVP provides a Flask-based API that:
1. Accepts educational content (e.g., syllabus text)
2. Generates a comprehensive content outline as the primary structure
3. Creates multiple learning materials based on the outline:
   - Podcast script for audio content
   - Study guide for quick reference
   - One-pager summaries for key points
   - Detailed reading materials for in-depth study
   - FAQs for common questions and misconceptions
   - Flashcards for key terms and concepts
   - Reading guide questions for critical thinking
4. Converts the podcast script to audio using ElevenLabs
5. Returns all generated content via a REST API

## Prerequisites

- Python 3.10+
- Docker
- Google Cloud Platform account with:
  - Vertex AI API enabled
  - Cloud Run API enabled
  - Artifact Registry API enabled
- ElevenLabs API key

## Environment Variables

The following environment variables must be set:

- `GCP_PROJECT_ID`: Your Google Cloud project ID (e.g., "ai-content-factory-460918")
- `GEMINI_MODEL_NAME`: Vertex AI Gemini model name (default: "gemini-2.5-flash-preview-05-20")
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `ELEVENLABS_VOICE_ID`: ElevenLabs voice ID (default: "EXAVITQu4vr4xnSDxMaL")

## Local Development

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run tests:
   ```bash
   pytest
   ```

4. Start the development server:
   ```bash
   export GCP_PROJECT_ID=ai-content-factory-460918
   export ELEVENLABS_API_KEY=your-actual-elevenlabs-api-key
   export ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL
   export GEMINI_MODEL_NAME=gemini-2.5-flash-preview-05-20
   python3 main.py
   ```

## Docker Build & Run

1. Build the Docker image:
   ```bash
   docker build -t ai-content-factory-mvp:latest .
   ```

2. Run the container:
   ```bash
   docker run -p 8080:8080 \
     -e GCP_PROJECT_ID=ai-content-factory-460918 \
     -e GEMINI_MODEL_NAME=gemini-2.5-flash-preview-05-20 \
     -e ELEVENLABS_API_KEY=your-actual-elevenlabs-api-key \
     -e ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL \
     ai-content-factory-mvp:latest
   ```

## API Usage

### Generate Content

```bash
curl -X POST http://localhost:8080/generate-content \
  -H "Content-Type: application/json" \
  -d '{
    "syllabus_text": "Your educational content here..."
  }'
```

Response:
```json
{
  "content_outline": "Generated content outline...",
  "podcast_script": "Generated podcast script...",
  "study_guide": "Generated study guide...",
  "one_pager_summary": "Generated one-pager summary...",
  "detailed_reading_material": "Generated detailed reading material...",
  "faqs": [
    {
      "question": "FAQ question...",
      "answer": "FAQ answer..."
    }
  ],
  "flashcards": [
    {
      "term": "Key term...",
      "definition": "Term definition..."
    }
  ],
  "reading_guide_questions": [
    "Critical thinking question 1...",
    "Critical thinking question 2..."
  ],
  "audio_status": "Audio generated successfully and saved temporarily."
}
```

Error Response:
```json
{
  "error": "Failed to generate content from AI.",
  "error_detail": "Gemini Error: [specific error message]",
  "content_outline": "Error: Failed to generate content outline.",
  "podcast_script": "Error: Failed to generate podcast script.",
  "study_guide": "Error: Failed to generate study guide.",
  "one_pager_summary": "Error: Failed to generate one-pager summary.",
  "detailed_reading_material": "Error: Failed to generate detailed reading material.",
  "faqs": [],
  "flashcards": [],
  "reading_guide_questions": [],
  "audio_status": "Not attempted."
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

- 400 Bad Request: Invalid input (e.g., missing or invalid syllabus_text)
- 500 Internal Server Error: Missing environment variables
- 503 Service Unavailable: External API failures (Gemini or ElevenLabs)

Error responses include:
- User-friendly error message
- Detailed error information
- Partial content if available
- Status of each content type

## Monitoring & Logging

The application includes comprehensive logging:
- API request/response details
- Token usage for Gemini API calls
- Generation time metrics
- Error tracking with stack traces
- Audio generation status

## Deployment

The application is designed to be deployed to Google Cloud Run. See the deployment documentation in `docs/DEPLOYMENT.md` for detailed instructions.

## Security Notes

- This MVP uses environment variables for sensitive configuration
- Future versions will implement Google Secret Manager
- No authentication is required for MVP endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.