# AI Content Factory - Production Deployment Checklist

**Version:** 1.0  
**Date:** 2025-05-30  
**Project:** AI Content Factory MVP

**Note on Automation:** Many of the infrastructure setup, application build, and deployment steps outlined in this checklist are automated via Terraform (see `iac/` directory) and GitHub Actions CI/CD pipelines (see `.github/workflows/`). This checklist serves as a comprehensive guide to all components and considerations, including verification steps for automated processes and fallback manual steps where applicable.

## Pre-Deployment Checklist

### 🔧 **Infrastructure Prerequisites**

#### GCP Project Setup
- [ ] GCP Project created and billing enabled
- [ ] Required APIs enabled:
  - [ ] Cloud Run API
  - [ ] Artifact Registry API
  - [ ] Firestore API
  - [ ] Cloud Tasks API
  - [ ] Secret Manager API
  - [ ] Cloud Workflows API
  - [ ] Vertex AI API
- [ ] Terraform service account created with appropriate permissions
- [ ] Workload Identity Federation configured for GitHub Actions

#### Terraform Infrastructure Deployment
- [ ] **GCS Backend Setup:**
  ```bash
  # Create Terraform state bucket
  gsutil mb gs://acpf-mvp-terraform-state
  gsutil versioning set on gs://acpf-mvp-terraform-state
  ```

- [ ] **Deploy Infrastructure:**
  ```bash
  cd iac/
  terraform init
  terraform plan -var="project_id=YOUR_PROJECT_ID"
  terraform apply -var="project_id=YOUR_PROJECT_ID"
  ```

- [ ] **Verify Resources Created:**
  - [ ] Artifact Registry repository
  - [ ] Cloud Run service
  - [ ] Firestore database
  - [ ] Cloud Tasks queue
  - [ ] Secret Manager secrets (placeholders)
  - [ ] API Gateway (if used)
  - [ ] IAM service accounts and bindings

### 🔐 **Secrets Management**

**Note:** Secret placeholders are created by Terraform. Versions are populated manually as per below for MVP. Ensure IAM permissions for Cloud Run SA to access these are set by Terraform.

#### Required Secrets in GCP Secret Manager (as referenced by `app/core/config/settings.py`)
- [ ] **`AI_CONTENT_FACTORY_API_KEY`** - API Key for accessing the application itself.
- [ ] **`AI_CONTENT_FACTORY_ELEVENLABS_KEY`** - ElevenLabs API key for audio generation.
- [ ] **`AI_CONTENT_FACTORY_JWT_SECRET_KEY`** - JWT signing secret (generate: `openssl rand -hex 32`).
- [ ] **`AI_CONTENT_FACTORY_SENTRY_DSN`** - Sentry DSN for error reporting (optional).

#### Secret Population Commands
```bash
# Application API Key
echo "YOUR_APPLICATION_API_KEY" | gcloud secrets versions add AI_CONTENT_FACTORY_API_KEY --data-file=-

# JWT Secret
openssl rand -hex 32 | gcloud secrets versions add AI_CONTENT_FACTORY_JWT_SECRET_KEY --data-file=-

# ElevenLabs API Key
echo "YOUR_ELEVENLABS_API_KEY" | gcloud secrets versions add AI_CONTENT_FACTORY_ELEVENLABS_KEY --data-file=-

# Sentry DSN (Optional)
echo "YOUR_SENTRY_DSN" | gcloud secrets versions add AI_CONTENT_FACTORY_SENTRY_DSN --data-file=-
```

- [ ] All secrets populated with valid values
- [ ] Service account has Secret Manager access
- [ ] Test secret retrieval: `gcloud secrets versions access latest --secret="AI_CONTENT_FACTORY_API_KEY"`

### 🏗️ **Application Deployment**

**Note:** Docker image build/push and Cloud Run deployment are automated by CI/CD workflows. Manual steps below are for understanding or emergency/manual override.

#### Docker Image Build & Push
- [ ] **Build and Push via CI/CD:**
  - [ ] Push code to `main` branch
  - [ ] Verify GitHub Actions workflows execute successfully
  - [ ] Confirm image pushed to Artifact Registry

- [ ] **Manual Build (if needed):**
  ```bash
  # Build image
  docker build -t ${{ secrets.GCP_ARTIFACT_REGISTRY_REGION }}-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/${{ secrets.GCP_ARTIFACT_REGISTRY_REPO_ID }}/acpf-mvp:manual-build .
  
  # Push to Artifact Registry
  docker push ${{ secrets.GCP_ARTIFACT_REGISTRY_REGION }}-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/${{ secrets.GCP_ARTIFACT_REGISTRY_REPO_ID }}/acpf-mvp:manual-build
  ```

