# Implementation Roadmap with TDD & Quality Gates

## 🏗️ Implementation Strategy

**ALIGNED WITH SIMPLIFICATION PLAN**: Simple implementation (Railway, minimal code) + Comprehensive AI context (.claude/ system)

### Dual-Track Approach

- **Track 1**: Minimal codebase implementation (<1500 lines, Railway deployment)
- **Track 2**: Comprehensive context engineering (full .claude/ directory for Claude Code effectiveness)

### Atomic Task Breakdown

#### Sprint 1: Foundation (Days 1-5)

```yaml
TASK-001:
  title: "Initialize simple project structure"
  tdd_first: 
    - Write test for basic FastAPI health endpoint
    - Write test for project structure validation
  implement:
    - Create minimal project structure
    - Setup Railway project
    - Initialize git repository
  quality_gate:
    - All tests pass
    - Railway deployment successful
    - Health endpoint responds
  atomic_commit: "feat: initialize minimal la-factoria-simple structure with health check"

TASK-002:
  title: "Implement basic content generation"
  tdd_first:
    - Test content generation endpoint exists
    - Test successful generation returns content
    - Test missing API key returns 401
  implement:
    - Create simple content generation endpoint
    - Add basic API key validation
    - Integrate with AI provider (OpenAI/Anthropic)
  quality_gate:
    - Tests pass with >80% coverage
    - Code < 100 lines
    - No complex abstractions
  atomic_commit: "feat: add basic content generation with API key auth"

TASK-003:
  title: "Integrate Langfuse for prompts"
  tdd_first:
    - Test Langfuse connection
    - Test prompt retrieval
    - Test prompt compilation with variables
  implement:
    - Setup Langfuse client
    - Create basic prompts in Langfuse UI
    - Replace hardcoded prompts
  quality_gate:
    - All prompts managed in Langfuse
    - Zero prompt code in repository
    - Tests verify Langfuse integration
  atomic_commit: "feat: integrate Langfuse for external prompt management"
```

#### Sprint 2: Data & Frontend (Days 6-10)

```yaml
TASK-004:
  title: "Add Railway Postgres"
  tdd_first:
    - Test database connection
    - Test content storage
    - Test content retrieval
  implement:
    - Setup Railway Postgres
    - Create simple schema (users, content)
    - Add basic CRUD operations
  quality_gate:
    - Database operations < 50 lines
    - No ORM complexity (raw SQL fine)
    - All tests pass
  atomic_commit: "feat: add Railway Postgres for content persistence"

TASK-005:
  title: "Create minimal frontend"
  tdd_first:
    - Test HTML loads
    - Test form submission
    - Test content display
  implement:
    - Single HTML file
    - Vanilla JavaScript (no framework)
    - Simple CSS (no preprocessor)
  quality_gate:
    - Frontend < 500 lines total
    - No build process needed
    - Works on mobile
  atomic_commit: "feat: add minimal vanilla JS frontend"
```

#### Sprint 3: Essential Features (Days 11-15)

```yaml
TASK-006:
  title: "Add simple user deletion (GDPR)"
  tdd_first:
    - Test user deletion endpoint
    - Test cascade deletion of content
    - Test deletion logging
  implement:
    - DELETE /api/user/{id} endpoint
    - Simple cascade delete
    - Basic logging
  quality_gate:
    - Implementation < 30 lines
    - No complex audit trail
    - Tests verify complete deletion
  atomic_commit: "feat: add simple GDPR-compliant user deletion"

TASK-007:
  title: "Add basic monitoring"
  tdd_first:
    - Test stats endpoint
    - Test metric calculations
    - Test uptime tracking
  implement:
    - /api/stats endpoint
    - Count queries for metrics
    - Simple uptime calculation
  quality_gate:
    - No external monitoring tools
    - Implementation < 50 lines
    - Response time < 100ms
  atomic_commit: "feat: add basic stats endpoint for monitoring"
```

## 🧪 TDD Templates

### Backend Test Template

