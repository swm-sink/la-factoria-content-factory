# API Rate Limiting Issues

**Severity**: P3 (Medium)  
**Time Estimate**: 10-20 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Platform Team  
**Related SLO**: API Availability 99.9%

## Summary

Troubleshooting and resolving rate limiting issues affecting API users. This runbook helps identify and resolve issues where legitimate users are hitting rate limits or when API abuse is detected. Expected outcome is to restore normal API access while maintaining protection against abuse.

## Symptoms

- [ ] Users receiving 429 (Too Many Requests) errors
- [ ] Legitimate users blocked
- [ ] API abuse detected
- [ ] Rate limit configuration issues

## Alert References

- **Alert Name**: `api-rate-limit-exceeded`
- **Dashboard**: Rate Limiting Dashboard
- **Runbook Trigger**: High rate of 429 responses

## Prerequisites

- Railway CLI access with production permissions
- Python scripts directory access
- Understanding of rate limiting tiers
- Access to monitoring dashboards
- API key management permissions

## Initial Assessment (2-5 minutes)

1. **Check rate limit metrics**:

   ```bash
   # Check current rate limit status - counts 429 errors in last 100 log lines
   railway logs --tail 100 | grep -c "429"

   # Identify top consumers by extracting and counting rate limit hits
   # Field $5 should contain user identifier (API key or IP)
   railway logs --tail 1000 | grep "rate_limit" | \
     awk '{print $5}' | sort | uniq -c | sort -rn | head -10
   ```

2. **Identify patterns**:

   ```bash
   # Analyze rate limit patterns by IP address to identify potential abuse
   railway run python scripts/analyze_rate_limits.py --by-ip

   # Group rate limit hits by API key to find heavy users
   railway run python scripts/analyze_rate_limits.py --by-key

   # Check which endpoints are hit most to optimize limits
   railway run python scripts/analyze_rate_limits.py --by-endpoint
   ```

## Resolution Steps

### Step 1: Adjust Rate Limits (5-10 minutes)

**Goal**: Balance protection with usability

```bash
# Display current rate limit configuration from environment variables
railway env | grep RATE_LIMIT

# For legitimate high-volume users
railway env set RATE_LIMIT_TIER_PREMIUM=1000  # per hour
railway env set RATE_LIMIT_TIER_STANDARD=100   # per hour
railway env set RATE_LIMIT_TIER_FREE=20        # per hour

# Adjust burst limits
railway env set RATE_LIMIT_BURST_MULTIPLIER=2
railway env set RATE_LIMIT_WINDOW_SECONDS=3600

railway restart
```

### Step 2: Whitelist Legitimate Users (5-10 minutes)

**Goal**: Exempt verified high-volume users

```bash
# Add specific API key to whitelist to bypass rate limits
railway run python scripts/manage_whitelist.py --add --api-key="key123"

# Or by IP range (internal services)
railway run python scripts/manage_whitelist.py --add --ip-range="10.0.0.0/8"

# Verify whitelist
railway run python scripts/manage_whitelist.py --list
```

### Step 3: Block Abusive Users (5-10 minutes)

**Goal**: Stop API abuse

```bash
# Identify potential API abusers exceeding 5000 requests threshold
railway run python scripts/identify_api_abuse.py --threshold=5000

# Block specific API keys
railway run python scripts/block_api_key.py --key="abusive_key" --reason="abuse"

# Block IP addresses
railway run python scripts/block_ip.py --ip="1.2.3.4" --duration=24h

# Enable stricter limits for anonymous users
railway env set RATE_LIMIT_ANONYMOUS=5  # very low
railway restart
```

## Rate Limiting Strategies

### 1. Tiered Limits

```python
# Configuration example
RATE_LIMITS = {
    'free': {'hourly': 20, 'daily': 100},
    'basic': {'hourly': 100, 'daily': 1000},
    'premium': {'hourly': 1000, 'daily': 10000},
    'enterprise': {'hourly': 10000, 'daily': 100000}
}
```

### 2. Endpoint-Specific Limits

