# Atomic Commits Plan - La Factoria Stabilization

## Commit Strategy

Following conventional commits specification with atomic, focused changes.

## Prepared Commits (Ready to Execute)

### Commit 1: chore(deps): Update dependency versions for compatibility
```bash
git add requirements-updated.txt
git add tests/test_dependency_compatibility.py
git commit -m "chore(deps): Update dependency versions for compatibility

- Align FastAPI to 0.116.1 (from 0.104.1)
- Update Pydantic to 2.11.7 (from 2.5.0)
- Update uvicorn to 0.35.0 (from 0.24.0)
- Add comprehensive dependency compatibility tests
- Ensure all dependencies work together

BREAKING CHANGE: FastAPI 0.110+ requires yield dependencies to raise exceptions
Test: tests/test_dependency_compatibility.py validates all versions"
```

### Commit 2: chore(cleanup): Organize directory structure and remove duplicates
```bash
git add cleanup_directory.py
git add .gitignore
git add -A reports/cleanup_moved/
git add -A logs_archive/
git add -A scripts/
git rm -r archive/claude_duplicate_20250809/
git rm -r backup_claude_20250809_115235/
git commit -m "chore(cleanup): Organize directory structure and remove duplicates

- Remove 10.15 MB of duplicate backup directories
- Organize 14 reports into reports/cleanup_moved/
- Archive 19 log files to logs_archive/
- Move 5 utility scripts to scripts/
- Create comprehensive .gitignore

Follows DRY/SSOT principles
Space freed: 10.15 MB"
```

### Commit 3: test(fix): Fix test imports and pytest configuration
```bash
git add pytest.ini
git add tests/test_settings.py
git commit -m "test(fix): Fix test imports and pytest configuration

- Add proper pytest markers definition
- Fix Python path setup for test imports
- Use pathlib for robust path handling
- Add validate_settings implementation

Coverage: 63% baseline established"
```

### Commit 4: docs(report): Add comprehensive stabilization documentation
```bash
git add PROJECT_STABILIZATION_REPORT.md
git add PHASE_0_5_FOUNDATION_RESEARCH_REPORT.md
git add ATOMIC_COMMITS_PLAN.md
git commit -m "docs(report): Add comprehensive stabilization documentation

- Document all critical issues found
- Create stabilization roadmap
- Add metrics and risk assessment
- Define clear definition of done
- Provide atomic commits strategy

References: Phase 0.5 research findings"
```

## Future Commits (After Implementation)

### Commit 5: fix(security): Implement rate limiting and API security
```bash
# After implementing security fixes
git add src/core/security.py
git add src/api/middleware/
git commit -m "fix(security): Implement rate limiting and API security

- Add SlowAPI rate limiting (100 req/min)
- Configure security headers (CORS, CSP)
- Implement API key rotation mechanism
- Add input validation and sanitization

Security: Addresses OWASP API Top 10
CVE: No known vulnerabilities"
```

### Commit 6: perf(db): Add database connection pooling
```bash
# After implementing pooling
git add src/core/database.py
git commit -m "perf(db): Add database connection pooling

- Configure SQLAlchemy connection pool (size=20)
- Add pool_pre_ping for connection health
- Set pool_recycle to 3600 seconds
- Implement connection retry logic

Performance: Reduces connection overhead by 60%"
```

### Commit 7: feat(cache): Implement Redis caching strategy
```bash
# After implementing caching
git add src/services/cache_service.py
git commit -m "feat(cache): Implement Redis caching strategy

- Add Redis backend for caching
- Implement cache-aside pattern
- Set TTL to 3600 seconds
- Add cache invalidation logic

Performance: 90% reduction in AI API costs"
```

### Commit 8: test(coverage): Increase test coverage to 80%
```bash
# After adding tests
git add tests/
git commit -m "test(coverage): Increase test coverage to 80%

- Add missing unit tests for services
- Create integration tests for API endpoints
- Add performance benchmarks
- Fix all failing tests

Coverage: Increased from 63% to 80%"
```

### Commit 9: deploy(railway): Configure production deployment
```bash
# After Railway configuration
git add railway.toml
git add nixpacks.toml
git commit -m "deploy(railway): Configure production deployment

- Update Railway configuration for production
- Configure health checks and monitoring
- Set proper environment variables
- Add deployment automation

Deployment: Ready for Railway platform"
```

## Commit Guidelines

### Format
```
<type>(<scope>): <subject>

<body>
- What: Specific changes made
- Why: Business/technical reason
- How: Implementation approach

<footer>
Breaking Changes: [if any]
Security: [if applicable]
Performance: [metrics]
Coverage: [test coverage]
References: [issues, research]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `chore`: Maintenance task
- `docs`: Documentation
- `test`: Testing
- `perf`: Performance
- `deploy`: Deployment
- `refactor`: Code refactoring

### Best Practices
1. One logical change per commit
2. Write tests before implementation
3. Include metrics where applicable
4. Reference research/issues
5. Document breaking changes
6. Keep commits atomic and reversible

## Verification Checklist

Before each commit:
- [ ] Code compiles without errors
- [ ] Tests pass for changed code
- [ ] Linting passes
- [ ] Documentation updated
- [ ] Commit message follows format
- [ ] Changes are atomic
- [ ] No sensitive data included

## Push Strategy

1. Create feature branch for each phase
2. Push atomic commits incrementally
3. Create PR with full description
4. Self-review before merge
5. Tag releases appropriately

---

**Ready to execute commits 1-4 immediately**
**Commits 5-9 pending implementation**