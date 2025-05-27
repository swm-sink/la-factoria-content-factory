# Deployment Guide

## Prerequisites

1. Google Cloud Platform account with:
   - Vertex AI API enabled
   - Cloud Run API enabled
   - Artifact Registry API enabled
   - IAM permissions configured

2. Google Cloud CLI installed and configured:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

## Deployment Steps

1. **Build and Push Docker Image**
   ```bash
   # Build the image
   docker build -t gcr.io/YOUR_PROJECT_ID/ai-content-factory-mvp:latest .

   # Push to Google Container Registry
   docker push gcr.io/YOUR_PROJECT_ID/ai-content-factory-mvp:latest
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy ai-content-factory-mvp \
     --image gcr.io/YOUR_PROJECT_ID/ai-content-factory-mvp:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="GCP_PROJECT_ID=YOUR_PROJECT_ID,GEMINI_MODEL_NAME=gemini-1.5-flash-001,ELEVENLABS_API_KEY=YOUR_API_KEY,ELEVENLABS_VOICE_ID=YOUR_VOICE_ID"
   ```

3. **Verify Deployment**
   ```bash
   # Get the service URL
   gcloud run services describe ai-content-factory-mvp --platform managed --region us-central1 --format 'value(status.url)'

   # Test the endpoint
   curl -X POST https://YOUR_SERVICE_URL/generate-content \
     -H "Content-Type: application/json" \
     -d '{"syllabus_text": "Test content..."}'
   ```

## Monitoring Setup

1. **Enable Cloud Monitoring**
   ```bash
   gcloud services enable monitoring.googleapis.com
   ```

2. **Create Monitoring Dashboard**
   - Go to Cloud Console > Monitoring > Dashboards
   - Create new dashboard with:
     - Request latency
     - Error rates
     - Token usage
     - Cost metrics

3. **Set Up Alerts**
   - Create alert policies for:
     - High error rates (>5%)
     - Slow response times (>60s)
     - High cost per request (>$0.50)

## Scaling Configuration

1. **Configure Autoscaling**
   ```bash
   gcloud run services update ai-content-factory-mvp \
     --min-instances 1 \
     --max-instances 10 \
     --cpu 1 \
     --memory 2Gi
   ```

2. **Set Up Load Balancing**
   - Configure Cloud CDN
   - Set up rate limiting
   - Configure SSL certificates

## Maintenance

1. **Regular Updates**
   - Monitor for security updates
   - Update dependencies monthly
   - Review and update API keys

2. **Backup Strategy**
   - Regular database backups
   - Configuration backups
   - Log retention policy

## Troubleshooting

1. **Common Issues**
   - API quota exceeded
   - Memory limits reached
   - Cold start latency

2. **Debug Commands**
   ```bash
   # View logs
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ai-content-factory-mvp"

   # Check service status
   gcloud run services describe ai-content-factory-mvp
   ```

## Security Considerations

1. **API Security**
   - Use API keys
   - Implement rate limiting
   - Enable CORS properly

2. **Data Security**
   - Encrypt sensitive data
   - Use Secret Manager for credentials
   - Regular security audits

## Development Setup

1. **Local Development Environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install development dependencies
   pip install -r requirements.txt

   # Install pre-commit hooks
   pre-commit install
   ```

2. **Code Quality Tools**
   ```bash
   # Run type checking
   mypy .

   # Run linting
   flake8 .
   black . --check
   isort . --check

   # Run security checks
   bandit -r .
   safety check
   ```

3. **Testing**
   ```bash
   # Run all tests with coverage
   pytest --cov=. --cov-report=html

   # Run specific test categories
   pytest tests/unit/
   pytest tests/integration/
   pytest tests/e2e/
   ```

## CI/CD Pipeline

1. **GitHub Actions Workflow**
   ```yaml
   name: CI/CD Pipeline
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.10'
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt
         - name: Run tests
           run: |
             pytest --cov=. --cov-report=xml
         - name: Upload coverage
           uses: codecov/codecov-action@v3
   ```

2. **Quality Gates**
   - Test coverage > 80%
   - No type errors
   - No linting errors
   - No security vulnerabilities
   - All tests passing 