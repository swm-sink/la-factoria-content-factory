# Atomic Task List for La Factoria Simplification

## Task Naming Convention
- Format: `[PHASE]-[NUMBER]: [ACTION] [TARGET]`
- Example: `SETUP-001: Create new repository structure`

## Week 0: Discovery Tasks

### DISCOVER-001: Create user survey
**Duration**: 2 hours
**Dependencies**: None
**TDD**: N/A
**Output**: Google Form or survey link
**Quality Gate**: Survey covers all current features

### DISCOVER-002: Analyze usage data
**Duration**: 4 hours  
**Dependencies**: Access to current system logs
**TDD**: Create analysis script with tests
**Output**: Usage report with metrics
**Quality Gate**: Data from last 30 days analyzed

### DISCOVER-003: Document compliance requirements
**Duration**: 2 hours
**Dependencies**: DISCOVER-002
**TDD**: N/A
**Output**: Compliance checklist
**Quality Gate**: Legal/regulatory requirements identified

## Week 1: Foundation Tasks

### SETUP-001: Create repository structure
**Duration**: 1 hour
**Dependencies**: None
**TDD**: Test directory structure exists
**Output**: Empty project skeleton
**Quality Gate**: All directories created
```bash
mkdir -p la-factoria-simple/{src,static,tests,scripts,docs}
```

### SETUP-002: Initialize Railway project
**Duration**: 1 hour
**Dependencies**: Railway account
**TDD**: Test deployment works
**Output**: Railway project URL
**Quality Gate**: Deployment successful

### SETUP-003: Create test framework
**Duration**: 2 hours
**Dependencies**: SETUP-001
**TDD**: Meta-test the test runner
**Output**: Pytest configuration
**Quality Gate**: Sample test passes
```python
# tests/test_setup.py
def test_project_structure_exists():
    assert os.path.exists('src')
    assert os.path.exists('static')
```

### API-001: Implement health check endpoint
**Duration**: 2 hours
**Dependencies**: SETUP-003
**TDD**: Write test first
**Output**: /health endpoint
**Quality Gate**: Returns 200 OK
```python
# tests/test_health.py
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### API-002: Create content generation endpoint structure
**Duration**: 3 hours
**Dependencies**: API-001
**TDD**: Test endpoint exists and validates input
**Output**: POST /api/generate skeleton
**Quality Gate**: 400 on invalid input, 401 on no auth
```python
# tests/test_generate.py
def test_generate_requires_auth():
    response = client.post("/api/generate", json={})
    assert response.status_code == 401

def test_generate_validates_input():
    response = client.post("/api/generate", 
                         json={},
                         headers={"X-API-Key": "test"})
    assert response.status_code == 400
```

### API-003: Implement simple authentication
**Duration**: 3 hours
**Dependencies**: API-002
**TDD**: Test auth validation
**Output**: API key validation
**Quality Gate**: Valid/invalid keys handled correctly
```python
# tests/test_auth.py
def test_valid_api_key():
    response = client.get("/health", 
                         headers={"X-API-Key": "valid-key"})
    assert response.status_code == 200

def test_invalid_api_key():
    response = client.get("/api/generate",
                         headers={"X-API-Key": "invalid"})
    assert response.status_code == 401
```

### API-004: Add AI provider integration
**Duration**: 4 hours
**Dependencies**: API-002
**TDD**: Mock AI responses
**Output**: Working content generation
**Quality Gate**: Generates content successfully
```python
# tests/test_ai_integration.py
@patch('src.main.openai_client')
def test_ai_generation(mock_client):
    mock_client.return_value = "Generated content"
    response = client.post("/api/generate",
                         json={"topic": "Python"},
                         headers={"X-API-Key": "valid"})
    assert "Generated content" in response.json()["content"]
```

### FRONT-001: Create basic HTML structure
**Duration**: 2 hours
**Dependencies**: None
**TDD**: Test HTML validation
**Output**: index.html
**Quality Gate**: Valid HTML5, responsive

### FRONT-002: Add form and interaction
**Duration**: 3 hours
**Dependencies**: FRONT-001
**TDD**: Test form submission
**Output**: Working form
**Quality Gate**: Form submits to API

### DEPLOY-001: Deploy prototype to Railway
**Duration**: 2 hours
**Dependencies**: API-004, FRONT-002
**TDD**: Test deployed endpoint
**Output**: Live URL
**Quality Gate**: Accessible from internet

## Week 2: Enhancement Tasks

### DB-001: Set up Railway Postgres
**Duration**: 2 hours
**Dependencies**: Railway project
**TDD**: Test connection
**Output**: Database URL
**Quality Gate**: Can connect and query

### DB-002: Create database schema
**Duration**: 2 hours
**Dependencies**: DB-001
**TDD**: Test schema creation
**Output**: Tables created
**Quality Gate**: Schema matches design
```sql
-- Simple schema
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    api_key_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE content_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    topic TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### DB-003: Implement user CRUD
**Duration**: 3 hours
**Dependencies**: DB-002
**TDD**: Test each operation
**Output**: User management functions
**Quality Gate**: All CRUD operations work

