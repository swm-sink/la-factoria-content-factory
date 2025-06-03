# Sentry Error Management Process

**Document Version**: 1.0
**Last Updated**: June 3, 2025
**Owner**: AI Content Factory Team

## Overview

This document outlines the formal process for managing errors, exceptions, and performance issues reported through Sentry in the AI Content Factory application.

## Sentry Configuration

### Environment Setup
- **Production Environment**: `ai-content-factory-prod`
- **Staging Environment**: `ai-content-factory-staging`
- **Development Environment**: `ai-content-factory-dev`

### Project Configuration
- **Organization**: AI Content Factory
- **Teams**: Backend, DevOps, Product
- **Integration**: Slack notifications for critical errors
- **Retention**: 90 days for all environments

## Error Classification & Severity Levels

### 1. Critical (P0) - Immediate Response Required
**Response Time**: Within 15 minutes during business hours, 30 minutes 24/7

**Criteria**:
- Service completely unavailable (5xx errors > 50% for 5+ minutes)
- Data loss or corruption
- Security breaches or authentication failures
- Gemini/ElevenLabs API integration completely failing
- Payment processing failures

**Examples**:
```python
# Critical errors that trigger immediate alerts
- ConnectionError: "Unable to connect to Vertex AI"
- ValidationError: "Content generation pipeline failure"
- SecurityError: "Unauthorized access attempt detected"
```

**Actions**:
1. Immediate investigation by on-call engineer
2. Notify team lead and product manager
3. Create incident in incident management system
4. Post updates in #alerts Slack channel every 15 minutes

### 2. High (P1) - Same Day Resolution
**Response Time**: Within 2 hours during business hours

**Criteria**:
- Individual feature completely broken
- Performance degradation affecting user experience
- Non-critical API failures with fallback mechanisms
- Cache failures affecting performance

**Examples**:
```python
# High priority errors requiring same-day attention
- TimeoutError: "Content generation taking >60 seconds"
- CacheError: "Redis connection intermittent"
- ValidationError: "FAQ generation failing, other content types working"
```

**Actions**:
1. Assign to appropriate team member within 2 hours
2. Create GitHub issue with Sentry link
3. Investigate root cause and implement fix
4. Update in daily standup

### 3. Medium (P2) - This Week Resolution
**Response Time**: Within 24 hours during business hours

**Criteria**:
- Intermittent errors affecting <10% of requests
- Non-user-facing errors (logging, monitoring)
- Performance issues that don't significantly impact UX
- Edge case validation errors

**Examples**:
```python
# Medium priority errors for weekly resolution
- ValidationError: "Unusual syllabus format causing parsing issues"
- PerformanceWarning: "Cache hit ratio below 80%"
- LoggingError: "Unable to write to audit log"
```

**Actions**:
1. Add to weekly planning backlog
2. Assign during sprint planning
3. Document in team knowledge base if recurring

### 4. Low (P3) - Next Sprint Resolution
**Response Time**: Reviewed in weekly triage

**Criteria**:
- Cosmetic issues with no functional impact
- Debug logging errors
- Non-critical third-party service warnings
- Documentation or help text issues

## Daily Error Review Process

### Morning Triage (9:00 AM Daily)
**Participants**: Team Lead, Senior Engineer, DevOps Engineer

**Agenda** (15 minutes):
1. **Review Critical/High Priority Issues**
   - Any P0/P1 issues from last 24 hours
   - Status updates on open incidents

2. **Performance Metrics Review**
   - Error rate trends
   - Performance regression alerts
   - Resource utilization spikes

3. **Assign Daily Tasks**
   - Assign unresolved P1 issues
   - Review P2 issues for escalation
   - Update incident status

### Weekly Deep Dive (Fridays 2:00 PM)
**Participants**: Full Engineering Team

**Agenda** (30 minutes):
1. **Trend Analysis**
   - Weekly error patterns
   - Recurring issue identification
   - Performance trend review

2. **Root Cause Analysis**
   - Deep dive on resolved critical issues
   - Documentation of lessons learned
   - Process improvement opportunities

3. **Prevention Planning**
   - Additional monitoring needs
   - Code quality improvements
   - Testing gap identification

## Sentry Alert Configuration

### Slack Integration
**Channel**: `#ai-content-factory-alerts`

**Alert Rules**:
```yaml
Critical Alerts (Immediate):
  - Error rate > 5% over 5 minutes
  - Any error tagged as "critical"
  - New release errors > 10 per minute
  - Security-related errors (any volume)

High Priority Alerts (Within 1 hour):
  - Error rate > 2% over 15 minutes
  - Performance degradation > 50% from baseline
  - Content generation failures > 5 per hour
  - Cache errors > 10 per hour

Daily Digest (9:00 AM):
  - Previous day error summary
  - New error types discovered
  - Performance metrics summary
```

### Email Notifications
**Recipients**:
- Team Lead (all P0/P1 alerts)
- On-call Engineer (P0 alerts only)
- Product Manager (P0 alerts and daily digest)

