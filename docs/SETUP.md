# La Factoria Setup Guide

This guide will help you set up and run La Factoria Educational Content Generation Platform locally or deploy it to Railway.

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Git
- AI Provider API keys (OpenAI, Anthropic, or Google Cloud)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd la-factoria-v2/lima
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Initialize database (optional)**
   ```bash
   # For PostgreSQL, run the migration
   # psql -f migrations/001_initial_schema.sql
   
   # For development, SQLite will be created automatically
   ```

6. **Run the application**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the application**
   - API: http://localhost:8000
   - Frontend: http://localhost:8000/static/index.html
   - API Documentation: http://localhost:8000/docs

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

#### Required Settings
- `LA_FACTORIA_API_KEY`: Your API key for authentication
- `SECRET_KEY`: Secret key for session management
- At least one AI provider API key:
  - `OPENAI_API_KEY`: OpenAI GPT-4 access
  - `ANTHROPIC_API_KEY`: Anthropic Claude access
  - `GOOGLE_CLOUD_PROJECT`: Google Cloud project for Vertex AI

#### Optional Settings
- `DATABASE_URL`: PostgreSQL connection string (defaults to SQLite)
- `LANGFUSE_SECRET_KEY` & `LANGFUSE_PUBLIC_KEY`: For prompt management
- `REDIS_URL`: For caching (optional)

### AI Provider Setup

#### OpenAI
1. Get API key from https://platform.openai.com/api-keys
2. Set `OPENAI_API_KEY` in your `.env` file

#### Anthropic
1. Get API key from https://console.anthropic.com/
2. Set `ANTHROPIC_API_KEY` in your `.env` file

#### Google Cloud (Vertex AI)
1. Create a Google Cloud project
2. Enable Vertex AI API
3. Set `GOOGLE_CLOUD_PROJECT` and optionally `GOOGLE_CLOUD_REGION`

## Railway Deployment

### One-Click Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/...)

### Manual Deployment

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and create project**
   ```bash
   railway login
   railway init
   ```

3. **Add environment variables**
   ```bash
   railway variables set LA_FACTORIA_API_KEY=your-key-here
   railway variables set OPENAI_API_KEY=your-openai-key
   # Add other required variables
   ```

4. **Deploy**
   ```bash
   railway up
   ```

## Database Setup

### PostgreSQL (Production)

1. **Create database**
   ```sql
   CREATE DATABASE la_factoria;
   ```

2. **Run migrations**
   ```bash
   psql -d la_factoria -f migrations/001_initial_schema.sql
   ```

### SQLite (Development)

SQLite database will be created automatically at `./la_factoria_dev.db`.

## API Usage

### Authentication

All API endpoints require authentication using a Bearer token:

```bash
curl -H "Authorization: Bearer your-api-key" \
     http://localhost:8000/api/v1/content-types
```

### Generate Content

```bash
curl -X POST "http://localhost:8000/api/v1/generate/study_guide" \
     -H "Authorization: Bearer your-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "Python Programming Basics",
       "age_group": "high_school",
       "additional_requirements": "Include practical examples"
     }'
```

### Available Content Types

- `master_content_outline` - Foundation structure with learning objectives
- `podcast_script` - Conversational audio content with speaker notes
- `study_guide` - Comprehensive educational material with key concepts
- `one_pager_summary` - Concise overview with essential takeaways
- `detailed_reading_material` - In-depth content with examples and exercises
- `faq_collection` - Question-answer pairs covering common topics
- `flashcards` - Term-definition pairs for memorization and review
- `reading_guide_questions` - Discussion questions for comprehension

## Troubleshooting

### Common Issues

1. **Import errors**
   - Make sure virtual environment is activated
   - Install dependencies: `pip install -r requirements.txt`

2. **Database connection errors**
   - Check `DATABASE_URL` in `.env`
   - Ensure PostgreSQL is running (if using PostgreSQL)

3. **AI provider errors**
   - Verify API keys are correct and have sufficient credits
   - Check API key permissions and rate limits

4. **Port already in use**
   ```bash
   # Use a different port
   uvicorn src.main:app --port 8001
   ```

### Health Checks

- Basic health: `GET /health`
- Detailed health: `GET /api/v1/health/detailed`
- AI providers: `GET /api/v1/health/ai-providers`

### Logs

Application logs are printed to stdout. To change log level:

```bash
export LOG_LEVEL=DEBUG
uvicorn src.main:app --reload
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Install development dependencies
pip install pytest pytest-asyncio black flake8

# Format code
black .

# Lint code
flake8 .
```

### Adding New Content Types

1. Add prompt template to `prompts/` directory
2. Update `LaFactoriaContentType` enum in `src/models/educational.py`
3. Add endpoint in `src/api/routes/content_generation.py`
4. Update frontend in `static/`

## Support

For issues and questions:

1. Check this setup guide
2. Review the API documentation at `/docs`
3. Check application logs for error details
4. Verify environment configuration

## Performance Optimization

### Production Recommendations

- Use PostgreSQL instead of SQLite
- Enable Redis for caching
- Configure proper CORS origins
- Set appropriate worker count for uvicorn
- Monitor quality thresholds and adjust as needed

### Scaling

- Railway handles automatic scaling
- For high volume, consider:
  - Increasing worker count
  - Using load balancing
  - Implementing request queuing
  - Monitoring AI provider rate limits

## Security

### Production Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Use strong `LA_FACTORIA_API_KEY`
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS (automatic on Railway)
- [ ] Regularly rotate API keys
- [ ] Monitor for unusual usage patterns
- [ ] Keep dependencies updated