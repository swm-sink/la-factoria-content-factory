# La Factoria Production Operations Runbook

## 🚀 Deployment Status
- **Platform**: Railway
- **Environment**: Production  
- **Version**: 1.0.0
- **Last Updated**: 2025-08-04

---

## 📊 Monitoring & Health Checks

### Primary Monitoring Endpoints

#### Health Check
```bash
curl https://your-app.railway.app/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-04T...",
  "version": "1.0.0",
  "environment": "production"
}
```

#### Detailed Health Check
```bash
curl https://your-app.railway.app/api/v1/health/detailed
```
**Monitors:**
- Database connectivity
- AI provider availability
- System resource usage
- Application metrics
- Quality assessment pipeline

#### System Metrics
```bash
curl https://your-app.railway.app/api/v1/metrics
```

#### Educational Metrics
```bash
curl https://your-app.railway.app/api/v1/metrics/educational
```

#### Visual Dashboard
Access: `https://your-app.railway.app/static/monitor.html`
- Real-time system health
- Resource utilization
- Educational metrics
- Content generation stats
- Auto-refresh every 30 seconds

---

## 🎯 Performance Targets & SLAs

### Response Time Targets
- **Health Check**: <100ms (99th percentile)
- **API Endpoints**: <200ms (95th percentile)
- **Content Generation**: <30s end-to-end
- **Quality Assessment**: <5s completion
- **Database Queries**: <50ms average

### Quality Thresholds
- **Overall Quality**: ≥0.70 minimum
- **Educational Value**: ≥0.75 minimum
- **Factual Accuracy**: ≥0.85 minimum
- **Generation Success Rate**: >95%

### Availability Targets
- **System Uptime**: 99%+ monthly
- **API Availability**: 99.5%+ monthly
- **Educational Content Generation**: 99%+ success rate

---

## 📈 Key Performance Indicators (KPIs)

### Educational Effectiveness
- Quality score distribution
- Content type popularity
- User satisfaction ratings
- Learning outcome correlation

### Technical Performance
- API response times
- Content generation latency
- System resource utilization
- Error rates and types

### Business Metrics
- Content generation volume
- User engagement patterns
- AI provider cost optimization
- Feature usage analytics

---

## 🚨 Alerting & Incident Response

### Critical Alerts
**Trigger immediate response:**
- API downtime >2 minutes
- Health check failures
- Database connectivity issues
- Quality score degradation <0.65
- Response time >1000ms sustained

### Warning Alerts
**Monitor and investigate:**
- CPU usage >80% for 10 minutes
- Memory usage >80% for 10 minutes
- Quality score <0.70 average for 1 hour
- Generation success rate <90%

### Alert Channels
- Railway dashboard notifications
- Health check monitoring
- Custom alerting via monitoring endpoints

---

## 🔧 Troubleshooting Guide

### Common Issues

#### 1. 502 Bad Gateway
**Symptoms:** Application not responding
**Investigation:**
```bash
railway logs --tail 100
```
**Common Causes:**
- Environment variables missing
- Database connection failure
- Application startup errors
- Memory/CPU exhaustion

**Resolution:**
1. Check environment variables in Railway dashboard
2. Verify DATABASE_URL is set
3. Check AI provider API keys
4. Review application logs for specific errors

#### 2. Database Connection Errors
**Symptoms:** Database health check failing
**Investigation:**
```bash
railway connect
\dt  # List tables
```
**Resolution:**
1. Verify DATABASE_URL environment variable
2. Check Railway PostgreSQL service status
3. Run database migration if needed:
```bash
railway run psql -d $DATABASE_URL -f migrations/001_initial_schema.sql
```

#### 3. AI Provider Errors
**Symptoms:** Content generation failures
**Investigation:**
- Check `/api/v1/health/detailed` for AI provider status
- Review logs for API key errors
- Verify rate limits not exceeded

**Resolution:**
1. Verify AI provider API keys in Railway dashboard
2. Check provider status pages
3. Implement provider failover if needed

#### 4. Quality Assessment Failures
**Symptoms:** Quality scores consistently low or errors
**Investigation:**
- Check educational metrics endpoint
- Review content generation logs
- Verify quality thresholds configuration

**Resolution:**
1. Review quality assessment configuration
2. Check for prompt template issues
3. Validate content complexity against audience

#### 5. Performance Degradation
**Symptoms:** Slow response times
**Investigation:**
- Monitor system metrics endpoint
- Check database query performance
- Review resource utilization

**Resolution:**
1. Scale resources if needed
2. Optimize database queries
3. Implement caching where appropriate
4. Review AI provider response times

---

## 🛠️ Maintenance Procedures

### Weekly Maintenance
- [ ] Review performance metrics
- [ ] Check error logs and patterns
- [ ] Validate quality score trends
- [ ] Monitor resource utilization
- [ ] Review user feedback

### Monthly Maintenance
- [ ] Database performance optimization
- [ ] Security updates and patches
- [ ] Capacity planning review
- [ ] Cost optimization analysis
- [ ] Backup verification