#### Cloud Run Deployment
- [ ] **Deploy to Cloud Run:**
  **Automated via `.github/workflows/deploy-cloud-run.yml` and `.github/workflows/terraform-apply.yml`.**
  Manual command example (ensure alignment with CI/CD variables and IaC outputs - especially image path and service account):
  ```bash
  gcloud run deploy acpf-mvp-api-dev \
    --image ${{ secrets.GCP_ARTIFACT_REGISTRY_REGION }}-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/${{ secrets.GCP_ARTIFACT_REGISTRY_REPO_ID }}/acpf-mvp:latest \
    --platform managed \
    --region ${{ secrets.GCP_ARTIFACT_REGISTRY_REGION }} \
    --allow-unauthenticated \
    --service-account cloud-run-service-account@${{ secrets.GCP_PROJECT_ID }}.iam.gserviceaccount.com \
    --set-env-vars PROJECT_ID=${{ secrets.GCP_PROJECT_ID }},ENVIRONMENT=production
  ```

- [ ] **Verify Deployment:**
  - [ ] Service status: `gcloud run services describe acpf-mvp-apiserver --region=REGION`
  - [ ] Health check: `curl https://YOUR_SERVICE_URL/health`
  - [ ] API endpoint test: `curl https://YOUR_SERVICE_URL/api/v1/health`

### 🧪 **Post-Deployment Testing**

#### API Endpoints Verification
- [ ] **Health Checks:**
  - [ ] `GET /health` returns 200 OK
  - [ ] `GET /api/v1/health` returns 200 OK

- [ ] **Authentication Endpoints:**
  - [ ] `POST /api/v1/auth/register` accepts new user registration
  - [ ] `POST /api/v1/auth/login` returns valid JWT token
  - [ ] `GET /api/v1/auth/users/me` returns user details with valid JWT

- [ ] **Content Generation:**
  - [ ] `POST /api/v1/jobs` creates content generation job
  - [ ] `GET /api/v1/jobs/{job_id}` returns job status
  - [ ] End-to-end content generation completes successfully

- [ ] **Feedback System:**
  - [ ] `POST /api/v1/content/{content_id}/feedback` accepts feedback

#### Integration Testing
- [ ] **Firestore Integration:**
  - [ ] Jobs are persisted in Firestore
  - [ ] User data is stored correctly
  - [ ] Feedback data is stored correctly

- [ ] **External API Integration:**
  - [ ] Vertex AI Gemini API calls succeed
  - [ ] ElevenLabs TTS API calls succeed (if enabled)
  - [ ] All API keys and service accounts work

- [ ] **Cloud Tasks Integration:**
  - [ ] Jobs are queued to Cloud Tasks
  - [ ] Worker endpoint processes tasks
  - [ ] Job status updates correctly

### 🖥️ **Frontend Deployment** (Optional)

#### Static Hosting Setup
- [ ] **Build Frontend:**
  ```bash
  cd frontend/
  npm run build
  ```

- [ ] **Deploy to GCS/CDN:**
  ```bash
  # Create bucket for static hosting
  gsutil mb gs://YOUR_PROJECT_ID-frontend
  gsutil web set -m index.html -e index.html gs://YOUR_PROJECT_ID-frontend
  
  # Upload build files
  gsutil -m cp -r dist/* gs://YOUR_PROJECT_ID-frontend/
  gsutil -m acl ch -u AllUsers:R gs://YOUR_PROJECT_ID-frontend/**
  ```

- [ ] **Configure API Base URL:**
  - [ ] Update `VITE_API_URL` in frontend build to point to Cloud Run service
  - [ ] Verify CORS settings in backend allow frontend domain

### 📊 **Monitoring & Observability**

#### Cloud Monitoring Setup
- [ ] **Alerts Configured:**
  - [ ] Cloud Run instance health
  - [ ] API endpoint response times
  - [ ] Error rate thresholds
  - [ ] Firestore read/write quotas

- [ ] **Dashboards Created:**
  - [ ] Application performance dashboard
  - [ ] API usage dashboard
  - [ ] Cost monitoring dashboard

#### Logging Verification
- [ ] **Application Logs:**
  - [ ] Structured logging is working
  - [ ] No sensitive data in logs
  - [ ] Log levels appropriate for production

- [ ] **Audit Logging:**
  - [ ] API access logs
  - [ ] Authentication events
  - [ ] Content generation requests

### 🔒 **Security Verification**

#### Access Controls
- [ ] **IAM Permissions:**
  - [ ] Service accounts follow least privilege
  - [ ] No overly broad permissions
  - [ ] Regular audit schedule established