```bash
# Heavy endpoints get lower limits
railway env set RATE_LIMIT_CONTENT_GENERATE=10   # per hour
railway env set RATE_LIMIT_AUDIO_GENERATE=5      # per hour
railway env set RATE_LIMIT_HEALTH_CHECK=1000     # per hour
```

### 3. Adaptive Rate Limiting

```bash
# Enable adaptive limits based on system load
railway env set ADAPTIVE_RATE_LIMITING=true
railway env set RATE_LIMIT_CPU_THRESHOLD=80
railway env set RATE_LIMIT_REDUCTION_FACTOR=0.5
```

## Monitoring Rate Limits

### Real-time Monitoring

```bash
# Monitor rate limit hits in real-time, updates every 5 seconds
watch -n 5 'railway logs --tail 50 | grep -c "rate_limit"'

# Monitor by endpoint
railway run python scripts/monitor_rate_limits.py --real-time
```

### Rate Limit Headers

```bash
# Check rate limit headers - HEAD request to see limits without consuming quota
curl --fail -I https://api.lafactoria.com/api/content/list \
  -H "Authorization: Bearer $API_KEY"

# Expected headers:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 95
# X-RateLimit-Reset: 1234567890
```

## User Communication

### For Legitimate Users Hit Limits

```
Hello [User],

We noticed you're hitting our API rate limits. Your current plan allows [X] requests per hour.

Options:
1. Upgrade to [Plan] for higher limits
2. Implement request batching
3. Add caching to reduce requests

Need help? Contact support@lafactoria.com
```

### For Blocked Users

```
Your API access has been temporarily restricted due to [reason].

To restore access:
1. Review our API usage guidelines
2. Implement proper rate limiting
3. Contact support with your use case

Block expires: [timestamp]
```

## Best Practices Implementation

### 1. Client-Side Rate Limiting

```python
# Example retry logic
import time
from functools import wraps

def rate_limit_retry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if i < max_retries - 1:
                    time.sleep(e.retry_after)
                else:
                    raise
    return wrapper
```

### 2. Caching Recommendations

```bash
# Enable caching headers
railway env set CACHE_CONTROL_ENABLED=true
railway env set CACHE_CONTROL_MAX_AGE=300

# Encourage client caching
railway env set ETAG_ENABLED=true
```

## Troubleshooting Common Issues

### Issue: Rate limits not applying

```bash
# Verify Redis connection for rate limit storage (if using Redis backend)
railway run python scripts/check_redis.py

# Verify configuration loaded
railway run python -c "from app.config import settings; print(settings.rate_limits)"
```

### Issue: Inconsistent limits

```bash
# Check for time synchronization issues that can affect rate limit windows
railway run python scripts/check_time_sync.py

# Reset rate limit counters
railway run python scripts/reset_rate_limits.py --all
```

## Post-Incident Actions

- [ ] Review rate limit configuration
- [ ] Update documentation for users
- [ ] Implement better monitoring
- [ ] Consider graduated response
- [ ] Educate users on best practices

## Verification

1. **Confirm rate limits are working correctly**:

   ```bash
   # Test rate limit is enforced
   for i in {1..25}; do
     curl --fail -s -o /dev/null -w "%{http_code}\n" \
       https://api.lafactoria.com/api/health \
       -H "Authorization: Bearer $TEST_API_KEY";
   done | grep -c "429"
   # Should see 429s after limit exceeded
   ```

2. **Verify legitimate users have access**:

   ```bash
   # Check whitelisted user can access
   curl --fail https://api.lafactoria.com/api/content/list \
     -H "Authorization: Bearer $WHITELISTED_KEY"
   # Expected: 200 OK response
   ```

3. **Monitor error rates**:

   ```bash
   # Error rate should decrease after fixes
   railway logs --tail 100 | grep -c "429"
   # Expected: Lower count than initial assessment
   ```

## Related Documentation

- API Usage Guidelines (see docs/api/)
- Rate Limiting Architecture (see docs/architecture/)
- API Authentication Guide (see docs/api/)
- Monitoring Setup Guide (see docs/monitoring/)
