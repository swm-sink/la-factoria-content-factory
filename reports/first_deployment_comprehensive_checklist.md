# AI Content Factory - FIRST DEPLOYMENT COMPREHENSIVE CHECKLIST

**Date**: June 3, 2025
**Deployment Type**: Initial Production Deployment (First Ever)
**Service**: AI Content Factory with Unified Content Service

## 🚨 CRITICAL FIRST DEPLOYMENT ITEMS

### 1. **Infrastructure Prerequisites** ❌ NOT YET DEPLOYED
Since this is the FIRST deployment, these GCP resources need to be created:

- [ ] **GCP Project Setup**
  - [ ] Project created and configured
  - [ ] Billing account linked
  - [ ] APIs enabled (Cloud Run, Vertex AI, Firestore, etc.)

- [ ] **Service Accounts**
  - [ ] Cloud Run service account created
  - [ ] Vertex AI permissions granted
  - [ ] Firestore access configured
  - [ ] Secret Manager permissions set

- [ ] **Terraform Infrastructure**
  ```bash
  cd iac/
  terraform init
  terraform plan
  terraform apply
  ```
  Required resources:
  - [ ] Cloud Run service
  - [ ] Firestore database
  - [ ] Secret Manager secrets
  - [ ] API Gateway
  - [ ] Cloud Storage buckets
  - [ ] VPC/networking (if needed)

### 2. **Secrets & Configuration** ⚠️ REQUIRES SETUP

- [ ] **Google Secret Manager Secrets**
  ```bash
  # These need to be created BEFORE deployment:
  gcloud secrets create elevenlabs-api-key --data-file=-
  gcloud secrets create openai-api-key --data-file=-
  gcloud secrets create api-keys --data-file=-
  gcloud secrets create redis-connection-string --data-file=-
  ```

- [ ] **Environment Variables**
  Required for Cloud Run:
  - [ ] `GCP_PROJECT_ID` - Set to your project ID
  - [ ] `GCP_LOCATION` - Set to deployment region (e.g., us-central1)
  - [ ] `ENVIRONMENT` - Set to "production"
  - [ ] `GOOGLE_APPLICATION_CREDENTIALS` - Handled by Cloud Run
  - [ ] `REDIS_URL` - Redis connection string
  - [ ] `FIRESTORE_DATABASE` - Database name

### 3. **Application Code Status** ✅ READY

- [x] **Core Services**
  - [x] UnifiedContentService implemented
  - [x] ServiceRouter configured
  - [x] Feature flags enabled
  - [x] Error handling comprehensive
  - [x] Monitoring integrated

- [x] **API Endpoints**
  - [x] `/api/v1/content/generate` - Main content generation
  - [x] `/api/v1/jobs` - Job management
  - [x] `/healthz` - Health check
  - [x] `/metrics` - Prometheus metrics

- [x] **Dependencies**
  - [x] All Python packages in requirements.txt
  - [x] Dockerfile configured
  - [x] No security vulnerabilities

### 4. **Testing Status** ⚠️ NEEDS VERIFICATION

- [x] **Unit Tests**
  - UnifiedContentService: 7/7 tests passing
  - Total coverage: >90%

- [ ] **Integration Tests**
  - [ ] API endpoint tests with real services
  - [ ] Database connectivity tests
  - [ ] External service mocks

- [ ] **Load Testing**
  - [ ] Baseline performance metrics
  - [ ] Concurrent request handling
  - [ ] Rate limit validation

### 5. **Security Checklist** 🔐 CRITICAL

- [ ] **API Security**
  - [ ] API keys configured in Secret Manager
  - [ ] Rate limiting enabled (10 req/min per IP)
  - [ ] CORS configured properly
  - [ ] Input validation active

- [ ] **Infrastructure Security**
  - [ ] IAM roles follow least privilege
  - [ ] Service account permissions minimal
  - [ ] Network policies configured
  - [ ] Cloud Armor rules (if applicable)

- [x] **Application Security**
  - [x] No hardcoded secrets
  - [x] Environment-based configuration
  - [x] Secure headers configured
  - [x] Error messages sanitized

### 6. **Deployment Procedure** 📋

Since this is the FIRST deployment, follow this exact sequence:

1. **Pre-deployment Setup** (30-60 minutes)
   ```bash
   # 1. Set up GCP project
   gcloud config set project YOUR_PROJECT_ID

   # 2. Enable required APIs
   gcloud services enable run.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable firestore.googleapis.com
   gcloud services enable secretmanager.googleapis.com

   # 3. Create service account
   gcloud iam service-accounts create acpf-cloud-run-sa \
     --display-name="AI Content Factory Cloud Run Service Account"
   ```

