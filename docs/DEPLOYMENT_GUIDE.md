# La Factoria Production Deployment Guide

**Version**: 1.0.0  
**Last Updated**: 2025-08-08  
**Platform**: Railway

## 📋 Pre-Deployment Checklist

### ✅ Core Requirements
- [ ] Python 3.11+ environment
- [ ] Railway account created
- [ ] Git repository initialized
- [ ] API keys obtained (OpenAI/Anthropic/etc.)
- [ ] Domain name (optional)

### ✅ Code Readiness
- [ ] All tests passing (91.4% pass rate achieved)
- [ ] Health monitoring endpoints verified
- [ ] Database schema validated
- [ ] Environment variables documented
- [ ] Frontend assets optimized

## 🚀 Quick Start Deployment

### Option 1: One-Click Railway Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Option 2: Railway CLI Deployment

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Create new project
railway init

# 4. Add PostgreSQL database
railway add --database postgres

# 5. Deploy application
railway up

# 6. View deployment
railway open
```

## 📦 Detailed Deployment Steps

### Step 1: Prepare Codebase

```bash
# Clone repository
git clone <your-repo-url>
cd la-factoria

# Verify railway.toml exists
cat railway.toml

# Check requirements.txt is up to date
pip freeze > requirements.txt

# Ensure migrations are ready
ls migrations/001_initial_schema.sql
```

### Step 2: Configure Railway Project

```bash
# Initialize Railway project
railway init

# Set project name
railway project name "la-factoria-production"

# Add PostgreSQL addon
railway add --database postgres

# Optional: Add Redis for caching
railway add --database redis
```

### Step 3: Set Environment Variables

```bash
# Core Configuration
railway variables --set "PYTHON_VERSION=3.11"
railway variables --set "ENVIRONMENT=production"
railway variables --set "API_SECRET_KEY=$(openssl rand -hex 32)"
railway variables --set "DEBUG=false"

# Database (automatically set by Railway)
# DATABASE_URL will be auto-configured

# AI Provider Keys
railway variables --set "OPENAI_API_KEY=sk-..."
railway variables --set "ANTHROPIC_API_KEY=sk-ant-..."
railway variables --set "GOOGLE_CLOUD_PROJECT=your-project"

# Optional: Monitoring
railway variables --set "LANGFUSE_PUBLIC_KEY=..."
railway variables --set "LANGFUSE_SECRET_KEY=..."

# Quality Thresholds
railway variables --set "QUALITY_THRESHOLD_OVERALL=0.70"
railway variables --set "QUALITY_THRESHOLD_EDUCATIONAL=0.75"
railway variables --set "QUALITY_THRESHOLD_FACTUAL=0.85"
```

### Step 4: Deploy Application

```bash
# Deploy to Railway
railway up

# Monitor deployment
railway logs --tail

# Check deployment status
railway status

# Get deployment URL
railway open
```

### Step 5: Database Migration

```bash
# Connect to Railway PostgreSQL
railway run psql $DATABASE_URL

# Apply database schema
railway run psql $DATABASE_URL < migrations/001_initial_schema.sql

# Verify tables created
railway run psql $DATABASE_URL -c "\dt"
```

### Step 6: Verify Deployment

```bash
# Check health endpoint
curl https://your-app.railway.app/api/v1/health

# Test readiness probe
curl https://your-app.railway.app/api/v1/ready

# Verify liveness probe
curl https://your-app.railway.app/api/v1/live

# Access frontend
open https://your-app.railway.app
```

## 🔧 Configuration Details

### Railway.toml Configuration

```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn src.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 30
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 3

[environments.production]
  [environments.production.build]
  nixpacksPlan = """
    [phases.setup]
    nixPkgs = ['python311', 'gcc']
  """
```

### Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes* | PostgreSQL connection string | Auto-set by Railway |
| `API_SECRET_KEY` | Yes | JWT signing key | Random 32-byte hex |
| `ENVIRONMENT` | Yes | Deployment environment | `production` |
| `OPENAI_API_KEY` | No** | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | No** | Anthropic API key | `sk-ant-...` |
| `REDIS_URL` | No | Redis cache connection | Auto-set if added |
| `ALLOWED_ORIGINS` | No | CORS allowed origins | `https://yourdomain.com` |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | No | API rate limiting | `100` |

