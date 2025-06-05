# Phase 5: Production Deployment & Operations Plan

**Project**: AI Content Factory
**Phase Start Date**: June 3, 2025
**Status**: 🚀 READY TO BEGIN
**Prerequisites**: Phase 4 Complete (97.5%), Production Readiness Approved (99/100)

## Executive Summary

Phase 5 represents the culmination of all development efforts, transitioning the AI Content Factory from a production-ready state to live production operations. This phase focuses on systematic deployment, verification, and operational handoff.

## Phase 5 Objectives

1. **Infrastructure Deployment**: Deploy all GCP resources via Terraform
2. **Application Deployment**: Deploy containerized application to Cloud Run
3. **Configuration & Secrets**: Set up production secrets and configurations
4. **Verification & Testing**: Validate production deployment
5. **Monitoring Activation**: Enable all monitoring and alerting
6. **Operational Handoff**: Team training and documentation

## Deployment Architecture Overview

```
Production Environment (GCP)
├── Core Services
│   ├── Cloud Run (FastAPI application)
│   ├── API Gateway (rate limiting, authentication)
│   └── Cloud Load Balancer
├── Data Layer
│   ├── Firestore (job persistence)
│   ├── Cloud Storage (content storage)
│   └── Redis (Memorystore for caching)
├── Processing Layer
│   ├── Cloud Tasks (async job queue)
│   ├── Cloud Workflows (orchestration)
│   └── Vertex AI (Gemini API)
├── Security Layer
│   ├── Secret Manager (API keys, credentials)
│   ├── IAM (service accounts, roles)
│   └── Cloud Armor (DDoS protection)
└── Monitoring Layer
    ├── Cloud Monitoring (metrics, alerts)
    ├── Cloud Logging (centralized logs)
    └── Sentry (error tracking)
```

## Detailed Action Plan

### Stage 1: Pre-Deployment Preparation (Day 1)

#### 1.1 Environment Setup
- [ ] Create production GCP project (if not exists)
- [ ] Configure project billing and quotas
- [ ] Set up production branch protection in GitHub
- [ ] Create production environment in GitHub

#### 1.2 Access & Permissions
- [ ] Verify deployment service account permissions
- [ ] Configure GitHub Actions secrets for production
- [ ] Set up team access to production project
- [ ] Document emergency access procedures

#### 1.3 Configuration Review
- [ ] Review all Terraform variables for production
- [ ] Validate production domain/URL settings
- [ ] Confirm API Gateway configuration
- [ ] Review resource sizing (Cloud Run, Redis, etc.)

### Stage 2: Infrastructure Deployment (Day 1-2)

#### 2.1 Terraform Deployment
```bash
# Initialize Terraform with production backend
cd iac/
terraform init -backend-config="bucket=acpf-prod-terraform-state"

# Create Terraform workspace for production
terraform workspace new production || terraform workspace select production

# Review planned changes
terraform plan -var-file="environments/production.tfvars" -out=tfplan

# Apply infrastructure
terraform apply tfplan
```

#### 2.2 Core Infrastructure Components
- [ ] Cloud Run service (with proper scaling)
- [ ] API Gateway with rate limiting
- [ ] Firestore database with indexes
- [ ] Redis instance (Memorystore)
- [ ] Cloud Tasks queues
- [ ] Cloud Storage buckets
- [ ] VPC and networking

#### 2.3 Security Infrastructure
- [ ] IAM roles and service accounts
- [ ] Secret Manager secrets
- [ ] Cloud Armor policies
- [ ] SSL certificates

### Stage 3: Secrets & Configuration (Day 2)

#### 3.1 Secret Manager Setup
```bash
# Create production secrets
gcloud secrets create api-key --data-file=- <<< "$(openssl rand -base64 32)"
gcloud secrets create jwt-secret-key --data-file=- <<< "$(openssl rand -base64 64)"
gcloud secrets create elevenlabs-api-key --data-file=api-keys/elevenlabs.txt
gcloud secrets create sentry-dsn --data-file=monitoring/sentry-dsn.txt

# Grant Cloud Run service account access
gcloud secrets add-iam-policy-binding api-key \
  --member="serviceAccount:acpf-prod-cloudrun@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### 3.2 Environment Variables
- [ ] Configure Cloud Run environment variables
- [ ] Set production feature flags
- [ ] Configure rate limiting thresholds
- [ ] Set monitoring endpoints

### Stage 4: Application Deployment (Day 2)

#### 4.1 Container Registry Setup
```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker REGION-docker.pkg.dev

# Build and push production image
docker build -t REGION-docker.pkg.dev/PROJECT_ID/acpf-prod/api:v1.0.0 .
docker push REGION-docker.pkg.dev/PROJECT_ID/acpf-prod/api:v1.0.0
```

#### 4.2 Cloud Run Deployment
```bash
# Deploy to Cloud Run
gcloud run deploy acpf-prod-api \
  --image=REGION-docker.pkg.dev/PROJECT_ID/acpf-prod/api:v1.0.0 \
  --platform=managed \
  --region=REGION \
  --service-account=acpf-prod-cloudrun@PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars="ENVIRONMENT=production" \
  --cpu=2 \
  --memory=4Gi \
  --min-instances=2 \
  --max-instances=100 \
  --concurrency=80
