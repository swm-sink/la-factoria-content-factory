# DRY/SSOT Analysis Report - La Factoria Project

## Critical Duplication Issues Identified

### 1. Major Duplications

#### CLAUDE.md Files (2 copies)
- **Root**: `/CLAUDE.md` (18,003 lines count)
- **Bangui**: `/.conductor/bangui/CLAUDE.md` (~17,950 lines count)
- **Issue**: Nearly identical content with minor discrepancies
- **Impact**: Confusion about which is authoritative

#### .claude Directories (2 complete copies)
- **Root**: `/.claude/` (full context system)
- **Bangui**: `/.conductor/bangui/.claude/` (full context system)
- **Issue**: Both contain full context systems with differences
- **Impact**: Context drift, maintenance overhead, confusion

#### Prompt Templates (3 locations)
- **Bangui Main**: `/.conductor/bangui/prompts/` (11 files)
- **Archive**: `/.conductor/bangui/archive/langchain/prompts/` (11 files)
- **Context**: Referenced in multiple .claude files
- **Issue**: Same prompts in multiple locations
- **Impact**: Which version is authoritative?

### 2. Documentation Sprawl

#### Reports (20+ scattered files)
- Multiple validation reports
- Architecture reports
- Completion reports
- Progress reports
- **Issue**: No clear organization or lifecycle management

#### Documentation Directories (Multiple)
- `/.conductor/bangui/docs/`
- `/.claude/documentation/`
- Various README.md files
- **Issue**: Documentation scattered across project

### 3. Content Duplication Analysis

#### Validation System (~30% duplicated)
- Validation components described in CLAUDE.md
- Separate validation directory structure
- Multiple validation reports
- **Issue**: Validation information spread across multiple files

#### MEP-CE Protocol (100% duplicated)
- Identical in both CLAUDE.md files
- Referenced in multiple context files
- **Issue**: Complete duplication of methodology

#### Technology Stack (100% duplicated)
- Identical sections in both CLAUDE.md files
- Minor status differences (✅ vs 🔧)
- **Issue**: Status discrepancies between copies

## Single Source of Truth Plan

### 1. Primary Structure (SSOT)

```
la-factoria-content-factory/
├── CLAUDE.md                    # Navigation hub only (links to context)
├── .claude/                     # SINGLE context system (delete bangui copy)
│   ├── PROJECT.md              # Core project info (SSOT)
│   ├── IMPLEMENTATION.md       # Tech stack & status (SSOT)
│   ├── METHODOLOGY.md          # MEP-CE protocol (SSOT)
│   ├── context/                # All context files
│   ├── domains/                # Domain organization
│   └── memory/                 # Project memory
├── .conductor/                  
│   └── bangui/                 # Working directory
│       ├── src/                # Source code
│       ├── tests/              # Test files
│       ├── prompts/            # SSOT for prompts
│       ├── docs/               # User documentation only
│       └── reports/            # Organized reports
└── archive/                    # Historical/deprecated content
```

### 2. Information Mapping (SSOT Locations)

| Information Type | Current Locations | SSOT Location |
|-----------------|------------------|---------------|
| Project Overview | 2 CLAUDE.md files | `.claude/PROJECT.md` |
| Tech Stack | 2 CLAUDE.md files | `.claude/IMPLEMENTATION.md` |
| MEP-CE Protocol | 2 CLAUDE.md files | `.claude/METHODOLOGY.md` |
| Validation System | CLAUDE.md + directories | `.claude/validation/README.md` |
| Prompts | 3 directories | `/.conductor/bangui/prompts/` |
| Context System | 2 .claude directories | `/.claude/` (root) |
| Reports | Scattered | `/.conductor/bangui/reports/` |
| User Docs | Multiple locations | `/.conductor/bangui/docs/` |

### 3. CLAUDE.md Transformation

Transform CLAUDE.md into a clean navigation hub:

```markdown
# La Factoria - Claude Code Configuration

## Quick Start
- **Project**: Educational content generation platform
- **Status**: Production ready (Phase 3C complete)
- **Location**: `.conductor/bangui/` (working directory)

## Navigation

### Core Information
- [Project Overview](.claude/PROJECT.md)
- [Implementation Status](.claude/IMPLEMENTATION.md)
- [Development Methodology](.claude/METHODOLOGY.md)

### Context System
- [Master Index](.claude/indexes/master-context-index.md)
- [Domains](.claude/domains/)
- [Examples](.claude/examples/)

### Working Directory
- [Source Code](.conductor/bangui/src/)
- [Tests](.conductor/bangui/tests/)
- [Prompts](.conductor/bangui/prompts/)
- [Documentation](.conductor/bangui/docs/)

### Git Configuration
- Author: swm-sink <stefan.menssink@gmail.com>
- See: [Git Configuration](.conductor/bangui/GIT_CONFIGURATION.md)
```

## Implementation Steps

### Phase 1: Extract Core Information
1. Extract project overview to `.claude/PROJECT.md`
2. Extract tech stack to `.claude/IMPLEMENTATION.md`
3. Extract MEP-CE to `.claude/METHODOLOGY.md`
4. Extract validation to `.claude/validation/README.md`

### Phase 2: Consolidate Directories
1. Compare and merge .claude directories (keep best/latest)
2. Delete duplicate bangui/.claude directory
3. Archive langchain prompts (already in archive)
4. Organize reports into categories

### Phase 3: Update References
1. Update CLAUDE.md as navigation hub
2. Update file imports in context files
3. Fix cross-references
4. Update documentation links

### Phase 4: Clean Up
1. Remove duplicate files
2. Archive deprecated content
3. Validate all links work
4. Test context loading

## Expected Benefits

### Clarity
- Single authoritative source for each piece of information
- Clear navigation structure
- No confusion about which file to update

### Maintenance
- Update information in one place only
- Reduced file count (~30% reduction)
- Clear ownership of information

### Performance
- Faster context loading
- Less memory usage
- Cleaner git history

## Risk Mitigation

### Backup Plan
1. Create full backup before changes
2. Commit current state first
3. Make changes incrementally
4. Test after each phase

### Validation
1. Verify all links work
2. Check context imports
3. Test with Claude Code
4. Confirm no information lost

## Metrics

### Current State
- Files with duplication: ~50
- Total duplicate content: ~15,000 lines
- Maintenance overhead: High

### Target State
- Files with duplication: 0
- Total duplicate content: 0
- Maintenance overhead: Low

## Decision Required

This reorganization will:
1. Eliminate all duplication
2. Establish clear SSOT for all information
3. Create clean navigation structure
4. Reduce maintenance overhead

**Recommendation**: Proceed with full reorganization following the phases above.