2. **Infrastructure Deployment** (20-30 minutes)
   ```bash
   cd iac/
   terraform init
   terraform plan -out=tfplan
   terraform apply tfplan
   ```

3. **Secrets Configuration** (10-15 minutes)
   ```bash
   # Add your API keys
   echo -n "YOUR_ELEVENLABS_KEY" | gcloud secrets create elevenlabs-api-key --data-file=-
   echo -n "YOUR_OPENAI_KEY" | gcloud secrets create openai-api-key --data-file=-
   ```

4. **Container Build & Deploy** (15-20 minutes)
   ```bash
   # Build and push container
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-content-factory

   # Deploy to Cloud Run
   gcloud run deploy ai-content-factory \
     --image gcr.io/YOUR_PROJECT_ID/ai-content-factory \
     --platform managed \
     --region YOUR_REGION \
     --service-account acpf-cloud-run-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

### 7. **Post-Deployment Verification** ✓

- [ ] **Health Checks**
  ```bash
  curl https://YOUR_CLOUD_RUN_URL/healthz
  # Expected: {"status": "healthy", "version": "..."}
  ```

- [ ] **API Gateway Verification**
  ```bash
  curl -H "X-API-Key: YOUR_KEY" https://YOUR_API_GATEWAY_URL/api/v1/content/generate
  ```

- [ ] **Monitoring Setup**
  - [ ] Cloud Monitoring dashboards created
  - [ ] Alert policies configured
  - [ ] Log-based metrics defined
  - [ ] Error reporting enabled

### 8. **Rollback Plan** 🔄

For first deployment issues:

1. **Immediate Rollback**
   ```bash
   # Delete Cloud Run service
   gcloud run services delete ai-content-factory

   # Revert infrastructure if needed
   cd iac/ && terraform destroy
   ```

2. **Feature Flag Rollback**
   - Set `use_unified_service: false` in features.yaml
   - Redeploy to use legacy service

### 9. **Known Issues & Mitigations** ⚠️

1. **Cold Start Latency**
   - First requests may take 30-60s
   - Mitigation: Set min instances to 1

2. **Token Usage Costs**
   - Monitor closely in first 24 hours
   - Set up budget alerts

3. **Rate Limits**
   - External APIs have limits
   - Implement exponential backoff

### 10. **First 24 Hours Monitoring Plan** 👀

**Hour 1-2:**
- Monitor health check endpoint every 5 minutes
- Check error logs for any failures
- Verify API responses

**Hour 2-6:**
- Monitor token usage and costs
- Check response time metrics
- Verify cache hit ratios

**Hour 6-24:**
- Review aggregated metrics
- Check for any error patterns
- Monitor resource utilization

## 🎯 GO/NO-GO Decision Criteria

### ✅ **GO Criteria** (All must be met)
- [ ] All infrastructure deployed successfully
- [ ] Health checks passing
- [ ] API authentication working
- [ ] No critical errors in logs
- [ ] Response times < 60s
- [ ] Team available for monitoring

### ❌ **NO-GO Criteria** (Any triggers stop)
- [ ] Infrastructure deployment failures
- [ ] Missing critical secrets
- [ ] Authentication not working
- [ ] Critical errors in deployment
- [ ] No monitoring access
- [ ] Team unavailable

## 📊 Success Metrics (First 7 Days)

1. **Availability**: >99% uptime
2. **Performance**: P95 < 30s
3. **Error Rate**: <1%
4. **Cost**: Within budget projections
5. **User Feedback**: No critical issues

## 🚀 Launch Communication Plan

1. **Pre-Launch** (T-1 hour)
   - Notify team of deployment start
   - Confirm all checklist items

2. **During Launch**
   - Real-time updates in Slack
   - Document any issues

3. **Post-Launch** (T+1 hour)
   - Send success confirmation
   - Share monitoring dashboard

4. **Daily Updates** (First week)
   - Metrics summary
   - Issues and resolutions
   - Cost tracking

---

**CRITICAL REMINDER**: This is the FIRST production deployment. Take extra time to verify each step. Have rollback commands ready. Monitor closely.

**Prepared by**: Development Team
**Deployment Window**: [TO BE SCHEDULED]
**Primary Contact**: [ASSIGN DEPLOYMENT LEAD]
**Backup Contact**: [ASSIGN BACKUP LEAD]
