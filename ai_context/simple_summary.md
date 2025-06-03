# AI Context - Simple Summary
**Generated**: 2025-06-02 20:30:02

## 🎯 What You Should Work On Right Now

🚨 **FIX THIS FIRST**: GCP Project ID is set to placeholder - blocks all cloud services

**Quick Fix**: `export GCP_PROJECT_ID=ai-content-factory-460918`
**Verify**: `echo $GCP_PROJECT_ID`

Until this is fixed, everything else is blocked.

## 👤 Human Actions Required

**3 actions need your personal attention**

These actions require human judgment, accounts, or manual steps that LLM cannot perform:

### 1. Human decisions and manual tasks pending
**Source**: tasks/user_input_required.md
**Action**: Review tasks/user_input_required.md for required actions

### 2. Human decisions and manual tasks pending
**Source**: docs/archive/user_inputs/user_input_required_final.md
**Action**: Review docs/archive/user_inputs/user_input_required_final.md for required actions

### 3. Missing API keys: OPENAI_API_KEY, GEMINI_API_KEY
**Source**: environment_setup
**Action**: Set up API keys for external services (requires accounts/billing)

**Important**: Complete these human actions before expecting full system functionality.


## 📁 Available Context Files

**For LLM Analysis**:
- `complete_codebase.md` - Complete technical context (use for complex questions)
- `project_overview.md` - Current state and immediate goals
- `quick_reference.md` - API endpoints and common patterns
- `issue_analysis.md` - Specific problems and their solutions

- `user_actions_required.md` - Human-only tasks that need your attention

## 🚀 Ready-to-Use LLM Prompts

### Quick Debug Session
**When**: Something is broken, need immediate help
```
# Quick Debug Help Needed

**Project**: AI Content Factory (FastAPI + GCP + Vertex AI)

**Problem**: [Describe what's broken]

**Error**: [Paste any error messages]

**Context Available**:
- Complete codebase: `ai_context/complete_codebase.md`
- Known issues: `ai_context/issue_analysis.md`
- API reference: `ai_context/quick_reference.md`

**Need**: Quick fix with explanation. What's wrong and how do I fix it?
```

### Feature Implementation
**When**: Building something new
```
# Feature Implementation Help

**Project**: AI Content Factory (FastAPI + GCP + Vertex AI)

**Goal**: [What you want to build]

**Context Available**:
- Full technical context: `ai_context/complete_codebase.md`
- API patterns: `ai_context/quick_reference.md`

**Request**:
1. How should I implement this?
2. What existing patterns should I follow?
3. Show me code examples that fit the project style

Keep it practical and focused on getting working code.
```

### Code Review
**When**: Get feedback on what you built
```
# Code Review Request

**Project**: AI Content Factory

**What I built**: [Brief description]

**Files changed**: [List main files]

**Context**: See `ai_context/complete_codebase.md` for full project context

**Review focus**:
1. Does this follow project patterns?
2. Any obvious issues or improvements?
3. Does the approach make sense?

Be direct and specific with feedback.
```

## 🔧 Quick Commands

**Update context**: `python scripts/simple_smart_context.py`
**Check blockers**: Review issue_analysis.md
**Debug API**: `curl http://localhost:8080/healthz`
**Human actions**: Review user_actions_required.md

---
*Keep it simple. Fix blockers, complete human actions, then build features.*
