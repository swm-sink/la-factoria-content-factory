# La Factoria Railway Deployment Guide

## Pre-Deployment Checklist ✅

### Project Structure
- [x] FastAPI application (`src/main.py`)
- [x] Railway configuration (`railway.toml`)
- [x] Dependencies (`requirements.txt`)
- [x] Database migration (`migrations/001_initial_schema.sql`)
- [x] Frontend interface (`static/` directory)
- [x] Educational content system

## Railway Deployment Steps

### 1. Initial Deployment
```bash
# Connect to Railway (if not already done)
railway login

# Link to existing project or create new
railway link

# Deploy to Railway
railway up
```

### 2. Environment Variables Setup
Set these in Railway dashboard:

**Required:**
- `LA_FACTORIA_API_KEY` - API authentication key
- `SECRET_KEY` - Application secret key
- `DATABASE_URL` - Railway PostgreSQL (auto-set)

**AI Providers (at least one required):**
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key  
- `GOOGLE_CLOUD_PROJECT` - Google Cloud project ID

**Optional:**
- `LANGFUSE_PUBLIC_KEY` - Prompt management
- `LANGFUSE_SECRET_KEY` - Prompt management
- `REDIS_URL` - Caching (Railway Redis)

### 3. Database Setup
```bash
# Railway will automatically provision PostgreSQL
# Run migration after first deployment:
railway run psql -d $DATABASE_URL -f migrations/001_initial_schema.sql
```

### 4. Verification Steps

#### Health Check
```bash
curl https://your-app.railway.app/health
```
Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-03T...",
  "version": "1.0.0"
}
```

#### Content Generation Test
```bash
curl -X POST https://your-app.railway.app/api/v1/content/generate/study_guide \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Programming Basics",
    "age_group": "high_school"
  }'
```

### 5. Monitoring Setup

#### Health Monitoring
- Railway automatically monitors `/health` endpoint
- Auto-restart on failure configured
- Resource monitoring in Railway dashboard

#### Performance Targets
- API Response: <200ms (95th percentile)
- Content Generation: <30s end-to-end
- Quality Assessment: <5s completion
- Database Queries: <50ms average

## Production URLs

- **Application**: `https://your-app.railway.app`
- **API Documentation**: `https://your-app.railway.app/docs` (staging only)
- **Health Check**: `https://your-app.railway.app/health`

## Educational Content Generation

### Supported Content Types (8 total):
1. **Master Content Outline** - Learning framework
2. **Podcast Script** - Audio content with cues
3. **Study Guide** - Comprehensive educational material
4. **One-Pager Summary** - Concise overview
5. **Detailed Reading Material** - In-depth content
6. **FAQ Collection** - Common questions
7. **Flashcards** - Memory aid cards
8. **Reading Guide Questions** - Discussion prompts

### Quality Standards:
- Overall Quality: ≥0.70
- Educational Value: ≥0.75  
- Factual Accuracy: ≥0.85
- Age Appropriateness: Validated

## Troubleshooting

### Common Issues:
1. **502 Bad Gateway** - Check environment variables
2. **Database connection** - Verify DATABASE_URL
3. **AI provider errors** - Check API keys
4. **Quality assessment fails** - Review content complexity

### Logs:
```bash
railway logs
```

### Database Access:
```bash
railway connect
```

## Operational Excellence

### Daily Monitoring:
- [ ] Health check status
- [ ] Response time metrics  
- [ ] Content generation success rate
- [ ] Quality score distribution
- [ ] AI provider performance

### Weekly Reviews:
- [ ] Resource utilization
- [ ] Cost optimization
- [ ] User feedback analysis
- [ ] Performance trends
- [ ] Educational effectiveness metrics

---

**🎯 Success Criteria Met:**
- ✅ Complete La Factoria platform deployed
- ✅ All 8 educational content types operational
- ✅ Quality assessment pipeline working
- ✅ Professional frontend interface
- ✅ Comprehensive monitoring setup
- ✅ Production-ready infrastructure