## Investigation Workflow

### 1. Initial Assessment (First 5 minutes)
```markdown
**Checklist**:
- [ ] Determine severity level
- [ ] Check if this is a known issue
- [ ] Verify error is still occurring
- [ ] Check related services (Vertex AI, Firestore, etc.)
- [ ] Review recent deployments/changes
```

### 2. Detailed Investigation
```markdown
**Standard Investigation Steps**:
- [ ] Review Sentry error details and stack trace
- [ ] Check application logs for correlation_id context
- [ ] Review Google Cloud Console for infrastructure issues
- [ ] Analyze user impact scope
- [ ] Check performance dashboards for correlations
- [ ] Review recent code changes in affected areas
```

### 3. Resolution Documentation
```markdown
**Required Documentation**:
- Root cause analysis
- Fix implementation details
- Prevention measures implemented
- Testing performed to verify fix
- Monitoring added to prevent recurrence
```

## Sentry Best Practices

### Error Context Enhancement
```python
# Always include relevant context in Sentry events
import sentry_sdk

def process_content_generation(job_id: str, user_id: str):
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("job_id", job_id)
        scope.set_tag("user_id", user_id)  # Ensure no PII
        scope.set_tag("feature", "content_generation")
        scope.set_context("job_details", {
            "job_type": "comprehensive",
            "target_format": "study_guide"
        })
```

### Custom Error Types
```python
# Use meaningful error types for better categorization
class ContentGenerationError(Exception):
    """Raised when content generation fails"""
    pass

class LLMValidationError(ContentGenerationError):
    """Raised when LLM output fails validation"""
    pass

class CacheTimeoutError(Exception):
    """Raised when cache operations timeout"""
    pass
```

### Performance Monitoring
```python
# Add performance transactions for key operations
@sentry_sdk.trace
def generate_comprehensive_content(syllabus_text: str):
    with sentry_sdk.start_transaction(name="content_generation", op="ai_operation"):
        # Content generation logic
        pass
```

## Metrics and KPIs

### Weekly Review Metrics
- **Error Rate**: Target <1% of total requests
- **MTTR (Mean Time to Resolution)**:
  - P0: <30 minutes
  - P1: <4 hours
  - P2: <24 hours
- **Error Recurrence Rate**: <5% of resolved issues
- **Coverage**: >95% of errors properly categorized and assigned

### Monthly Review Metrics
- **Error Trend Analysis**: Month-over-month error rate reduction
- **Top Error Categories**: Identify most common error sources
- **Team Response Time**: Average response time by severity
- **Prevention Effectiveness**: Reduction in recurring errors

## Escalation Procedures

### Internal Escalation
1. **15 minutes**: If P0 issue not resolved, escalate to Team Lead
2. **30 minutes**: If P0 issue not resolved, escalate to Engineering Manager
3. **1 hour**: If P0 issue not resolved, escalate to CTO and involve vendor support

### External Communication
**Customer Communication**:
- P0 issues affecting >10% of users: Status page update within 30 minutes
- P1 issues affecting core features: Proactive customer communication
- All issues: Post-incident review shared with affected customers

## Tools and Access

### Required Access
- **Sentry**: All team members have access to relevant projects
- **Google Cloud Console**: For infrastructure correlation
- **GitHub**: For code investigation and issue creation
- **Slack**: For team communication and alerts

### Integration Points
- **GitHub Issues**: Auto-create for P1+ errors
- **Google Cloud Monitoring**: Cross-reference infrastructure metrics
- **Grafana Dashboards**: Performance correlation analysis
- **PagerDuty**: Critical alert escalation (if configured)

## Continuous Improvement

### Monthly Process Review
- Review escalation effectiveness
- Assess alert noise vs. signal ratio
- Update severity classification based on experience
- Improve documentation based on common questions

### Quarterly Process Updates
- Review and update this documentation
- Assess tool effectiveness and potential alternatives
- Update team training and onboarding materials
- Benchmark against industry best practices

---

## Appendix

### Common Error Patterns and Solutions

**Content Generation Timeouts**:
```
Root Cause: Vertex AI API latency spikes
Solution: Implement retry logic with exponential backoff
Prevention: Monitor API latency and set appropriate timeouts
```

**Cache Connection Failures**:
```
Root Cause: Redis instance memory pressure
Solution: Implement cache size limits and LRU eviction
Prevention: Monitor cache memory usage and hit ratios
```

**Validation Errors**:
```
Root Cause: LLM output format variations
Solution: Enhanced JSON cleaning and retry logic
Prevention: Improve prompt engineering and output validation
```

### Emergency Contacts
- **Team Lead**: [Contact Information]
- **DevOps Engineer**: [Contact Information]
- **On-Call Rotation**: [PagerDuty/Escalation Details]

---

*This document is reviewed and updated quarterly or after significant incidents to ensure continued effectiveness of our error management process.*
