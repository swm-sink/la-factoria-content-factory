# Migration Guide: Enterprise → Simple

## Overview

This guide helps migrate from the complex enterprise system to La Factoria Simple.

## Pre-Migration Checklist

- [ ] Backup all data from Firestore
- [ ] Export user list and API keys
- [ ] Document which features are actually used
- [ ] Notify users of migration date
- [ ] Test new system with sample data

## Data Migration Steps

### 1. Export Users from Firestore

```python
# scripts/export_users.py
import firebase_admin
from firebase_admin import firestore

# Initialize Firestore
db = firestore.client()

# Export users
users = []
for doc in db.collection('users').stream():
    users.append({
        'id': doc.id,
        'email': doc.get('email'),
        'created_at': doc.get('created_at')
    })

# Save to JSON
import json
with open('users_export.json', 'w') as f:
    json.dump(users, f, indent=2)
```

### 2. Export Recent Content

```python
# Only export last 30 days of content
from datetime import datetime, timedelta

cutoff = datetime.now() - timedelta(days=30)
content = []

for doc in db.collection('content').where('created_at', '>', cutoff).stream():
    content.append(doc.to_dict())
```

### 3. Import to Railway Postgres

```sql
-- Create simple schema
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    api_key_hash VARCHAR(255),
    created_at TIMESTAMP,
    old_id VARCHAR(255) -- Reference to Firestore ID
);

CREATE TABLE content (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    topic TEXT,
    content_type VARCHAR(50),
    content TEXT,
    created_at TIMESTAMP
);
```

### 4. Generate New API Keys

```python
import secrets
import hashlib

def generate_api_key():
    """Generate secure API key."""
    return f"lf_{secrets.token_urlsafe(32)}"

def hash_api_key(key):
    """Hash API key for storage."""
    return hashlib.sha256(key.encode()).hexdigest()
```

## Feature Migration Map

| Old Feature | New Implementation | Action Required |
|-------------|-------------------|-----------------|
| Content Generation | ✅ Simplified endpoint | None |
| 8 Content Types | ✅ All supported | None |
| API Authentication | ✅ Simple API keys | Regenerate keys |
| User Management | ✅ Basic CRUD | Migrate users |
| GDPR Deletion | ✅ Simple endpoint | None |
| PDF Export | ❌ Removed | Notify users |
| Complex Search | ❌ Removed | Use ctrl+F |
| Job Queues | ❌ Removed | Now synchronous |
| SLA Monitoring | ❌ Removed | Use Railway metrics |
| Audit Trails | ❌ Removed | Basic logging only |

## DNS Cutover Plan

### Phase 1: Parallel Run (1 week)
- Old system: api.lafactoria.ai
- New system: simple.lafactoria.ai
- Users can test new system

### Phase 2: Gradual Migration
```
Day 1: Migrate internal team
Day 3: Migrate 50% of users
Day 5: Migrate remaining users
Day 7: Switch DNS
```

### Phase 3: DNS Switch
```bash
# Update DNS records
api.lafactoria.ai → [New Railway URL]

# Keep old system running for 30 days
old.lafactoria.ai → [Old Cloud Run URL]
```

## User Communication Template

```
Subject: La Factoria Simplification - Action Required

Dear User,

We're simplifying La Factoria to make it faster and more reliable.

What's Changing:
- New, simpler interface
- Faster response times  
- Lower costs (savings passed to you)

What's Staying the Same:
- All 8 content types
- API compatibility
- Your data

Action Required:
1. Save your new API key: [KEY]
2. Update your integration by [DATE]
3. Test at: simple.lafactoria.ai

Removed Features:
- PDF export (use browser print instead)
- Advanced search (use browser search)

Questions? Reply to this email.

Best,
La Factoria Team
```

## Rollback Plan

If issues arise:

1. **Immediate**: Switch DNS back (5 minutes)
2. **Data**: Restore from backup
3. **Communication**: Email users
4. **Fix**: Address issues in new system
5. **Retry**: Attempt migration again

## Success Metrics

- [ ] All users migrated successfully
- [ ] <5 support tickets
- [ ] Response time <500ms
- [ ] Zero data loss
- [ ] Cost reduction achieved

## Post-Migration

1. Monitor Railway metrics for 1 week
2. Archive old GCP project
3. Cancel unnecessary services
4. Document lessons learned
5. Celebrate simplification! 🎉