```

#### 4.3 API Gateway Configuration
- [ ] Deploy OpenAPI specification
- [ ] Configure rate limiting rules
- [ ] Set up custom domain
- [ ] Enable CORS policies

### Stage 5: Monitoring & Alerting Setup (Day 3)

#### 5.1 Cloud Monitoring Configuration
- [ ] Deploy alert policies from Terraform
- [ ] Configure uptime checks
- [ ] Set up custom dashboards
- [ ] Configure log-based metrics

#### 5.2 Alert Policy Verification ⚠️
**This completes the remaining 2.5% from Phase 4**
```bash
# Verify alert policies are active
gcloud alpha monitoring policies list --filter="displayName:acpf-prod"

# Test alert notifications
gcloud monitoring channels list
gcloud monitoring channels test-notification-channel CHANNEL_ID
```

#### 5.3 Sentry Integration
- [ ] Verify Sentry DSN configuration
- [ ] Test error reporting
- [ ] Configure release tracking
- [ ] Set up performance monitoring

### Stage 6: Production Validation (Day 3)

#### 6.1 Health Checks
```bash
# Basic health check
curl https://api.ai-content-factory.com/health

# Comprehensive health check
curl https://api.ai-content-factory.com/health/comprehensive
```

#### 6.2 E2E Test Execution
```bash
# Run production E2E tests
export API_BASE_URL=https://api.ai-content-factory.com
export API_KEY=$(gcloud secrets versions access latest --secret="api-key")
pytest tests/e2e/ -v --env=production
```

#### 6.3 Performance Validation
- [ ] Load test with expected traffic
- [ ] Verify response times (<2s)
- [ ] Check cache hit ratios
- [ ] Monitor resource utilization

### Stage 7: Operational Handoff (Day 4)

#### 7.1 Documentation Review
- [ ] Update operational runbooks
- [ ] Document incident response procedures
- [ ] Create troubleshooting guides
- [ ] Update architecture diagrams

#### 7.2 Team Training
- [ ] Conduct deployment walkthrough
- [ ] Review monitoring dashboards
- [ ] Practice incident response
- [ ] Demo administrative tasks

#### 7.3 Access Management
- [ ] Set up on-call rotations
- [ ] Configure PagerDuty integration
- [ ] Document escalation procedures
- [ ] Create access request process

### Stage 8: Go-Live & Monitoring (Day 5)

#### 8.1 Traffic Migration
- [ ] Update DNS records
- [ ] Configure traffic splitting (if applicable)
- [ ] Monitor error rates
- [ ] Check performance metrics

#### 8.2 Post-Deployment Monitoring
- [ ] 24-hour monitoring period
- [ ] Review all metrics and logs
- [ ] Address any issues
- [ ] Document lessons learned

## Rollback Plan

### Automated Rollback Triggers
- Error rate >5% for 5 minutes
- Response time >5s for 5 minutes
- Health check failures

### Manual Rollback Procedure
```bash
# Rollback Cloud Run to previous revision
gcloud run services update-traffic acpf-prod-api \
  --to-revisions=PREVIOUS_REVISION=100

# Rollback infrastructure if needed
cd iac/
terraform workspace select production
terraform apply -var-file="environments/production.tfvars" \
  -target=module.affected_module
```

## Success Criteria

### Deployment Success
- [ ] All infrastructure deployed successfully
- [ ] Application responding to health checks
- [ ] E2E tests passing in production
- [ ] Monitoring and alerts active
- [ ] No critical errors in first 24 hours

### Performance Targets
- [ ] API response time <2s (p99)
- [ ] Content generation <30s average
- [ ] Cache hit ratio >75%
- [ ] Error rate <1%
- [ ] Uptime >99.9%

## Risk Mitigation

### Identified Risks
1. **Database Migration Issues**
   - Mitigation: Firestore handles schema flexibly
   - Backup: Export data before deployment

2. **API Gateway Configuration**
   - Mitigation: Test in staging first
   - Backup: Direct Cloud Run access available

3. **Secret Management**
   - Mitigation: Verify all secrets before deployment
   - Backup: Manual secret injection if needed

4. **Traffic Spike**
   - Mitigation: Auto-scaling configured
   - Backup: Manual scaling available

## Post-Deployment Tasks

### Week 1
- [ ] Monitor all metrics daily
- [ ] Review cost optimization opportunities
- [ ] Gather user feedback
- [ ] Plan Phase 6 enhancements

### Week 2-4
- [ ] Implement minor improvements from Phase 4
- [ ] Optimize based on production data
- [ ] Conduct security review
- [ ] Plan feature roadmap

## Communication Plan

### Stakeholder Updates
- Pre-deployment notification (Day 0)
- Daily status during deployment
- Go-live announcement
- Weekly status reports

### Incident Communication
- Slack: #acpf-production-alerts
- Email: acpf-oncall@company.com
- Escalation: CTO after 30 minutes

## Appendix: Quick Reference

### Key Commands
```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Check service status
gcloud run services describe acpf-prod-api --region=REGION

# Monitor active requests
gcloud monitoring time-series list --filter='metric.type="run.googleapis.com/request_count"'

# Update traffic split
gcloud run services update-traffic acpf-prod-api --to-latest
```

### Important URLs
- Production API: https://api.ai-content-factory.com
- Health Check: https://api.ai-content-factory.com/health
- API Docs: https://api.ai-content-factory.com/docs
- Monitoring: https://console.cloud.google.com/monitoring

### Emergency Contacts
- On-Call Engineer: Via PagerDuty
- Platform Team: platform-team@company.com
- Security Team: security@company.com
- CTO: cto@company.com

---

**Document Status**: Ready for Execution
**Last Updated**: June 3, 2025
**Next Review**: Post-deployment retrospective
