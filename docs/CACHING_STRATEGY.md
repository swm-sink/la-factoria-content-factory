# HTTP Response Caching Strategy

## Overview

La Factoria implements a comprehensive HTTP response caching strategy to improve performance and reduce server load. This document outlines our caching approach for different content types and scenarios.

## Cache Strategies by Content Type

### 1. Static Assets (CSS, JS, Images, Fonts)
- **Cache Duration**: 1 year (31536000 seconds)
- **Cache-Control**: `public, max-age=31536000, immutable`
- **Strategy**: Aggressive caching with immutable flag
- **Rationale**: Static assets with versioned filenames can be cached indefinitely

```
Cache-Control: public, max-age=31536000, immutable
```

### 2. API Responses

#### General API Endpoints
- **Cache Duration**: 5 minutes (300 seconds)
- **Cache-Control**: `private, max-age=300, must-revalidate`
- **Strategy**: Short-term private caching with revalidation
- **Rationale**: Balance between performance and data freshness

#### Rarely Changing Data (e.g., content types, templates)
- **Cache Duration**: 15 minutes (900 seconds)
- **Cache-Control**: `public, max-age=900, must-revalidate`
- **Strategy**: Longer caching for stable data
- **Rationale**: These resources change infrequently

### 3. Dynamic Content (HTML)
- **Cache Duration**: 1 minute (60 seconds)
- **Cache-Control**: `private, max-age=60, must-revalidate`
- **Strategy**: Very short caching with ETags
- **Rationale**: Allows for quick updates while reducing server load

### 4. User-Specific Content
- **Cache Duration**: No caching
- **Cache-Control**: `no-cache`
- **Strategy**: Always fetch fresh data
- **Rationale**: User data must always be current

### 5. Generated Content (Audio, PDFs)
- **Audio Files**: 24 hours cache
- **PDF Documents**: 1 hour cache
- **Strategy**: Moderate caching for generated content
- **Rationale**: Balance storage costs with regeneration overhead

## Conditional Requests

### ETag Support
- Generated for all dynamic content
- Weak ETags using content hash
- Enables 304 Not Modified responses

### Last-Modified Headers
- Added to all responses
- Used as fallback when ETags not available
- Supports If-Modified-Since requests

## Cache Invalidation

### Automatic Invalidation
- POST/PUT/DELETE operations invalidate related caches
- Pattern-based invalidation (e.g., `/api/v1/content*`)
- Timestamp-based tracking

### Manual Invalidation
- Admin endpoints for cache purging
- Pattern matching for targeted invalidation
- Cleanup of old invalidation records

## Vary Headers

### Content Negotiation
- `Vary: Accept` for content type negotiation
- `Vary: Accept-Encoding` for compression
- `Vary: Authorization` for user-specific responses

## Performance Optimizations

### Stale-While-Revalidate
- Added to non-immutable cached content
- Allows serving stale content while fetching fresh
- Improves perceived performance

### Process-Time Header
- `X-Process-Time` header shows processing duration
- Helps monitor cache effectiveness
- Useful for performance debugging

## Implementation Details

### Middleware Architecture
1. **CacheHeadersMiddleware**: Adds appropriate cache headers
2. **CacheInvalidationHandler**: Tracks invalidation patterns
3. **CacheUtils**: Utilities for ETag generation and parsing

### Configuration
- Centralized in `app/core/config/cache_config.py`
- Path-based and content-type based rules
- Easy to modify cache durations

## Browser Caching Benefits

### Reduced Latency
- Static assets served from browser cache
- API responses cached for repeated requests
- Conditional requests reduce bandwidth

### Server Load Reduction
- Fewer requests reach the server
- 304 responses are lightweight
- CDN integration amplifies benefits

## Monitoring and Metrics

### Cache Hit Rate
- Tracked in middleware
- Logged periodically
- Target: >80% for static content

### Performance Metrics
- Process time per request
- Cache vs non-cache response times
- Conditional request statistics

## Best Practices

1. **Version Static Assets**: Use fingerprinted filenames
2. **Set Appropriate Durations**: Balance freshness vs performance
3. **Use ETags**: Enable conditional requests
4. **Monitor Performance**: Track cache effectiveness
5. **Plan Invalidation**: Clear caches when content changes

## Testing

Run the validation script to verify cache headers:

```bash
python scripts/validate_cache_headers.py
```

This validates:
- Correct cache durations
- Proper cache strategies
- ETag generation
- Conditional request handling
- Performance improvements