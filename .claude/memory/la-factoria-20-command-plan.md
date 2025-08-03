# La Factoria 20 Command Plan

## Target: Reduce from 62 commands to 20 commands (68% reduction)

### 7 Core La Factoria Task Commands (TASK-001 through TASK-007)

1. **`/la-factoria-init`** - TASK-001: Initialize structure + Railway
2. **`/la-factoria-content`** - TASK-002: Basic content generation with AI
3. **`/la-factoria-langfuse`** - TASK-003: External prompt management  
4. **`/la-factoria-postgres`** - TASK-004: Railway PostgreSQL (✅ EXISTS)
5. **`/la-factoria-frontend`** - TASK-005: Minimal frontend
6. **`/la-factoria-gdpr`** - TASK-006: User deletion compliance
7. **`/la-factoria-monitoring`** - TASK-007: Basic stats and uptime

### 13 Essential Development Commands

8. **`/project`** - Construction orchestrator (✅ EXISTS)
9. **`/test`** - TDD test execution
10. **`/deploy`** - Railway deployment
11. **`/quality`** - Quality gates and validation
12. **`/debug`** - Development debugging
13. **`/security`** - Security validation
14. **`/env`** - Environment setup
15. **`/git`** - Git operations
16. **`/config`** - Configuration management
17. **`/logs`** - Log management
18. **`/docs`** - Documentation generation
19. **`/backup`** - System backup
20. **`/health`** - Health monitoring

## Commands to DELETE (42 commands)

All commands not in the list above should be deleted, including:
- Granular specialized commands (DAG orchestration, swarm coordination, etc.)
- Enterprise complexity commands
- Redundant commands that overlap with the 20 core commands
- Generic template commands not adapted to La Factoria

## Implementation Strategy

1. **Create 5 missing La Factoria task commands** (init, content, langfuse, frontend, gdpr, monitoring)
2. **Keep 2 existing transformed commands** (project, la-factoria-postgres)  
3. **Identify 13 essential development commands** from existing 60 commands
4. **Delete remaining 42 commands** that don't make the cut

## Success Criteria

- **Simple Focus**: Each command serves a specific La Factoria purpose
- **TDD Integration**: All commands support test-first development
- **Railway Focus**: Deployment commands target Railway platform
- **Educational Content**: All La Factoria commands support educational content generation
- **Quality Gates**: All commands include quality validation