# AI Content Factory - Context Overview

**Generated**: 2025-06-05 09:12:21

## 📁 Available Files

### For Quick Debugging
- **`project_overview.md`** - Current state, blockers, immediate goals
  - What's working, what's broken, what's next
  - Perfect for "what should I work on?" questions
  - Current task status and known issues

- **`quick_reference.md`** - API endpoints, models, debug commands
  - All endpoints and data models at a glance
  - Common debug commands and quick fixes
  - Perfect for "how do I test this?" questions

### For Deep Analysis
- **`complete_codebase.md`** - Complete technical context (402KB)
  - All source code, configs, documentation
  - For comprehensive code review and architecture questions
  - Everything needed for complex debugging

### For Issue Resolution
- **`issue_analysis.md`** - Built-in issue analysis and quick fixes
  - Identifies critical blockers (like Firestore configuration issues)
  - Provides exact commands to fix common problems
  - Always generated, no API key required

- **`ai_analysis.md`** - AI-generated analysis (optional)
  - Automated issue identification and recommendations
  - Prioritized task list with specific actions
  - Only available if OPENAI_API_KEY is set

## 🚀 Quick Usage

### Common Debugging Scenarios
**"What's broken?"** → Use `project_overview.md`
**"How do I test the API?"** → Use `quick_reference.md`
**"Why isn't this working?"** → Use `complete_codebase.md`
**"What should I do next?"** → Use `ai_analysis.md` (if available)

### Get Automated Insights
1. Set your OpenAI API key: `export OPENAI_API_KEY=your_key`
2. Run: `python scripts/smart_ai_context.py`
3. Check `ai_analysis.md` for AI-generated recommendations

## 🔄 Updates

To regenerate context (recommended after significant code changes):
```bash
python scripts/smart_ai_context.py
```

This system focuses on simplicity and effectiveness:
- One comprehensive file for manual use
- Automated analysis when API key is available
- Clear next steps and actionable recommendations