- [ ] **Network Security:**
  - [ ] HTTPS enforced on all endpoints
  - [ ] No public database access
  - [ ] Firewall rules configured appropriately

#### Data Protection
- [ ] **Secret Management:**
  - [ ] No secrets in code or logs
  - [ ] Secret rotation schedule established
  - [ ] Backup of critical secrets secured

- [ ] **Data Privacy:**
  - [ ] User data encryption at rest
  - [ ] Data retention policies implemented
  - [ ] GDPR compliance measures (if applicable)

### 💰 **Cost Management**

#### Budget Controls
- [ ] **Billing Alerts:**
  - [ ] Daily spending alerts configured
  - [ ] Monthly budget thresholds set
  - [ ] Cost attribution by service enabled

- [ ] **Resource Optimization:**
  - [ ] Cloud Run concurrency settings optimized
  - [ ] Firestore read/write patterns analyzed
  - [ ] AI API usage monitoring enabled

## Go-Live Checklist

### Final Pre-Production Steps
- [ ] **Load Testing:** Conduct load tests with expected user volume
- [ ] **Disaster Recovery:** Backup/restore procedures tested
- [ ] **Documentation:** All operational docs updated
- [ ] **Team Training:** Operations team trained on monitoring and troubleshooting

### Go-Live Execution
1. [ ] **DNS Update:** Point domain to Cloud Run service (if applicable)
2. [ ] **SSL Certificate:** Verify HTTPS working correctly
3. [ ] **Monitoring:** Confirm all alerts are active
4. [ ] **Performance:** Baseline performance metrics captured
5. [ ] **Communication:** Stakeholders notified of go-live

## Post-Deployment Monitoring (First 24 Hours)

### Critical Metrics to Watch
- [ ] **Response Times:** API endpoints < 2 seconds
- [ ] **Error Rates:** < 1% error rate
- [ ] **Availability:** > 99.9% uptime
- [ ] **Cost:** Within expected budget range

### Incident Response
- [ ] **On-Call Schedule:** Established for first week
- [ ] **Escalation Path:** Clear escalation procedures
- [ ] **Rollback Plan:** Tested rollback to previous version
- [ ] **Communication Plan:** Status page and user communication ready

## Troubleshooting Guide

### Common Issues & Solutions

#### Service Won't Start
```bash
# Check Cloud Run logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Check service configuration
gcloud run services describe acpf-mvp-apiserver --region=REGION
```

#### Database Connection Issues
```bash
# Verify Firestore permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID

# Test Firestore connection
python -c "from google.cloud import firestore; db = firestore.Client(); print('Connection successful')"
```

#### Secret Manager Access Issues
```bash
# Test secret access
gcloud secrets versions access latest --secret="AI_CONTENT_FACTORY_API_KEY"

# Check service account permissions
gcloud iam service-accounts get-iam-policy cloud-run-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

#### API Performance Issues
```bash
# Check Cloud Run metrics
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"

# Analyze request patterns
gcloud logs read "resource.type=cloud_run_revision AND textPayload:'POST /api/v1/jobs'" --limit=100
```

## Rollback Procedures

### Emergency Rollback
1. **Identify Previous Working Image:**
   ```bash
   gcloud container images list-tags REGION-docker.pkg.dev/YOUR_PROJECT_ID/acpf-mvp-repository/acpf-mvp-apiserver
   ```

2. **Deploy Previous Version:**
   ```bash
   gcloud run deploy acpf-mvp-apiserver \
     --image REGION-docker.pkg.dev/YOUR_PROJECT_ID/acpf-mvp-repository/acpf-mvp-apiserver:PREVIOUS_TAG \
     --platform managed --region REGION
   ```

3. **Verify Rollback:**
   - Test critical endpoints
   - Check application logs
   - Verify user functionality

### Database Rollback (If Needed)
- Firestore: Use automated backups or export/import procedures
- Secrets: Revert to previous secret versions if necessary

---

## Sign-off

### Deployment Team Sign-off
- [ ] **Technical Lead:** ___________________ Date: ___________
- [ ] **DevOps Engineer:** ___________________ Date: ___________  
- [ ] **Security Review:** ___________________ Date: ___________
- [ ] **Project Manager:** ___________________ Date: ___________

### Production Ready Confirmation
- [ ] All checklist items completed
- [ ] Security review passed
- [ ] Performance benchmarks met
- [ ] Monitoring and alerting active
- [ ] Team trained and ready for operations

**Final Go-Live Approval:** ___________________ Date: ___________

---

**Document Version:** 1.0  
**Last Updated:** 2025-05-30  
**Next Review Date:** TBD 