# Quick Reference - AI Content Factory

**Generated**: 2025-06-05 11:17:32

---

## 🚀 API Endpoints

### Main Endpoints

- **GET** `/` - Root endpoint
- **GET** `/healthz` - Health check
- **POST** `/api/v1/jobs` - Create content generation job
- **GET** `/api/v1/jobs/{job_id}` - Get job status
- **GET** `/api/v1/jobs/{job_id}/result` - Get job result


## ⚡ Common Commands

### Start local server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Test health endpoint
```bash
curl http://localhost:8080/healthz
```

### Run tests
```bash
pytest
```

### Format code
```bash
black . && isort .
```

### Build Docker image
```bash
docker build -t ai-content-factory .
```

### Start with Docker Compose
```bash
docker-compose up -d
```

### Update AI context
```bash
python scripts/smart_ai_context.py
```

## 🔍 Debug Commands

### Check environment
```bash
printenv | grep -E '(GCP|API|KEY)'
```

### Test Firestore connection
```bash
gcloud firestore databases list
```

### Check Docker status
```bash
docker ps
```

### View logs
```bash
docker-compose logs -f api
```

### Test job creation
```bash
curl -X POST http://localhost:8080/api/v1/jobs -H 'Content-Type: application/json' -d '{"syllabus_text":"Test topic", "options":{}}'
```
