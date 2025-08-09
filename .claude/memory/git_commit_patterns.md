# Git Commit Patterns & Best Practices

## Atomic Commit Strategy

### Commit Categories
1. **feat**: New feature additions
2. **fix**: Bug fixes
3. **docs**: Documentation updates
4. **refactor**: Code refactoring without feature changes
5. **analysis**: Code/architecture analysis findings
6. **memory**: Updates to .claude/memory system
7. **config**: Configuration updates

### Atomic Commit Rules
- One logical change per commit
- Self-contained and reversible
- Clear, descriptive commit messages
- Reference specific files/components changed

### Memory System Integration
Each significant finding/decision should trigger:
1. Immediate memory file update
2. Atomic commit with analysis tag
3. Clear documentation of rationale

### Example Commit Messages
```
analysis: discover GDPR compliance requirements - revise simplification approach

- Found comprehensive user data deletion system in /app/services/user_data_deletion.py
- SLA targets (99.9% uptime) suggest enterprise/contractual obligations
- Extensive audit logging indicates regulatory requirements
- Initial over-engineering assessment was flawed - complexity driven by compliance

Refs: .claude/memory/analysis_learnings.md
```

### Anti-Patterns to Avoid
❌ "WIP" or "misc changes" commits
❌ Mixing multiple logical changes
❌ Commits without clear rationale
❌ Changes without memory system updates

### Anti-Pattern Learnings from Phase 3C

#### 1. API Route Conflicts
**Problem**: Multiple routers defining same endpoints (/health, /ready, /live)
**Solution**: Ensure route uniqueness across all routers
**Commit Pattern**: Fix conflicts FIRST before any other changes

#### 2. Database Type Compatibility
**Problem**: Using PostgreSQL-specific types (UUID) breaks SQLite development
**Solution**: Use database-agnostic types for portability
**Commit Pattern**: Fix compatibility issues before service layer changes

#### 3. Test Model Synchronization
**Problem**: Tests importing non-existent models (QualityAssessmentDB, etc.)
**Solution**: Keep tests synchronized with actual model definitions
**Commit Pattern**: Fix test infrastructure before adding new tests

#### 4. API Path Consistency
**Problem**: Validation scripts using incorrect URL prefixes (/health vs /api/v1/health)
**Solution**: Always verify API route prefixes in client code
**Commit Pattern**: Fix path issues in validation before declaring "ready"

#### 5. Legacy Code Accumulation
**Problem**: Obsolete langchain/ system alongside new implementation
**Solution**: Remove legacy code promptly after migration
**Commit Pattern**: Remove legacy code AFTER all fixes are complete

### Atomic Commit Order Strategy

When multiple issues exist, commit in this order:
1. **Critical Fixes First**: Breaking bugs that prevent functionality
2. **Compatibility Fixes**: Database/API compatibility issues
3. **Test Fixes**: Fix test infrastructure to validate changes
4. **Feature Enhancements**: Add new functionality on fixed foundation
5. **Legacy Cleanup**: Remove obsolete code after all fixes
6. **Documentation**: Update docs to reflect final state
7. **Status Updates**: Mark project milestones last

### Verification Checklist
- [ ] Single logical change
- [ ] All assertions backed by specific file evidence
- [ ] Memory system updated if significant finding
- [ ] Clear rollback path
- [ ] No hallucinated claims
- [ ] Anti-patterns documented in commit message
- [ ] Each commit leaves codebase in working state