```python
# tests/test_feature.py
import pytest
from fastapi.testclient import TestClient

class TestFeature:
    """TDD: Write these tests BEFORE implementation"""
    
    def test_feature_exists(self, client):
        """Test the endpoint exists"""
        response = client.get("/api/feature")
        assert response.status_code != 404
    
    def test_feature_auth_required(self, client):
        """Test authentication is enforced"""
        response = client.get("/api/feature")
        assert response.status_code == 401
    
    def test_feature_success(self, client, auth_headers):
        """Test successful operation"""
        response = client.get("/api/feature", headers=auth_headers)
        assert response.status_code == 200
        assert "expected_field" in response.json()
```

### Frontend Test Template

```javascript
// tests/frontend.test.js
describe('Frontend Tests', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <form id="content-form">
                <input id="topic" />
                <button type="submit">Generate</button>
            </form>
            <div id="output"></div>
        `;
    });

    test('form submission triggers API call', async () => {
        const mockFetch = jest.fn(() => 
            Promise.resolve({ json: () => ({ content: 'Generated content' }) })
        );
        global.fetch = mockFetch;

        document.getElementById('topic').value = 'Test topic';
        document.querySelector('form').submit();

        expect(mockFetch).toHaveBeenCalledWith('/api/generate', expect.any(Object));
    });
});
```

## 🚦 Quality Gates

### Code Quality Gates

```yaml
simplicity_gates:
  file_size:
    max_lines: 200
    action: "Split if larger"
  
  function_complexity:
    max_cyclomatic: 5
    action: "Refactor if complex"
  
  dependency_count:
    backend_max: 15
    frontend_max: 0  # Vanilla JS only
    action: "Justify each addition"
  
  abstraction_layers:
    max_depth: 2
    action: "Flatten if deeper"
```

### Deployment Gates

```yaml
deployment_gates:
  test_coverage:
    minimum: 80%
    core_features: 95%
  
  build_time:
    maximum: 60s
    target: 30s
  
  deploy_time:
    maximum: 120s
    target: 60s
  
  health_check:
    must_pass: true
    timeout: 5s
```

## 📝 Atomic Commit Strategy

### Commit Message Format

```
<type>: <description>

- What: Specific changes made
- Why: Business value delivered  
- How: Technical approach (if non-obvious)

Tests: X added, Y passing
Complexity: -X lines removed
```

### Commit Types for Simplification

- `simplify`: Reducing complexity
- `remove`: Deleting unnecessary code
- `consolidate`: Combining multiple files/functions
- `replace`: Swapping complex solution for simple one

### Example Commits

```bash
simplify: replace 15 middleware with 3 essential ones

- What: Removed 12 middleware, kept CORS, Auth, Error
- Why: 10 users don't need enterprise monitoring
- How: Direct FastAPI middleware, no custom classes

Tests: 3 added, 3 passing
Complexity: -500 lines removed

---

replace: use Railway Postgres instead of Firestore + Redis

- What: Single database for all data needs
- Why: Managed service, zero configuration
- How: Simple SQL queries, no ORM

Tests: 5 added, 5 passing  
Complexity: -800 lines, -3 services

---

remove: eliminate complex export system

- What: Removed PDF, DOCX, CSV exporters
- Why: JSON API sufficient for 10 users
- How: Frontend can handle formatting if needed

Tests: 2 retained, 15 removed
Complexity: -1200 lines, -5 dependencies
```

## 🎯 Success Criteria

### Week 1 Checkpoint

- [ ] Basic API running on Railway
- [ ] Content generation working with Langfuse
- [ ] Simple frontend deployed
- [ ] <500 total lines of code

### Week 2 Checkpoint  

- [ ] Database persistence working
- [ ] Basic auth implemented
- [ ] User deletion (GDPR) added
- [ ] <1000 total lines of code

### Week 3 Checkpoint

- [ ] All essential features migrated
- [ ] Old system archived
- [ ] Documentation updated
- [ ] <1500 total lines of code

### Final Success Metrics

- **Developer Experience**: New dev productive in <1 hour
- **Deployment**: Git push = deployed in <2 minutes  
- **Maintenance**: <2 hours/month effort
- **Cost**: <$25/month on Railway
- **Performance**: <200ms response time
- **Reliability**: 99%+ uptime with zero complexity
