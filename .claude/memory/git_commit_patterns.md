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

### Verification Checklist
- [ ] Single logical change
- [ ] All assertions backed by specific file evidence
- [ ] Memory system updated if significant finding
- [ ] Clear rollback path
- [ ] No hallucinated claims
