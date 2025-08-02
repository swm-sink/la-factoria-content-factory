# Tikal Simple - Content Generation Without Complexity

A dramatically simplified version of the AI Content Factory, reduced from 1000+ files to ~10 files.

## Features

✅ AI-powered content generation (study guides, flashcards, summaries, quizzes)  
✅ Simple API key authentication  
✅ Basic GDPR compliance (user deletion)  
✅ Minimal monitoring (stats endpoint)  
✅ Zero configuration deployment on Railway

## Quick Start (< 10 minutes)

### 1. Clone and Install

```bash
git clone <repo>
cd tikal-simple/backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Locally

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend (in another terminal)
cd frontend
python -m http.server 3000
# Visit http://localhost:3000
```

### 4. Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy
railway up
```

That's it! Your app is live with HTTPS, monitoring, and automatic deploys.

## Architecture

```
Backend:  150 lines of Python (FastAPI)
Frontend: 150 lines of JavaScript (Vanilla)
Styles:   100 lines of CSS
Tests:     50 lines of pytest
Config:     3 files
-----------------------------------------
Total:   ~500 lines (vs 10,000+ original)
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/generate` - Generate content
- `DELETE /api/user/{id}` - GDPR deletion
- `GET /api/stats` - Basic statistics

## Configuration

All configuration via environment variables:
- `API_KEYS` - Comma-separated API keys
- `AI_PROVIDER` - "openai" or "anthropic"  
- `AI_API_KEY` - Your AI provider key

## Testing

```bash
cd backend
pytest ../tests/test_basic.py
```

## Monitoring

Railway provides:
- Automatic HTTPS
- Deployment logs
- Resource metrics
- Uptime monitoring

## Maintenance

- **Adding features**: Edit `main.py`
- **Changing UI**: Edit `index.html` and `app.js`
- **Updating deps**: Edit `requirements.txt`

## Philosophy

> "Perfection is achieved not when there is nothing more to add,  
> but when there is nothing left to take away." - Antoine de Saint-Exupéry

This project embraces radical simplicity for maintainability by non-technical "vibe coders".

## License

MIT - Keep it simple!