### AUTH-001: Add API key generation
**Duration**: 3 hours
**Dependencies**: DB-003
**TDD**: Test key generation and validation
**Output**: Key management endpoints
**Quality Gate**: Secure key generation

### GDPR-001: Implement user deletion
**Duration**: 3 hours
**Dependencies**: DB-003
**TDD**: Test cascade deletion
**Output**: DELETE /api/user/{id}
**Quality Gate**: All user data removed
```python
# tests/test_gdpr.py
def test_user_deletion_cascade():
    # Create user with content
    user_id = create_test_user()
    create_test_content(user_id)
    
    # Delete user
    response = client.delete(f"/api/user/{user_id}",
                           headers={"X-API-Key": "admin"})
    assert response.status_code == 200
    
    # Verify deletion
    assert get_user(user_id) is None
    assert get_user_content(user_id) == []
```

### FEAT-001: Add PDF export (if needed)
**Duration**: 4 hours
**Dependencies**: User survey results
**TDD**: Test PDF generation
**Output**: PDF export endpoint
**Quality Gate**: Valid PDF generated

## Week 3: Robustness Tasks

### TEST-001: Write comprehensive test suite
**Duration**: 6 hours
**Dependencies**: All API endpoints
**TDD**: N/A (this IS the tests)
**Output**: >80% coverage
**Quality Gate**: All tests pass

### PERF-001: Load test the system
**Duration**: 4 hours
**Dependencies**: Deployed system
**TDD**: Test performance thresholds
**Output**: Performance report
**Quality Gate**: <1s response time

### SEC-001: Security audit
**Duration**: 4 hours
**Dependencies**: All endpoints
**TDD**: Security test cases
**Output**: Security report
**Quality Gate**: No critical vulnerabilities

### MIG-001: Create data export script
**Duration**: 4 hours
**Dependencies**: Access to old system
**TDD**: Test export validation
**Output**: export_data.py
**Quality Gate**: Exports with checksums

### MIG-002: Create data import script
**Duration**: 4 hours
**Dependencies**: MIG-001, DB-002
**TDD**: Test import with rollback
**Output**: import_data.py
**Quality Gate**: Import reversible

### DOC-001: Write user documentation
**Duration**: 4 hours
**Dependencies**: All features complete
**TDD**: Documentation tests
**Output**: User guide
**Quality Gate**: Covers all features

## Week 4: Migration Tasks

### MIG-003: Pilot user migration
**Duration**: 4 hours
**Dependencies**: MIG-002
**TDD**: Test migration success
**Output**: 1 user migrated
**Quality Gate**: User can access system

### MIG-004: Batch migration (50%)
**Duration**: 6 hours
**Dependencies**: MIG-003 success
**TDD**: Test batch process
**Output**: 5 users migrated
**Quality Gate**: All users functional

### MIG-005: Complete migration
**Duration**: 6 hours
**Dependencies**: MIG-004 success
**TDD**: Test full migration
**Output**: All users migrated
**Quality Gate**: 100% migrated

### MON-001: Set up monitoring
**Duration**: 3 hours
**Dependencies**: Production system
**TDD**: Test alert firing
**Output**: Basic monitoring
**Quality Gate**: Alerts work

## Week 5: Finalization Tasks

### ARCH-001: Archive old system
**Duration**: 4 hours
**Dependencies**: Migration complete
**TDD**: Test archive integrity
**Output**: Archived repository
**Quality Gate**: Archive accessible

### CLEAN-001: Remove old resources
**Duration**: 3 hours
**Dependencies**: ARCH-001
**TDD**: Test resource removal
**Output**: GCP cleaned up
**Quality Gate**: No active resources

### KNOW-001: Knowledge transfer session
**Duration**: 4 hours
**Dependencies**: All documentation
**TDD**: N/A
**Output**: Training complete
**Quality Gate**: Maintainer confident

### RETRO-001: Project retrospective
**Duration**: 2 hours
**Dependencies**: Project complete
**TDD**: N/A
**Output**: Lessons learned
**Quality Gate**: Document created

## Total Task Count: 48 tasks
## Total Estimated Hours: ~140 hours
## Buffer (20%): 28 hours
## Total Project Hours: 168 hours (~4 weeks full-time)