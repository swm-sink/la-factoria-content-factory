# La Factoria Simplification - Enhanced Task Tracker with Anti-Hallucination Context

## ⚠️ CRITICAL CONTEXT FOR LLM (August 2025)

This enhanced task tracker includes comprehensive research context to prevent hallucination. Each task contains:

- Exact commands and configurations
- Current best practices as of August 2025
- Common pitfalls and how to avoid them
- Expected outputs and verification steps
- Tool-specific versions and compatibility notes

## Progress Overview

**Total Tasks**: 37 (34 planned + 3 extra completed)  
**Completed**: 9 tasks ✅  
**In Progress**: 0 tasks 🚧  
**Pending**: 28 tasks ⏳  
**Completion**: 24%

## Week 0: Discovery Phase (0/3 completed)

### **DISCOVER-001**: Create user survey (2h)

**🎯 Objective**: Gather essential qualitative feedback from 1-10 users to validate simplification decisions and identify which "over-engineered" features are actually valued.

**🔧 Tool Selection (August 2025)**:

1. **Google Forms** (RECOMMENDED)
   - URL: <https://forms.google.com>
   - Cost: FREE
   - Why: Zero cost, automatic data collection to Google Sheets, easy export to CSV
   - Setup: Use existing Google account, no additional configuration needed

2. **Typeform** (Alternative)
   - URL: <https://www.typeform.com>
   - Cost: Free tier allows 10 responses/month (sufficient for 1-10 users)
   - Why: Better UX but limits may be restrictive

**📋 Exact Survey Questions** (Copy-paste ready):

```
Survey Title: La Factoria User Feedback - Help Us Simplify!

Introduction:
"We're simplifying La Factoria to better serve you. This 5-minute survey will help us understand what features matter most. Your responses are confidential and will only be used to improve the service."

Q1. How often do you use La Factoria?
○ Daily
○ 2-3 times per week  
○ Weekly
○ Monthly
○ Rarely

Q2. Which content types do you generate? (Check all that apply)
□ Study Guide
□ Flashcards
□ Podcast Script
□ One-Pager Summary
□ Detailed Reading
□ FAQ
□ Reading Questions
□ Master Outline
□ Other: _______

Q3. What's your PRIMARY use case?
○ Teaching/Education
○ Content Creation
○ Personal Learning
○ Business/Professional
○ Other: _______

Q4. Rate the quality of generated content (1-5 scale)
○ 1 - Poor
○ 2 - Below Average
○ 3 - Average
○ 4 - Good
○ 5 - Excellent

Q5. How important are these features to you?

Export to PDF/Word:
○ Critical ○ Important ○ Nice to have ○ Not needed

99.9% Uptime guarantee:
○ Critical ○ Important ○ Nice to have ○ Not needed

Data deletion capability:
○ Critical ○ Important ○ Nice to have ○ Not needed

Detailed usage analytics:
○ Critical ○ Important ○ Nice to have ○ Not needed

Q6. What ONE improvement would make La Factoria more valuable?
[Open text field]

Q7. Any features you DON'T use or find unnecessary?
[Open text field]
```

**🚀 Implementation Steps**:

1. **Create Form**:

   ```bash
   # No CLI - use web interface
   # 1. Go to https://forms.google.com
   # 2. Click "+" to create new form
   # 3. Copy-paste questions above
   # 4. Enable "Collect email addresses" if user identification needed
   ```

2. **Configure Settings**:
   - Responses → Collect email addresses: ON (if needed)
   - Settings → Collect email addresses: OFF (for anonymity)
   - Settings → Limit to 1 response: ON
   - Settings → Edit after submit: OFF

3. **Test Survey**:

   ```bash
   # Manual testing checklist:
   # 1. Complete survey yourself
   # 2. Verify all questions display correctly
   # 3. Check response collection in Google Sheets
   # 4. Test CSV export: Responses → Download as → .csv
   ```

**📊 Data Collection Plan**:

```bash
# After survey deployment:
# Day 1: Send to all users via email
# Day 3: Send reminder
# Day 5: Close survey and analyze

# Export data:
# Google Forms → Responses → Google Sheets icon
# Google Sheets → File → Download → CSV
```

**🔍 Common Pitfalls & Solutions**:

1. **Pitfall**: Leading questions
   **Solution**: Use neutral language, avoid "Don't you think..." formulations

2. **Pitfall**: Too many questions
   **Solution**: Max 10 questions, 5-minute completion time

3. **Pitfall**: No GDPR compliance
   **Solution**: Add privacy notice: "Responses are anonymous and used only for service improvement"

4. **Pitfall**: Forgetting to test
   **Solution**: Always complete survey yourself before sending

**✅ Quality Gates**:

- [ ] Survey has ≤10 questions
- [ ] Completion time ≤5 minutes
- [ ] Privacy notice included
- [ ] All content types from original system listed
- [ ] Export/uptime/deletion questions included
- [ ] Tested end-to-end with CSV export
- [ ] Response limit appropriate for user count

**📤 Expected Outputs**:

1. Live survey URL (e.g., <https://forms.gle/ABC123xyz>)
2. CSV file with responses after collection period
3. Summary of key findings for next tasks

**🔗 Dependencies for Next Tasks**:

- DISCOVER-002 needs the CSV export
- DISCOVER-003 needs insights on compliance feature importance
- API-004 needs content type priorities
- FEAT-001 needs export format preferences

---

### **DISCOVER-002**: Analyze usage data (4h)

[To be enhanced next...]

### **DISCOVER-003**: Document compliance requirements (2h)

[To be enhanced next...]

## Enhancement Progress Tracking

- [x] DISCOVER-001: Fully enhanced with anti-hallucination context
- [ ] DISCOVER-002: Pending enhancement
- [ ] DISCOVER-003: Pending enhancement
- [ ] SETUP-001: Pending enhancement
- [ ] SETUP-002: Pending enhancement (Railway-specific)
- [ ] SETUP-003: Pending enhancement
- [ ] API-001: Pending enhancement
- [ ] API-002: Pending enhancement
- [ ] API-003: Pending enhancement
- [ ] API-004: Pending enhancement (AI provider integration)
- [ ] FRONT-001: Pending enhancement
- [ ] FRONT-002: Pending enhancement
- [ ] DEPLOY-001: Pending enhancement (Railway deployment)
- [ ] DB-001: Pending enhancement (Railway Postgres)
- [ ] ... [remaining tasks]

## Notes on Enhancement Approach

Each task enhancement includes:

1. **Tool-specific versions** and compatibility (crucial for August 2025 context)
2. **Exact commands** with proper syntax
3. **Configuration examples** that can be copy-pasted
4. **Error messages** and how to resolve them
5. **Testing procedures** with expected outputs
6. **Performance considerations** for the 1-10 user scale
7. **Cost implications** with specific pricing
8. **Security considerations** relevant to the task
