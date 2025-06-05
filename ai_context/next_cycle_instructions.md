# Next Development Cycle Instructions
**Generated**: 2025-06-05 09:12:21

## 🎯 Current Project Status

⚠️ **Project files need attention**

### Files Needing Update:

- Missing project_blockers.md
- Missing CHANGELOG.md
- Found 22 TODO comments in code

## 🚀 Ready for Feature Development

Infrastructure appears to be configured correctly. Ready for:
- API endpoint development
- Content generation features
- Testing and validation
- Performance optimization

## 📋 File Maintenance Tasks

Before starting new development:

- Create Project blockers documentation
- Create Version history
- Review and address TODO items for completeness

## 🔧 Code Cleanup (22 TODOs)

Consider addressing these TODO items:

- Review TODOs in `scripts/smart_ai_context.py`
- Review TODOs in `app/services/comprehensive_content_validator.py`

## 🔄 Development Cycle Guidance

### For Your Next Development Session:

1. **Start with the right context** - Choose the appropriate prompt below
2. **Check current status** - Always review `ai_context/issue_analysis.md` first
3. **Follow project patterns** - Use existing code as templates
4. **Test incrementally** - Verify each change works before moving on
5. **Update documentation** - Keep project files current

### Ready-to-Use Prompts for Different Scenarios:

#### Project Context Prompt
**Use when**: Starting a new debugging/development session

```
# AI Content Factory - Development Session Context

I'm working on the AI Content Factory project (FastAPI + GCP + Vertex AI). Here's the current context:

**Project Mission**: Transform textual input into comprehensive educational content (podcast scripts, study guides, summaries, audio).

**Current Architecture**: FastAPI backend, Vertex AI Gemini for content generation, ElevenLabs for audio, Firestore for persistence, Cloud Run deployment.

**Latest Context Files**:
- See `ai_context/complete_codebase.md` for full technical context
- See `ai_context/project_overview.md` for current state and blockers
- See `ai_context/issue_analysis.md` for specific problems and solutions

**What I need help with**: [Describe your specific issue/goal here]

Please analyze the context and provide specific, actionable guidance for moving forward.
```

#### Feature Development Prompt
**Use when**: Adding new functionality or improving existing features

```
# Feature Development Session

Working on AI Content Factory feature development.

**Current Status**: [Describe current state - working/blocked/partially complete]

**Target Feature**: [Describe what you want to build/improve]

**Context Available**:
- Full codebase: `ai_context/complete_codebase.md`
- API reference: `ai_context/quick_reference.md`
- Current issues: `ai_context/issue_analysis.md`

**Development Approach Needed**:
- Follow project patterns (Pydantic models, FastAPI routes, async patterns)
- Maintain consistency with existing code style
- Add proper error handling and logging
- Include unit tests where appropriate

**Questions**:
1. How should I implement [specific functionality]?
2. What existing patterns should I follow?
3. Are there any architectural considerations I should know about?

Please provide specific implementation guidance with code examples.
```

#### Code Review Prompt
**Use when**: Getting feedback on implementation

```
# Code Review Request

I've implemented [describe what you built] in the AI Content Factory project.

**Files Changed**: [List the files you modified/created]

**Implementation Approach**: [Briefly describe your approach]

**Context for Review**:
- Project architecture: See `ai_context/complete_codebase.md`
- Existing patterns: See `ai_context/quick_reference.md`
- Project standards: Follow FastAPI, Pydantic, async patterns

**Review Focus Areas**:
1. Code quality and consistency with project patterns
2. Error handling and edge cases
3. Performance considerations
4. Security implications
5. Testing coverage

**Specific Questions**:
- [Any specific concerns or areas you want feedback on]

Please provide detailed feedback and specific improvement suggestions.
```

#### Debugging Session Prompt
**Use when**: When something is broken and you need help debugging

```
# Debugging Session - Need Help

Something is broken in the AI Content Factory project and I need debugging help.

**Problem Description**: [Describe what's not working]

**Error Messages**:
```
[Paste any error messages here]
```

**Steps to Reproduce**:
1. [List the steps that trigger the issue]

**Expected vs Actual Behavior**:
- Expected: [What should happen]
- Actual: [What actually happens]

**Context Files**:
- Full codebase: `ai_context/complete_codebase.md`
- Known issues: `ai_context/issue_analysis.md`
- API reference: `ai_context/quick_reference.md`

**What I've Tried**: [List debugging steps you've already attempted]

Please help me:
1. Identify the root cause
2. Provide a fix with explanation
3. Suggest how to prevent similar issues
4. Recommend any additional testing
```

#### Architecture Decision Prompt
**Use when**: Making significant architectural or design decisions

```
# Architecture Decision Needed

I need to make an architectural decision for the AI Content Factory project.

**Decision Context**: [Describe the situation requiring a decision]

**Options Considered**:
1. [Option 1 with pros/cons]
2. [Option 2 with pros/cons]
3. [Other options...]

**Current Architecture Context**:
- See `ai_context/complete_codebase.md` for full system overview
- Current tech stack: FastAPI, GCP, Vertex AI, Firestore, Cloud Run
- See `ai_context/quick_reference.md` for current patterns

**Constraints**:
- [Technical constraints]
- [Business constraints]
- [Time/resource constraints]

**Questions**:
1. Which approach aligns best with the existing architecture?
2. What are the long-term implications of each option?
3. How does this impact testing, deployment, and maintenance?
4. Are there better alternatives I haven't considered?

Please provide a recommendation with detailed reasoning.
```

## 🔧 Workflow Integration

### Before Each Development Session:

1. **Update context**: `python scripts/smart_ai_context.py`
2. **Check for issues**: Review `ai_context/issue_analysis.md`
3. **Choose your prompt**: Use appropriate prompt from above
4. **Start with small steps**: Test frequently

### After Major Changes:

1. **Run tests**: `python -m pytest`
2. **Update documentation**: Modify README, CHANGELOG as needed
3. **Regenerate context**: `python scripts/smart_ai_context.py`
4. **Commit changes**: Git commit with descriptive message

### For Complex Features:

1. **Plan first**: Use Architecture Decision Prompt
2. **Implement incrementally**: Break into small, testable pieces
3. **Get feedback**: Use Code Review Prompt
4. **Document decisions**: Update project files

## 📊 Project Health Summary

- **File Consistency**: NEEDS_ATTENTION
- **Critical Issues**: NO
- **TODO Items**: 22
- **Last Updated**: 2025-06-05 09:12:21

---
*This guide is automatically generated. Re-run `python scripts/smart_ai_context.py` after significant changes.*