*Auto-configured by Railway when PostgreSQL addon is added
**At least one AI provider key is required

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check DATABASE_URL is set
railway variables

# Test connection
railway run psql $DATABASE_URL -c "SELECT 1"

# Re-apply migrations if needed
railway run psql $DATABASE_URL < migrations/001_initial_schema.sql
```

#### 2. Health Check Failing
```bash
# Check application logs
railway logs --tail 100

# Verify health endpoint locally
railway run curl localhost:8000/api/v1/health

# Check for port binding issues
railway variables --set "PORT=8000"
```

#### 3. AI Provider Issues
```bash
# Verify API keys are set
railway variables | grep API_KEY

# Test AI provider directly
railway run python -c "import openai; print('OpenAI OK')"
```

#### 4. Static Files Not Serving
```bash
# Ensure static directory is included
railway run ls -la static/

# Check FastAPI static mount
railway logs | grep "Static files"
```

## 📊 Monitoring & Maintenance

### Health Monitoring

Railway automatically monitors your application using the configured health check:

- **Endpoint**: `/api/v1/health`
- **Frequency**: Every 30 seconds
- **Timeout**: 30 seconds
- **Restart Policy**: On failure, max 3 retries

### Viewing Metrics

```bash
# Application logs
railway logs --tail 100

# Database metrics
railway database metrics postgres

# Resource usage
railway metrics
```

### Scaling

```bash
# Manual scaling (Railway Pro)
railway scale --replicas 3

# Automatic scaling based on CPU/Memory
# Configure in Railway dashboard
```

## 🔄 Updating Deployment

### Standard Update Process

```bash
# 1. Make code changes locally
git add .
git commit -m "Update: Description of changes"
git push origin main

# 2. Deploy to Railway
railway up

# 3. Monitor deployment
railway logs --tail

# 4. Verify update
curl https://your-app.railway.app/api/v1/health
```

### Database Migration Updates

```bash
# Create new migration file
echo "ALTER TABLE ..." > migrations/002_update.sql

# Apply migration
railway run psql $DATABASE_URL < migrations/002_update.sql

# Verify changes
railway run psql $DATABASE_URL -c "\d+ table_name"
```

## 🔒 Security Best Practices

1. **API Keys Management**
   - Never commit API keys to repository
   - Use Railway's environment variables
   - Rotate keys regularly
   - Use different keys for staging/production

2. **Database Security**
   - Railway manages database security
   - Use connection pooling
   - Enable SSL connections (default)
   - Regular backups (Railway Pro)

3. **Application Security**
   - Keep dependencies updated
   - Use rate limiting
   - Implement CORS properly
   - Monitor for suspicious activity

## 🌐 Custom Domain Setup

```bash
# 1. Add custom domain in Railway dashboard
# Railway Dashboard → Settings → Domains

# 2. Configure DNS (at your domain provider)
# Add CNAME record:
# Name: @ or subdomain
# Value: your-app.up.railway.app

# 3. Enable HTTPS (automatic)
# Railway provides free SSL certificates

# 4. Update CORS settings
railway variables --set "ALLOWED_ORIGINS=https://yourdomain.com"
```

## 📱 Post-Deployment Checklist

- [ ] Health check passing
- [ ] All content types generating
- [ ] Database connected and migrations applied
- [ ] AI providers configured and working
- [ ] Frontend accessible and functional
- [ ] API documentation available at `/docs`
- [ ] Monitoring dashboard accessible
- [ ] Rate limiting active
- [ ] Error tracking configured
- [ ] Backup strategy in place

## 📞 Support Resources

- **Railway Documentation**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **La Factoria Issues**: GitHub Issues page
- **API Documentation**: https://your-app.railway.app/docs

## 🎯 Performance Targets

After deployment, your application should meet these targets:

- **Response Time**: <200ms for API endpoints
- **Content Generation**: <30s for all content types
- **Uptime**: 99%+ availability
- **Health Check**: 100% success rate
- **Error Rate**: <1% for API requests

---

*For additional deployment options (Docker, Kubernetes, AWS), see the extended deployment documentation.*