### Quarterly Maintenance
- [ ] Full system performance review
- [ ] Educational effectiveness analysis
- [ ] Infrastructure scaling assessment
- [ ] Disaster recovery testing
- [ ] Security audit

---

## 📊 Database Management

### Database Access
```bash
# Connect to production database
railway connect

# Run queries
psql $DATABASE_URL
```

### Common Database Operations

#### Check System Health
```sql
-- Total content generated
SELECT COUNT(*) as total_content FROM educational_content;

-- Recent activity (last 24 hours)
SELECT COUNT(*) as recent_content 
FROM educational_content 
WHERE created_at >= NOW() - INTERVAL '24 hours';

-- Quality metrics
SELECT 
    AVG(quality_score) as avg_quality,
    AVG(educational_effectiveness) as avg_educational,
    AVG(factual_accuracy) as avg_accuracy
FROM educational_content 
WHERE created_at >= NOW() - INTERVAL '7 days';
```

#### Content Type Analysis
```sql
SELECT 
    content_type,
    COUNT(*) as count,
    AVG(quality_score) as avg_quality
FROM educational_content 
GROUP BY content_type 
ORDER BY count DESC;
```

#### Performance Analysis
```sql
SELECT 
    content_type,
    AVG(generation_duration_ms) as avg_duration,
    MIN(generation_duration_ms) as min_duration,
    MAX(generation_duration_ms) as max_duration
FROM educational_content 
WHERE generation_duration_ms IS NOT NULL
GROUP BY content_type;
```

### Backup Procedures
- **Automatic**: Railway handles automated backups
- **Manual**: Use Railway CLI for on-demand backups
- **Verification**: Monthly backup restore testing

---

## 🔐 Security Operations

### API Security
- **Authentication**: Bearer token via LA_FACTORIA_API_KEY
- **Rate Limiting**: 60 requests/minute, 100 generations/hour
- **Input Validation**: Comprehensive sanitization
- **HTTPS**: Enforced via Railway

### Data Protection
- **PII Handling**: Minimal collection, secure processing
- **Content Sanitization**: AI-generated content filtering
- **GDPR Compliance**: User data deletion capabilities
- **Audit Logging**: API usage tracking

### Security Monitoring
- **Failed Authentication**: Monitor 401 responses
- **Rate Limit Violations**: Track 429 responses
- **Suspicious Patterns**: Unusual request patterns
- **Input Validation**: Monitor validation failures

---

## 💰 Cost Management

### Resource Monitoring
- **Compute**: Track CPU/memory usage
- **Database**: Monitor storage and query performance
- **AI Providers**: Track token usage and costs
- **Bandwidth**: Monitor data transfer

### Cost Optimization
- **AI Provider Selection**: Route to cost-effective providers
- **Caching**: Implement intelligent caching
- **Resource Scaling**: Right-size compute resources
- **Query Optimization**: Optimize database performance

---

## 📞 Emergency Procedures

### Critical System Failure
1. **Assessment**: Check health endpoints and logs
2. **Communication**: Update stakeholders
3. **Mitigation**: Implement immediate fixes
4. **Recovery**: Restore service functionality
5. **Post-Incident**: Conduct thorough review

### Data Loss Prevention
1. **Immediate Backup**: Trigger manual backup
2. **Isolation**: Prevent further data loss
3. **Recovery**: Restore from most recent backup
4. **Validation**: Verify data integrity
5. **Documentation**: Record incident details

### Security Incident
1. **Containment**: Isolate affected systems
2. **Assessment**: Determine scope and impact
3. **Mitigation**: Implement security measures
4. **Recovery**: Restore secure operations
5. **Review**: Analyze and improve security

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Code review completed
- [ ] Tests passing
- [ ] Security scan completed
- [ ] Performance testing done
- [ ] Database migration ready

### Deployment
- [ ] Environment variables updated
- [ ] Railway deployment triggered
- [ ] Health checks passing
- [ ] Database migration executed
- [ ] Smoke tests completed

### Post-Deployment
- [ ] All endpoints responding
- [ ] Content generation working
- [ ] Quality assessment functional
- [ ] Monitoring active
- [ ] Performance within targets

---

## 📖 Additional Resources

### Documentation
- **API Documentation**: `/docs` (staging) or Railway logs
- **Database Schema**: `migrations/001_initial_schema.sql`
- **Architecture**: `CLAUDE.md` and `.claude/architecture/`
- **Configuration**: `railway.toml` and environment variables

### Support Channels
- **Railway Support**: For infrastructure issues
- **AI Provider Support**: For API-related issues
- **Application Logs**: Via Railway dashboard
- **Health Dashboard**: `/static/monitor.html`

### Useful Commands
```bash
# View application logs
railway logs --tail 100

# Connect to database
railway connect

# Deploy latest changes
railway up

# Check service status
railway status

# Environment variables
railway variables
```

---

**🎯 Operational Excellence Standards Met:**
- ✅ Comprehensive monitoring and alerting
- ✅ Clear troubleshooting procedures
- ✅ Production-ready performance targets
- ✅ Educational effectiveness tracking
- ✅ Security and compliance measures
- ✅ Cost optimization strategies
- ✅ Emergency response procedures
- ✅ Maintenance schedules and checklists