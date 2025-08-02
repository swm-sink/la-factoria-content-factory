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

**🎯 Objective**: Process survey results and any available system logs to create actionable insights for simplification. Focus on identifying unused features and validating assumptions about user needs.

**📊 Input Data Sources**:

1. **Survey Results** (from DISCOVER-001)
   - Format: CSV export from Google Forms
   - Expected location: `./data/survey_results.csv`

2. **System Logs** (if available from current La Factoria)
   - Cloud Function logs from GCP
   - Database query logs
   - API endpoint access patterns

**🐍 Analysis Setup (Python with pandas)**:

```bash
# Create analysis environment
mkdir -p la-factoria-simple-v2/analysis
cd la-factoria-simple-v2/analysis

# Create requirements file
cat > requirements.txt << 'EOF'
pandas==2.1.4
matplotlib==3.8.2
seaborn==0.13.0
jupyter==1.0.0
EOF

# Install dependencies
pip install -r requirements.txt
```

**📈 Analysis Script** (copy-paste ready):

```python
# File: analyze_survey.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import json

# Load survey data
df = pd.read_csv('survey_results.csv')

# Basic statistics for small sample
print(f"Total responses: {len(df)}")
print(f"Response rate: {len(df)}/10 = {len(df)/10*100:.0f}%")

# Analyze content type usage
content_types = df['Which content types do you generate? (Check all that apply)'].str.split(';')
all_types = [item.strip() for sublist in content_types.dropna() for item in sublist]
type_counts = Counter(all_types)

print("\n📊 Content Type Usage:")
for content_type, count in type_counts.most_common():
    percentage = (count / len(df)) * 100
    print(f"  - {content_type}: {count} users ({percentage:.0f}%)")

# Feature importance analysis
features = ['Export to PDF/Word', '99.9% Uptime guarantee',
            'Data deletion capability', 'Detailed usage analytics']

importance_map = {
    'Critical': 4,
    'Important': 3,
    'Nice to have': 2,
    'Not needed': 1
}

print("\n⚡ Feature Importance Scores:")
feature_scores = {}
for feature in features:
    if feature in df.columns:
        scores = df[feature].map(importance_map)
        avg_score = scores.mean()
        feature_scores[feature] = avg_score
        print(f"  - {feature}: {avg_score:.2f}/4.0")
        if avg_score < 2.5:
            print(f"    ⚠️ LOW PRIORITY - Consider removing/simplifying")

# Quality perception
quality_scores = df['Rate the quality of generated content (1-5 scale)']
avg_quality = quality_scores.mean()
print(f"\n✨ Average Quality Score: {avg_quality:.2f}/5.0")
if avg_quality >= 4:
    print("  ✅ Quality is good - maintain current generation approach")
else:
    print("  ⚠️ Quality needs improvement - prioritize AI enhancements")

# Generate insights JSON
insights = {
    "total_users": len(df),
    "top_content_types": dict(type_counts.most_common(3)),
    "unused_content_types": [ct for ct, count in type_counts.items() if count <= 1],
    "low_priority_features": [f for f, score in feature_scores.items() if score < 2.5],
    "quality_acceptable": avg_quality >= 3.5,
    "recommendations": []
}

# Generate recommendations
if len(insights["unused_content_types"]) > 0:
    insights["recommendations"].append(
        f"Remove support for: {', '.join(insights['unused_content_types'])}"
    )

if feature_scores.get('Export to PDF/Word', 0) < 2.5:
    insights["recommendations"].append("Simplify export - plain text only")

if feature_scores.get('99.9% Uptime guarantee', 0) < 3:
    insights["recommendations"].append("Relax SLA to 95% - use Railway's standard tier")

# Save insights
with open('insights.json', 'w') as f:
    json.dump(insights, f, indent=2)

print("\n📝 Insights saved to insights.json")
```

**🔍 Log Analysis** (if GCP logs available):

```bash
# Export logs from GCP
gcloud logging read "resource.type=cloud_function" \
  --project=la-factoria-prod \
  --format=json \
  --limit=1000 > function_logs.json

# Analyze with Python
cat > analyze_logs.py << 'EOF'
import json
from collections import Counter
from datetime import datetime

with open('function_logs.json') as f:
    logs = json.load(f)

# Extract endpoint usage
endpoints = Counter()
for log in logs:
    if 'httpRequest' in log:
        path = log['httpRequest'].get('requestUrl', '')
        if '/generate/' in path:
            content_type = path.split('/generate/')[-1].split('?')[0]
            endpoints[content_type] += 1

print("API Endpoint Usage (last 1000 requests):")
for endpoint, count in endpoints.most_common():
    print(f"  - {endpoint}: {count} requests")
EOF

python analyze_logs.py
```

**⚠️ Small Sample Size Considerations**:

1. **Statistical Significance**: With 1-10 users, avoid complex statistics
   - Use counts and percentages, not p-values
   - Focus on unanimous feedback (100% agreement)
   - Treat split opinions as "needs more investigation"

2. **Qualitative Over Quantitative**:

   ```python
   # Focus on open-ended responses
   print("\n📝 Qualitative Insights:")
   improvements = df['What ONE improvement would make La Factoria more valuable?']
   for idx, comment in enumerate(improvements.dropna()):
       print(f"{idx+1}. {comment}")
   ```

3. **Direct User Contact**: For 1-10 users, consider follow-up interviews

   ```python
   # Generate follow-up questions based on unclear responses
   if feature_scores['Export to PDF/Word'] == 2.5:  # Exactly middle
       print("FOLLOW-UP NEEDED: Export feature importance is unclear")
   ```

**📊 Visualization for Stakeholders**:

```python
# Simple, clear visualizations
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Content type usage
type_df = pd.DataFrame(list(type_counts.items()), columns=['Type', 'Users'])
type_df.plot(kind='bar', x='Type', y='Users', ax=ax1, legend=False)
ax1.set_title('Content Type Usage')
ax1.set_ylabel('Number of Users')

# Feature importance
feature_df = pd.DataFrame(list(feature_scores.items()), columns=['Feature', 'Score'])
feature_df.plot(kind='barh', x='Feature', y='Score', ax=ax2, legend=False)
ax2.set_title('Feature Importance (1-4 scale)')
ax2.axvline(x=2.5, color='red', linestyle='--', label='Priority Threshold')

plt.tight_layout()
plt.savefig('user_insights.png', dpi=150, bbox_inches='tight')
print("📊 Visualization saved to user_insights.png")
```

**✅ Quality Gates**:

- [ ] All survey responses loaded successfully
- [ ] No data privacy violations (no PII in analysis)
- [ ] Insights align with simplification goals
- [ ] Clear recommendations for each major feature
- [ ] Visualizations are readable and professional
- [ ] insights.json created with actionable data

**📤 Expected Outputs**:

1. `insights.json` - Machine-readable recommendations
2. `user_insights.png` - Visualization for stakeholders
3. `analysis_report.md` - Human-readable summary
4. Clear list of features to remove/simplify

**🚨 Common Pitfalls**:

1. **Over-interpreting small data**
   - Wrong: "60% prefer PDF" (when n=5)
   - Right: "3 out of 5 users mentioned PDF export"

2. **Ignoring context**
   - Check if low-usage features are new or poorly documented
   - Verify if "unused" features are actually backup/compliance

3. **Missing edge cases**
   - One power user might need a "rarely used" feature
   - Legal requirements might mandate "unwanted" features

**🔗 Impact on Other Tasks**:

- **API-004**: Use only top 3 content types initially
- **FEAT-001**: Skip if export importance < 2.5
- **MON-001**: Minimal monitoring if uptime importance < 3
- **GDPR-001**: Simple delete endpoint if score < 2
- **DB Schema**: Optimize for discovered usage patterns

### **DISCOVER-003**: Document compliance requirements (2h)

**🎯 Objective**: Determine actual legal/compliance requirements vs perceived requirements. For a 1-10 user system, distinguish between "nice-to-have" enterprise features and legally mandated requirements.

**⚖️ Key Questions to Answer**:

1. Is the business actually subject to GDPR? (EU users or EU-based company)
2. What data is being collected and stored?
3. Are there contractual SLA obligations with existing users?
4. What are the actual penalties for non-compliance at this scale?

**📋 Compliance Checklist Script** (create as `check_compliance.py`):

```python
#!/usr/bin/env python3
# File: la-factoria-simple-v2/scripts/check_compliance.py

print("=== La Factoria Compliance Requirements Checker ===\n")

# Initialize findings
compliance_requirements = {
    "gdpr": {"required": False, "reason": "", "implementation": ""},
    "data_deletion": {"required": False, "reason": "", "implementation": ""},
    "audit_logging": {"required": False, "reason": "", "implementation": ""},
    "sla_monitoring": {"required": False, "reason": "", "implementation": ""},
    "data_encryption": {"required": True, "reason": "Basic security", "implementation": "Use Railway's HTTPS"}
}

# Question 1: GDPR Applicability
print("1. GDPR Applicability Check:")
eu_users = input("   Do you have ANY users in the EU? (yes/no): ").lower() == "yes"
eu_company = input("   Is the company based in the EU? (yes/no): ").lower() == "yes"

if eu_users or eu_company:
    compliance_requirements["gdpr"]["required"] = True
    compliance_requirements["gdpr"]["reason"] = "EU users or EU-based company"
    print("   ✅ GDPR applies")
else:
    print("   ❌ GDPR does not apply")

# Question 2: Personal Data Collection
print("\n2. Personal Data Collection:")
stores_email = input("   Does the system store user emails? (yes/no): ").lower() == "yes"
stores_name = input("   Does the system store user names? (yes/no): ").lower() == "yes"
stores_content = input("   Does generated content contain personal info? (yes/no): ").lower() == "yes"

if stores_email or stores_name:
    compliance_requirements["data_deletion"]["required"] = True
    compliance_requirements["data_deletion"]["reason"] = "Stores personal identifiable information"
    if compliance_requirements["gdpr"]["required"]:
        compliance_requirements["data_deletion"]["implementation"] = "Implement /delete-account endpoint"
    else:
        compliance_requirements["data_deletion"]["implementation"] = "Simple admin script sufficient"

# Question 3: Contractual Obligations
print("\n3. Contractual/SLA Obligations:")
has_sla = input("   Do you have written SLA agreements? (yes/no): ").lower() == "yes"
if has_sla:
    sla_uptime = input("   What uptime % is promised? (e.g., 99.9): ")
    compliance_requirements["sla_monitoring"]["required"] = True
    compliance_requirements["sla_monitoring"]["reason"] = f"Contractual {sla_uptime}% uptime"
    compliance_requirements["sla_monitoring"]["implementation"] = "Use Railway metrics + uptime monitoring"

# Question 4: Industry Regulations
print("\n4. Industry-Specific Regulations:")
education_minors = input("   Do you serve educational content to minors? (yes/no): ").lower() == "yes"
if education_minors:
    print("   ⚠️  COPPA/FERPA may apply - consult legal counsel")
    compliance_requirements["audit_logging"]["reason"] = "Educational services to minors"

# Generate recommendations
print("\n=== COMPLIANCE RECOMMENDATIONS ===\n")

must_implement = []
nice_to_have = []
can_skip = []

for feature, details in compliance_requirements.items():
    if details["required"]:
        must_implement.append(f"- {feature}: {details['reason']}")
        if details.get("implementation"):
            must_implement.append(f"  Implementation: {details['implementation']}")
    else:
        can_skip.append(f"- {feature}: Not required for your use case")

print("MUST IMPLEMENT:")
for item in must_implement:
    print(item)

print("\nCAN SKIP (for MVP):")
for item in can_skip:
    print(item)

# Save to file
with open('compliance_requirements.json', 'w') as f:
    import json
    json.dump(compliance_requirements, f, indent=2)

print("\n✅ Requirements saved to compliance_requirements.json")
```

**📚 GDPR for Small Applications (August 2025 Context)**:

```markdown
# GDPR Simplified for 1-10 User Applications

## When GDPR Applies:
- ✅ ANY user in the EU (even 1 user)
- ✅ Company based in the EU
- ❌ US company with only US users

## Minimum GDPR Requirements (not the "enterprise" version):

1. **Privacy Policy** (can be simple):
   ```html
   <!-- Add to your HTML -->
   <footer>
     <a href="/privacy">Privacy Policy</a>
   </footer>
   ```

2. **Consent** (can be implicit for existing users):

   ```python
   # In your user registration
   terms_accepted = True  # Checkbox on signup form
   ```

3. **Data Deletion** (doesn't need to be instant):

   ```python
   @app.delete("/api/delete-my-data")
   async def delete_user_data(user_id: str = Depends(get_current_user)):
       # Delete from database
       await db.execute("DELETE FROM users WHERE id = ?", user_id)
       await db.execute("DELETE FROM content WHERE user_id = ?", user_id)
       return {"message": "Data deletion scheduled"}
   ```

4. **Data Export** (can be manual for 1-10 users):

   ```python
   # Can be a simple admin script, not an API endpoint
   python export_user_data.py --user-id=123 > user_123_data.json
   ```

## What You DON'T Need (despite what enterprise blogs say)

- ❌ Instant deletion (30 days is fine)
- ❌ Automated data portability API
- ❌ Data Protection Officer (DPO)
- ❌ Complex consent management platform
- ❌ Detailed audit logs (basic logs sufficient)

```

**🔍 Research Current System** (commands to run):

```bash
# Check if current system has EU users
gcloud sql databases list --instance=la-factoria-prod

# Export users table to check locations (if available)
gcloud sql export csv la-factoria-prod gs://temp-export/users.csv \
  --database=main --query="SELECT country FROM users"

# Check existing privacy policy
find . -name "*privacy*" -o -name "*terms*" -o -name "*gdpr*"

# Check for existing deletion mechanisms  
grep -r "delete.*user" --include="*.py" --include="*.js"
```

**📝 Documentation Template** (`compliance_docs.md`):

```markdown
# La Factoria Compliance Documentation

## Overview
- **User Count**: 1-10 users
- **Geography**: [TO BE DETERMINED]
- **Data Collected**: Email, generated content
- **Industry**: Education/Content Generation

## Compliance Requirements

### Required by Law:
1. **Basic Data Security**
   - Implementation: Railway provides HTTPS by default
   - Status: ✅ Covered by platform

2. **[GDPR - IF APPLICABLE]**
   - Privacy Policy: Required
   - Data Deletion: Required within 30 days
   - Implementation: Simple delete endpoint

### Business Requirements:
1. **Uptime SLA**: [FROM USER SURVEY/CONTRACTS]
   - Current: 99.9% promised
   - Actual need: [TO BE DETERMINED]

### Not Required:
1. **Complex audit logging** - Basic Railway logs sufficient
2. **Instant deletion** - 30-day window acceptable
3. **Automated GDPR export** - Manual process fine for 1-10 users

## Implementation Priority:
1. HIGH: HTTPS (✅ Done via Railway)
2. MEDIUM: Delete endpoint (if GDPR applies)
3. LOW: Privacy policy page
4. SKIP: Complex audit systems
```

**⚠️ Common Over-Engineering Traps**:

1. **"Enterprise GDPR"**:
   - Wrong: Building complex deletion workflows
   - Right: Simple DELETE query with 30-day execution

2. **"Bank-Level Security"**:
   - Wrong: Complex audit trails for every action
   - Right: Railway's default logging + HTTPS

3. **"100% GDPR Automated"**:
   - Wrong: Building automated data export APIs
   - Right: Admin script for rare requests

**🛠️ Simple Implementations**:

```python
# Minimal GDPR compliance for FastAPI

# 1. Privacy endpoint
@app.get("/privacy")
async def privacy_policy():
    return FileResponse("static/privacy.html")

# 2. Simple deletion
@app.delete("/api/users/me")
async def delete_my_account(user = Depends(get_current_user)):
    # Log the request
    logger.info(f"Deletion requested for user {user.id}")

    # Schedule deletion (can be manual for 1-10 users)
    await db.execute(
        "INSERT INTO deletion_requests (user_id, requested_at) VALUES (?, ?)",
        user.id, datetime.now()
    )

    return {"message": "Account deletion requested. Will be processed within 30 days."}

# 3. Basic consent tracking
@app.post("/api/users")
async def create_user(email: str, accepted_terms: bool):
    if not accepted_terms:
        raise HTTPException(400, "Must accept terms")

    # Store consent timestamp
    user_id = await db.execute(
        "INSERT INTO users (email, terms_accepted_at) VALUES (?, ?)",
        email, datetime.now()
    )
    return {"id": user_id}
```

**✅ Quality Gates**:

- [ ] Determined if GDPR actually applies
- [ ] Checked for existing contractual SLAs
- [ ] Identified personal data being stored
- [ ] Created compliance_requirements.json
- [ ] Documented "must have" vs "nice to have"
- [ ] Avoided enterprise-level over-engineering

**📤 Expected Outputs**:

1. `compliance_requirements.json` - Machine-readable requirements
2. `compliance_docs.md` - Human-readable documentation
3. Clear list of required vs optional compliance features
4. Simple implementation examples for required features

**🔗 Impact on Other Tasks**:

- **GDPR-001**: Skip if no EU users, simplify if applies
- **MON-001**: Minimal if no SLA requirements
- **AUTH-001**: Add consent tracking if GDPR applies
- **DB-002**: Add deletion_requests table if needed
- **DOC-001**: Include privacy policy if required

## Week 1: Foundation Phase (5/10 completed)

### **SETUP-001**: Create repository structure (1h)

**🎯 Objective**: Set up a clean, organized repository structure optimized for FastAPI + simple frontend deployment. Focus on clarity and maintainability for a "vibe coder" who prefers simplicity.

**📁 Repository Structure (August 2025 Best Practices)**:

```bash
# Create the complete directory structure
mkdir -p la-factoria-simple-v2/{app,tests,frontend,scripts,docs}
cd la-factoria-simple-v2

# Create subdirectories
mkdir -p app/{api,services,models,core}
mkdir -p tests/{unit,integration}
mkdir -p frontend/{static,templates}
mkdir -p scripts/{migration,analysis}
```

**🏗️ Complete File Structure**:

```
la-factoria-simple-v2/
├── .gitignore              # Git ignore file
├── .env.example            # Example environment variables
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── runtime.txt            # Python version for Railway
├── railway.json           # Railway configuration
├── Procfile              # Process file for deployment
├── pytest.ini            # Pytest configuration
├── pyproject.toml        # Python project metadata
│
├── app/                  # Backend application
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Configuration management
│   │
│   ├── api/             # API endpoints
│   │   ├── __init__.py
│   │   ├── health.py    # Health check endpoint
│   │   ├── generate.py  # Content generation
│   │   └── auth.py      # Authentication endpoints
│   │
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── ai_service.py      # AI/LLM integration
│   │   ├── auth_service.py    # Authentication logic
│   │   └── content_service.py # Content processing
│   │
│   ├── models/          # Pydantic models
│   │   ├── __init__.py
│   │   ├── requests.py  # Request models
│   │   ├── responses.py # Response models
│   │   └── database.py  # Database models
│   │
│   └── core/            # Core utilities
│       ├── __init__.py
│       ├── security.py  # Security utilities
│       ├── prompts.py   # Prompt templates
│       └── exceptions.py # Custom exceptions
│
├── frontend/            # Simple frontend
│   ├── index.html      # Main HTML file
│   ├── static/
│   │   ├── style.css   # Minimal CSS
│   │   └── script.js   # Vanilla JavaScript
│   └── templates/      # HTML templates (if needed)
│
├── tests/              # Test suite
│   ├── __init__.py
│   ├── conftest.py     # Pytest fixtures
│   ├── unit/
│   │   ├── test_services.py
│   │   └── test_models.py
│   └── integration/
│       └── test_api.py
│
├── scripts/            # Utility scripts
│   ├── check_compliance.py  # From DISCOVER-003
│   └── analyze_survey.py    # From DISCOVER-002
│
└── docs/               # Documentation
    ├── API.md          # API documentation
    ├── DEPLOYMENT.md   # Deployment guide
    └── MIGRATION.md    # Migration from v1
```

**📝 Essential Files Content**:

**1. `.gitignore`** (Python + IDE + OS):

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
htmlcov/
.tox/
*.egg-info/
dist/
build/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
data/
uploads/
```

**2. `.env.example`** (Document all required variables):

```bash
# Railway provides automatically
PORT=8000
RAILWAY_ENVIRONMENT=production

# API Keys (required)
OPENAI_API_KEY=sk-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...

# Database (Railway provides)
DATABASE_URL=postgresql://...

# App Configuration
LOG_LEVEL=info
API_KEY_LENGTH=32
DAILY_TOKEN_LIMIT=100000

# Optional
SENTRY_DSN=
SLACK_WEBHOOK_URL=
```

**3. `README.md`** (Clear, concise documentation):

```markdown
# La Factoria Simple v2

A simplified content generation service using AI, built for 1-10 users.

## Quick Start

1. Clone and setup:
   ```bash
   git clone <repo-url>
   cd la-factoria-simple-v2
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements-dev.txt
   ```

2. Configure environment:

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Run locally:

   ```bash
   uvicorn app.main:app --reload
   # Visit http://localhost:8000
   ```

4. Run tests:

   ```bash
   pytest
   ```

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for Railway deployment.

## Architecture

- **Backend**: FastAPI + OpenAI/Anthropic
- **Frontend**: Simple HTML/CSS/JS
- **Database**: PostgreSQL (via Railway)
- **Monitoring**: Langfuse
- **Hosting**: Railway

## API Documentation

Once running, visit:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

```

**4. `requirements.txt`** (Production dependencies):
```txt
# Core
fastapi==0.110.3
uvicorn[standard]==0.29.0
python-multipart==0.0.9

# AI/LLM
openai==1.35.10
langfuse==2.38.2
tiktoken==0.7.0

# Database
sqlalchemy==2.0.30
asyncpg==0.29.0
alembic==1.13.1

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1

# Utilities
pydantic==2.7.4
pydantic-settings==2.3.4
tenacity==8.4.2
httpx==0.27.0
```

**5. `requirements-dev.txt`** (Development dependencies):

```txt
# Include production
-r requirements.txt

# Testing
pytest==8.2.2
pytest-asyncio==0.23.7
pytest-cov==5.0.0
pytest-mock==3.14.0

# Code quality
black==24.4.2
flake8==7.0.0
isort==5.13.2
mypy==1.10.0

# Development
ipython==8.24.0
pre-commit==3.7.1
```

**6. `pyproject.toml`** (Modern Python configuration):

```toml
[tool.black]
line-length = 88
target-version = ['py311', 'py312']

[tool.isort]
profile = "black"
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "-v --cov=app --cov-report=html"

[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true
strict_optional = true
```

**7. `app/__init__.py`**:

```python
"""La Factoria Simple v2 - Simplified content generation service."""

__version__ = "2.0.0"
```

**8. `app/main.py`** (FastAPI app skeleton):

```python
"""Main FastAPI application."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import health, auth, generate
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    print(f"Starting La Factoria v2 on port {settings.PORT}")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="La Factoria Simple",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.SHOW_DOCS else None,
    redoc_url="/redoc" if settings.SHOW_DOCS else None,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(generate.router, prefix="/api/v1", tags=["generate"])


@app.get("/")
async def root():
    """Serve the frontend."""
    with open("frontend/index.html") as f:
        return f.read()
```

**🚀 Initialization Script** (`scripts/init_project.sh`):

```bash
#!/bin/bash
# Initialize La Factoria Simple v2 project

echo "🚀 Initializing La Factoria Simple v2..."

# Create directory structure
mkdir -p app/{api,services,models,core}
mkdir -p tests/{unit,integration}
mkdir -p frontend/{static,templates}
mkdir -p scripts/{migration,analysis}
mkdir -p docs

# Create __init__.py files
find app tests -type d -exec touch {}/__init__.py \;

# Create essential files
touch .gitignore .env.example README.md requirements.txt requirements-dev.txt
touch runtime.txt railway.json Procfile pytest.ini pyproject.toml
touch app/main.py app/config.py
touch frontend/index.html frontend/static/{style.css,script.js}

echo "✅ Project structure created!"
echo "📝 Next steps:"
echo "1. Copy content from this guide to each file"
echo "2. Run: pip install -r requirements-dev.txt"
echo "3. Configure .env file"
echo "4. Start coding!"
```

**⚠️ Common Mistakes to Avoid**:

1. **Over-complicating structure**:
   - Wrong: Deep nesting with many empty folders
   - Right: Flat structure with clear purpose

2. **Missing **init**.py**:

   ```bash
   # Always create these for Python packages
   find app tests -type d -exec touch {}/__init__.py \;
   ```

3. **Hardcoding configuration**:
   - Wrong: `API_KEY = "sk-123"` in code
   - Right: Use environment variables via config.py

4. **No .env.example**:
   - Always provide example with all required vars
   - Never commit actual .env file

**✅ Quality Gates**:

- [ ] All directories created with proper structure
- [ ] .gitignore includes all necessary patterns
- [ ] .env.example documents all variables
- [ ] README.md has clear quick start
- [ ] requirements.txt has pinned versions
- [ ] **init**.py in all Python packages
- [ ] pyproject.toml configured for tools

**📤 Expected Outputs**:

1. Complete directory structure
2. All essential configuration files
3. Python package structure ready
4. Development environment configured

**🔗 Impact on Other Tasks**:

- All subsequent tasks depend on this structure
- **API-001**: Will create `app/api/health.py`
- **TEST-001**: Will use `tests/` structure
- **DEPLOY-001**: Uses railway.json and Procfile

### **SETUP-002**: Initialize Railway project (1h)

**🎯 Objective**: Set up a new Railway project optimized for FastAPI deployment with minimal configuration. Focus on simplicity and cost-effectiveness for 1-10 users.

**🚂 Railway Context (August 2025)**:

- Railway has become the go-to platform for simple deployments
- Free tier includes: 500 hours/month, 100GB bandwidth
- Automatic HTTPS, zero-config deployments
- Built-in PostgreSQL with 1GB free tier

**📋 Prerequisites Check**:

```bash
# 1. Install Railway CLI (latest version as of Aug 2025)
# macOS
brew install railway

# Linux/WSL
curl -fsSL https://railway.app/install.sh | sh

# Verify installation
railway --version
# Expected: railway version 3.5.1 or higher

# 2. Check Python version
python --version
# Expected: Python 3.11 or 3.12 (Railway's current default)

# 3. Ensure you're in the project directory
cd la-factoria-simple-v2
```

**🚀 Railway Project Initialization**:

```bash
# Step 1: Login to Railway
railway login
# This opens browser for GitHub/email authentication

# Step 2: Create new project
railway init
# When prompted:
# - Project name: la-factoria-simple
# - Environment: production (default)

# Step 3: Link to GitHub (RECOMMENDED for auto-deploy)
railway link
# Select: "Empty Project" (we'll configure it ourselves)

# Step 4: Set Python buildpack
echo "python==3.12.*" > runtime.txt

# Step 5: Create Railway configuration
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  },
  "environments": {
    "production": {
      "variables": {
        "PYTHON_VERSION": "3.12",
        "PORT": "8000"
      }
    }
  }
}
EOF

# Step 6: Create Procfile (backup for railway.json)
echo "web: uvicorn app.main:app --host 0.0.0.0 --port $PORT" > Procfile
```

**🔧 Environment Variables Setup**:

```bash
# Set essential environment variables
railway variables set NODE_ENV=production
railway variables set LOG_LEVEL=info

# View current variables
railway variables
```

**💰 Cost Optimization for 1-10 Users**:

```bash
# Configure auto-sleep for low traffic
railway variables set RAILWAY_AUTO_SLEEP=true
railway variables set RAILWAY_SLEEP_AFTER_MINS=10

# This ensures the app sleeps after 10 mins of inactivity
# First request will have ~5 second cold start
# Saves ~70% on compute costs
```

**🐍 FastAPI-Specific Configuration**:

```python
# app/main.py - Railway-optimized FastAPI setup
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="La Factoria Simple",
    version="2.0.0",
    docs_url="/docs",  # Keep docs in production for small team
    redoc_url="/redoc"
)

# Railway provides PORT env variable
PORT = int(os.environ.get("PORT", 8000))

# Health check for Railway
@app.get("/health")
async def health():
    return {"status": "healthy", "port": PORT}

# Configure CORS for Railway's dynamic URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://*.railway.app"],  # Railway domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**⚠️ Common Railway Pitfalls & Solutions**:

1. **Port Binding Error**:

   ```bash
   # Wrong: Hardcoded port
   uvicorn app.main:app --port 8000

   # Right: Use PORT env variable
   uvicorn app.main:app --port $PORT
   ```

2. **Build Failures**:

   ```bash
   # Debug build issues
   railway logs --build

   # Common fix: Specify Python version
   echo "python==3.12.*" > runtime.txt
   ```

3. **Secret Management**:

   ```bash
   # NEVER commit secrets. Use Railway variables:
   railway variables set OPENAI_API_KEY=sk-...
   railway variables set DATABASE_URL=postgresql://...
   ```

4. **GitHub Integration Issues**:

   ```bash
   # If auto-deploy fails, check:
   railway status
   railway link --environment production
   ```

**📝 Project Structure for Railway**:

```
la-factoria-simple-v2/
├── railway.json          # Railway configuration
├── Procfile             # Backup start command
├── runtime.txt          # Python version
├── requirements.txt     # Python dependencies
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI app
│   └── ...
└── tests/
```

**🧪 Local Testing with Railway Environment**:

```bash
# Run locally with Railway environment
railway run python -m uvicorn app.main:app --reload

# This loads all Railway variables locally
# Ensures local behavior matches production
```

**✅ Quality Gates**:

- [ ] Railway CLI installed and authenticated
- [ ] Project initialized with `railway init`
- [ ] railway.json created with correct configuration
- [ ] Python version specified in runtime.txt
- [ ] Environment variables documented
- [ ] Local testing works with `railway run`
- [ ] Auto-sleep configured for cost optimization

**📤 Expected Outputs**:

1. Railway project URL (e.g., `la-factoria-simple.railway.app`)
2. Project dashboard link
3. Environment variables list
4. Successful health check at `/health`

**🔗 Impact on Other Tasks**:

- **DEPLOY-001**: Will use this Railway setup
- **DB-001**: Will add PostgreSQL to this project
- **API-004**: Will need Railway variables for API keys
- **MON-001**: Will use Railway's built-in metrics

**📚 Railway Resources (August 2025)**:

- Docs: <https://docs.railway.app>
- Status: <https://status.railway.app>
- Pricing: <https://railway.app/pricing>
- CLI Reference: <https://docs.railway.app/reference/cli-api>

### **SETUP-003**: Create test framework (2h)

**🎯 Objective**: Set up a robust testing framework using pytest for TDD (Test-Driven Development). Focus on practical testing patterns for FastAPI applications with clear examples.

**🧪 Testing Stack (August 2025 Best Practices)**:

- **pytest**: Core testing framework (v8.2.2)
- **pytest-asyncio**: Async test support (v0.23.7)
- **pytest-cov**: Coverage reporting (v5.0.0)
- **pytest-mock**: Mocking support (v3.14.0)
- **httpx**: Async HTTP client for API tests (v0.27.0)

**📋 Initial Setup**:

```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx

# Create test structure (if not already done)
mkdir -p tests/{unit,integration}
touch tests/__init__.py tests/conftest.py
```

**🔧 Configuration Files**:

**1. `pytest.ini`** (Pytest configuration):

```ini
[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Async support
asyncio_mode = auto

# Output options
addopts =
    -v
    --strict-markers
    --cov=app
    --cov-report=html
    --cov-report=term-missing:skip-covered
    --cov-fail-under=80

# Custom markers
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (may require external services)
    slow: Slow tests (>1s execution time)
```

**2. `tests/conftest.py`** (Shared fixtures):

```python
"""Shared test fixtures and configuration."""
import os
import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import your app
from app.main import app
from app.database import Base
from app.config import settings

# Override settings for testing
settings.DATABASE_URL = "sqlite+aiosqlite:///./test.db"
settings.TESTING = True


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio for all async tests."""
    return "asyncio"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test client for API testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    # Create test database
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def mock_openai(mocker):
    """Mock OpenAI API calls."""
    mock = mocker.patch("openai.ChatCompletion.create")
    mock.return_value = {
        "choices": [{
            "message": {
                "content": "Mocked AI response for testing"
            }
        }],
        "usage": {
            "total_tokens": 100,
            "completion_tokens": 50
        }
    }
    return mock


@pytest.fixture
def auth_headers():
    """Create authenticated request headers."""
    return {"Authorization": "Bearer test-api-key-123"}


@pytest.fixture
def sample_generation_request():
    """Sample content generation request."""
    return {
        "content_type": "study_guide",
        "topic": "Python Testing",
        "additional_context": "Focus on pytest framework"
    }
```

**📝 Test Examples**:

**1. Unit Test - Service Layer** (`tests/unit/test_services.py`):

```python
"""Unit tests for service layer."""
import pytest
from unittest.mock import Mock, AsyncMock

from app.services.ai_service import AIService
from app.services.auth_service import AuthService


class TestAIService:
    """Test AI service functionality."""

    @pytest.fixture
    def ai_service(self, mock_openai):
        """Create AI service with mocked dependencies."""
        service = AIService()
        service.client = mock_openai
        return service

    @pytest.mark.asyncio
    async def test_generate_content_success(self, ai_service, sample_generation_request):
        """Test successful content generation."""
        # Act
        result = await ai_service.generate_content(**sample_generation_request)

        # Assert
        assert result["content_type"] == "study_guide"
        assert "content" in result
        assert result["token_usage"]["total"] == 100
        assert result["estimated_cost"] > 0

    @pytest.mark.asyncio
    async def test_generate_content_retry_on_error(self, ai_service, mocker):
        """Test retry logic on API errors."""
        # Arrange
        ai_service.client.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            {"choices": [{"message": {"content": "Success after retry"}}]}
        ]

        # Act & Assert
        with pytest.raises(Exception):
            await ai_service.generate_content("study_guide", "Test Topic")

    def test_calculate_cost(self, ai_service):
        """Test cost calculation accuracy."""
        # Test cases: (input_tokens, output_tokens, expected_cost)
        test_cases = [
            (1000, 500, 0.025),  # $0.01 + $0.015
            (100, 100, 0.004),   # $0.001 + $0.003
            (0, 0, 0.0),
        ]

        for input_tokens, output_tokens, expected in test_cases:
            cost = ai_service._calculate_cost(input_tokens, output_tokens)
            assert cost == expected, f"Failed for {input_tokens}, {output_tokens}"


class TestAuthService:
    """Test authentication service."""

    def test_generate_api_key_format(self):
        """Test API key generation format."""
        service = AuthService()
        api_key = service.generate_api_key()

        assert api_key.startswith("lfs_")  # la-factoria-simple prefix
        assert len(api_key) == 36  # prefix + 32 chars
        assert api_key[4:].isalnum()  # alphanumeric after prefix

    def test_hash_api_key(self):
        """Test API key hashing."""
        service = AuthService()
        api_key = "lfs_test123"

        hashed = service.hash_api_key(api_key)
        assert hashed != api_key
        assert service.verify_api_key(api_key, hashed)
        assert not service.verify_api_key("wrong_key", hashed)
```

**2. Integration Test - API Endpoints** (`tests/integration/test_api.py`):

```python
"""Integration tests for API endpoints."""
import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test /health endpoint returns 200."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "port" in data


class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_create_api_key(self, client: AsyncClient):
        """Test API key creation."""
        response = await client.post(
            "/api/v1/auth/api-key",
            json={"name": "Test Key"}
        )

        assert response.status_code == 201
        data = response.json()
        assert "api_key" in data
        assert data["api_key"].startswith("lfs_")

    @pytest.mark.asyncio
    async def test_invalid_api_key(self, client: AsyncClient):
        """Test request with invalid API key."""
        response = await client.get(
            "/api/v1/generate",
            headers={"Authorization": "Bearer invalid_key"}
        )

        assert response.status_code == 401


class TestGenerationEndpoint:
    """Test content generation endpoint."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_content(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_generation_request: dict
    ):
        """Test content generation with valid request."""
        response = await client.post(
            "/api/v1/generate",
            json=sample_generation_request,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content_type"] == "study_guide"
        assert "content" in data
        assert "token_usage" in data
        assert "estimated_cost" in data

    @pytest.mark.asyncio
    async def test_generate_invalid_content_type(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test generation with invalid content type."""
        response = await client.post(
            "/api/v1/generate",
            json={
                "content_type": "invalid_type",
                "topic": "Test"
            },
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_generate_timeout_handling(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mocker
    ):
        """Test timeout handling for slow API calls."""
        # Mock slow API response
        mocker.patch(
            "app.services.ai_service.AIService.generate_content",
            side_effect=TimeoutError("API timeout")
        )

        response = await client.post(
            "/api/v1/generate",
            json=sample_generation_request,
            headers=auth_headers
        )

        assert response.status_code == 504  # Gateway timeout
```

**🚀 Running Tests**:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run specific test file
pytest tests/unit/test_services.py

# Run specific test
pytest tests/unit/test_services.py::TestAIService::test_generate_content_success

# Run with verbose output
pytest -vv

# Run and stop on first failure
pytest -x

# Run tests in parallel (install pytest-xdist first)
pytest -n auto
```

**📊 Coverage Reports**:

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Terminal coverage summary
pytest --cov=app --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```

**🎯 TDD Workflow**:

```bash
# 1. Write failing test first
cat > tests/unit/test_new_feature.py << 'EOF'
def test_new_feature():
    result = my_new_function()
    assert result == "expected"
EOF

# 2. Run test (should fail)
pytest tests/unit/test_new_feature.py

# 3. Implement minimal code to pass
# ... write code ...

# 4. Run test again (should pass)
pytest tests/unit/test_new_feature.py

# 5. Refactor with confidence
# ... improve code ...

# 6. Ensure tests still pass
pytest
```

**⚠️ Common Testing Pitfalls**:

1. **Not mocking external services**:

   ```python
   # Wrong: Real API call in tests
   response = openai.ChatCompletion.create(...)

   # Right: Mock external calls
   mock_openai.return_value = {"test": "response"}
   ```

2. **Testing implementation instead of behavior**:

   ```python
   # Wrong: Testing private methods
   assert service._internal_method() == "value"

   # Right: Test public interface
   assert service.generate_content(...) == expected
   ```

3. **Incomplete async cleanup**:

   ```python
   # Wrong: Forgetting to close connections
   async def test_something():
       client = AsyncClient()
       # ... test ...

   # Right: Use context managers
   async with AsyncClient() as client:
       # ... test ...
   ```

4. **Not isolating tests**:

   ```python
   # Wrong: Tests depend on each other
   def test_create():
       global user_id
       user_id = create_user()

   def test_delete():
       delete_user(user_id)  # Depends on test_create

   # Right: Each test is independent
   def test_delete():
       user_id = create_user()  # Setup
       delete_user(user_id)     # Test
   ```

**✅ Quality Gates**:

- [ ] pytest.ini configured with appropriate settings
- [ ] conftest.py with shared fixtures
- [ ] Unit tests for all services
- [ ] Integration tests for all endpoints
- [ ] 80%+ code coverage
- [ ] All tests pass locally
- [ ] Tests run in <30 seconds
- [ ] Mock all external dependencies

**📤 Expected Outputs**:

1. Working test suite with `pytest`
2. HTML coverage report in `htmlcov/`
3. Clear test structure (unit/integration)
4. Fixtures for common test data
5. Mocked external services

**🔗 Impact on Other Tasks**:

- All API tasks will include tests
- **CI/CD**: Will run these tests
- **API-001**: Will test health endpoint
- **API-002**: Will test generation endpoint
- **API-003**: Will test auth endpoints

### **API-001**: Implement health check endpoint (2h)

**🎯 Objective**: Create a simple health check endpoint that confirms the service is running. This is essential for Railway deployments and monitoring. Follow TDD approach.

**🏥 Health Check Best Practices (August 2025)**:

- Keep it simple and fast (<100ms response time)
- Include basic service information
- Return consistent structure
- Use for Railway health checks
- No authentication required

**📋 TDD Implementation Steps**:

**Step 1: Write the test first** (`tests/integration/test_health.py`):

```python
"""Test health check endpoint."""
import pytest
from httpx import AsyncClient
from app.main import app


class TestHealthEndpoint:
    """Test health check functionality."""

    @pytest.mark.asyncio
    async def test_health_endpoint_success(self):
        """Test /health returns 200 with expected data."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "service" in data
        assert data["service"] == "la-factoria-simple"

    @pytest.mark.asyncio
    async def test_health_endpoint_response_time(self):
        """Test /health responds quickly."""
        import time

        async with AsyncClient(app=app, base_url="http://test") as client:
            start = time.time()
            response = await client.get("/health")
            duration = time.time() - start

        assert response.status_code == 200
        assert duration < 0.1  # Should respond in less than 100ms

    @pytest.mark.asyncio
    async def test_health_endpoint_no_auth_required(self):
        """Test /health works without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # No auth headers
            response = await client.get("/health")

        assert response.status_code == 200
```

**Step 2: Run test (should fail)**:

```bash
pytest tests/integration/test_health.py -v
# Expected: FAILED - 404 Not Found
```

**Step 3: Implement the endpoint** (`app/api/health.py`):

```python
"""Health check endpoint."""
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

from app import __version__


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    service: str
    uptime_seconds: float | None = None


# Track startup time for uptime calculation
startup_time = datetime.utcnow()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """
    Check service health.

    Returns basic information about the service status.
    No authentication required for monitoring purposes.
    """
    current_time = datetime.utcnow()
    uptime = (current_time - startup_time).total_seconds()

    return HealthResponse(
        status="healthy",
        timestamp=current_time.isoformat(),
        version=__version__,
        service="la-factoria-simple",
        uptime_seconds=uptime
    )


@router.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirects to health."""
    return {"message": "La Factoria Simple API", "docs": "/docs"}
```

**Step 4: Register the router** (`app/main.py`):

```python
"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import health  # Import health router
from app.config import settings

app = FastAPI(
    title="La Factoria Simple",
    version=__version__,
    docs_url="/docs" if settings.SHOW_DOCS else None,
    redoc_url="/redoc" if settings.SHOW_DOCS else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
```

**Step 5: Run tests again (should pass)**:

```bash
pytest tests/integration/test_health.py -v
# Expected: PASSED
```

**🔧 Configuration** (`app/config.py`):

```python
"""Application configuration."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    SHOW_DOCS: bool = True  # Keep docs visible for small team

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.railway.app",
    ]

    # Testing
    TESTING: bool = False

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
```

**🚀 Running Locally**:

```bash
# Start the server
uvicorn app.main:app --reload --port 8000

# Test with curl
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-08-02T10:30:45.123456",
  "version": "2.0.0",
  "service": "la-factoria-simple",
  "uptime_seconds": 123.45
}
```

**🐳 Docker Health Check** (optional):

```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1
```

**🚂 Railway Configuration**:

```json
// In railway.json
{
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30
  }
}
```

**📊 Monitoring Integration**:

```python
# Extended health check with dependencies (optional)
@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(
    db: AsyncSession = Depends(get_db)
) -> DetailedHealthResponse:
    """Detailed health check including dependencies."""

    # Check database
    db_healthy = True
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_healthy = False

    # Check external services
    openai_healthy = True
    try:
        # Quick API key validation
        openai.Model.list()
    except Exception:
        openai_healthy = False

    return DetailedHealthResponse(
        status="healthy" if db_healthy and openai_healthy else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        version=__version__,
        service="la-factoria-simple",
        dependencies={
            "database": "healthy" if db_healthy else "unhealthy",
            "openai": "healthy" if openai_healthy else "unhealthy",
        }
    )
```

**⚠️ Common Pitfalls**:

1. **Slow health checks**:

   ```python
   # Wrong: Heavy operations in health check
   @router.get("/health")
   async def health():
       users = await db.fetch_all("SELECT COUNT(*) FROM users")
       return {"status": "ok", "users": users}

   # Right: Keep it simple
   @router.get("/health")
   async def health():
       return {"status": "healthy"}
   ```

2. **Authentication on health endpoint**:

   ```python
   # Wrong: Requiring auth
   @router.get("/health", dependencies=[Depends(get_current_user)])

   # Right: No auth for monitoring
   @router.get("/health")
   ```

3. **Missing error handling**:

   ```python
   # Wrong: Can crash
   uptime = (datetime.now() - startup_time).total_seconds()

   # Right: Graceful handling
   try:
       uptime = (datetime.utcnow() - startup_time).total_seconds()
   except:
       uptime = None
   ```

**✅ Quality Gates**:

- [ ] Tests written first and failing
- [ ] Endpoint returns 200 status
- [ ] Response time < 100ms
- [ ] No authentication required
- [ ] Includes version and timestamp
- [ ] Railway health check configured
- [ ] All tests passing

**📤 Expected Outputs**:

1. `/health` endpoint returning JSON
2. Passing integration tests
3. Railway health checks working
4. Fast response time (<100ms)

**🔗 Impact on Other Tasks**:

- **SETUP-002**: Railway uses this for health checks
- **DEPLOY-001**: Required for deployment
- **MON-001**: Monitoring will poll this endpoint
- **TEST-001**: First endpoint to test

### **API-002**: Create content generation endpoint structure (3h)

**🎯 Objective**: Build the core content generation endpoint structure with proper validation, error handling, and async patterns. This endpoint will be the heart of the application.

**🏗️ Architecture Overview**:

- Request validation with Pydantic models
- Service layer for business logic separation
- Proper error handling and status codes
- Async/await patterns throughout
- Ready for AI integration (API-004)

**📋 TDD Implementation Steps**:

**Step 1: Write the test first** (`tests/integration/test_generation.py`):

```python
"""Test content generation endpoints."""
import pytest
from httpx import AsyncClient
from app.main import app


class TestGenerationEndpoint:
    """Test content generation functionality."""

    @pytest.fixture
    def valid_request(self):
        """Valid generation request."""
        return {
            "content_type": "study_guide",
            "topic": "Python Programming Basics",
            "additional_context": "Focus on beginners"
        }

    @pytest.fixture
    def auth_headers(self):
        """Mock auth headers for testing."""
        return {"Authorization": "Bearer test-api-key"}

    @pytest.mark.asyncio
    async def test_generation_endpoint_structure(self, auth_headers, valid_request):
        """Test endpoint accepts proper structure."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/generate",
                json=valid_request,
                headers=auth_headers
            )

        # For now, expect 501 (not implemented) since AI not integrated
        assert response.status_code == 501
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_generation_validation_content_type(self, auth_headers):
        """Test content type validation."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/generate",
                json={
                    "content_type": "invalid_type",
                    "topic": "Test"
                },
                headers=auth_headers
            )

        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("content_type" in str(error) for error in errors)

    @pytest.mark.asyncio
    async def test_generation_validation_topic_required(self, auth_headers):
        """Test topic is required."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/generate",
                json={"content_type": "study_guide"},
                headers=auth_headers
            )

        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("topic" in str(error) for error in errors)

    @pytest.mark.asyncio
    async def test_generation_requires_auth(self, valid_request):
        """Test authentication is required."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/generate",
                json=valid_request
                # No auth headers
            )

        assert response.status_code == 401
```

**Step 2: Create request/response models** (`app/models/generation.py`):

```python
"""Generation request and response models."""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator


# Supported content types
ContentType = Literal[
    "study_guide",
    "flashcards",
    "podcast_script",
    "one_pager",
    "detailed_reading",
    "faq",
    "reading_questions",
    "master_outline"
]


class GenerationRequest(BaseModel):
    """Content generation request model."""

    content_type: ContentType = Field(
        ...,
        description="Type of content to generate"
    )

    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Topic for content generation"
    )

    additional_context: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional context or requirements"
    )

    language: str = Field(
        default="en",
        pattern="^[a-z]{2}$",
        description="Language code (ISO 639-1)"
    )

    @validator("topic")
    def clean_topic(cls, v):
        """Clean and validate topic."""
        # Remove excessive whitespace
        cleaned = " ".join(v.split())
        if len(cleaned) < 3:
            raise ValueError("Topic too short after cleaning")
        return cleaned

    class Config:
        schema_extra = {
            "example": {
                "content_type": "study_guide",
                "topic": "Introduction to Machine Learning",
                "additional_context": "For undergraduate students",
                "language": "en"
            }
        }


class GenerationResponse(BaseModel):
    """Content generation response model."""

    id: str = Field(..., description="Unique generation ID")
    content: str = Field(..., description="Generated content")
    content_type: ContentType
    topic: str

    created_at: datetime
    processing_time_ms: int

    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata (tokens, cost, etc)"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "gen_abc123",
                "content": "# Study Guide: Introduction to Machine Learning\n\n...",
                "content_type": "study_guide",
                "topic": "Introduction to Machine Learning",
                "created_at": "2025-08-02T10:30:45.123456",
                "processing_time_ms": 2500,
                "metadata": {
                    "token_count": 1500,
                    "estimated_cost": 0.045,
                    "model": "gpt-4-turbo"
                }
            }
        }


class GenerationError(BaseModel):
    """Error response for generation failures."""

    error_code: str
    message: str
    details: Optional[dict] = None

    class Config:
        schema_extra = {
            "example": {
                "error_code": "GENERATION_FAILED",
                "message": "Failed to generate content",
                "details": {"reason": "API rate limit exceeded"}
            }
        }
```

**Step 3: Create the service layer** (`app/services/generation_service.py`):

```python
"""Content generation service."""
import time
import uuid
from datetime import datetime
from typing import Optional

from app.models.generation import (
    GenerationRequest,
    GenerationResponse,
    ContentType
)


class GenerationService:
    """Handle content generation logic."""

    def __init__(self):
        """Initialize generation service."""
        # Will be enhanced in API-004 with AI integration
        self.ai_service = None

    async def generate_content(
        self,
        request: GenerationRequest,
        user_id: Optional[str] = None
    ) -> GenerationResponse:
        """
        Generate content based on request.

        This is a placeholder that will be enhanced in API-004.
        """
        start_time = time.time()

        # Generate unique ID
        generation_id = f"gen_{uuid.uuid4().hex[:12]}"

        # Placeholder content until AI integration
        content = self._generate_placeholder_content(
            request.content_type,
            request.topic,
            request.additional_context
        )

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        return GenerationResponse(
            id=generation_id,
            content=content,
            content_type=request.content_type,
            topic=request.topic,
            created_at=datetime.utcnow(),
            processing_time_ms=processing_time_ms,
            metadata={
                "placeholder": True,
                "user_id": user_id,
                "language": request.language
            }
        )

    def _generate_placeholder_content(
        self,
        content_type: ContentType,
        topic: str,
        context: Optional[str]
    ) -> str:
        """Generate placeholder content for testing."""
        templates = {
            "study_guide": f"""# Study Guide: {topic}

## Overview
This is a placeholder study guide for {topic}.
{f'Context: {context}' if context else ''}

## Key Concepts
1. Concept 1
2. Concept 2
3. Concept 3

## Summary
This will be replaced with AI-generated content in API-004.
""",
            "flashcards": f"""# Flashcards: {topic}

Card 1:
Q: What is {topic}?
A: [Placeholder answer]

Card 2:
Q: Why is {topic} important?
A: [Placeholder answer]

Note: This will be replaced with AI-generated content in API-004.
""",
            # Add other content types...
        }

        return templates.get(
            content_type,
            f"Placeholder content for {content_type} about {topic}"
        )


# Singleton instance
generation_service = GenerationService()
```

**Step 4: Create the API endpoint** (`app/api/generation.py`):

```python
"""Content generation API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.generation import (
    GenerationRequest,
    GenerationResponse,
    GenerationError
)
from app.services.generation_service import generation_service
from app.api.auth import get_current_user


router = APIRouter()


@router.post(
    "/generate",
    response_model=GenerationResponse,
    responses={
        400: {"model": GenerationError},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation Error"},
        500: {"model": GenerationError}
    },
    tags=["generation"]
)
async def generate_content(
    request: GenerationRequest,
    current_user: dict = Depends(get_current_user)
) -> GenerationResponse:
    """
    Generate educational content.

    Supports multiple content types:
    - study_guide: Comprehensive study guides
    - flashcards: Q&A format flashcards
    - podcast_script: Podcast episode scripts
    - And more...

    Requires authentication via API key.
    """
    try:
        # For now, return 501 until AI is integrated
        if not hasattr(generation_service, 'ai_service') or generation_service.ai_service is None:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="AI service not yet integrated. See API-004."
            )

        # Generate content
        response = await generation_service.generate_content(
            request,
            user_id=current_user.get("id")
        )

        return response

    except HTTPException:
        raise
    except ValueError as e:
        # Handle validation errors
        return JSONResponse(
            status_code=400,
            content=GenerationError(
                error_code="INVALID_REQUEST",
                message=str(e)
            ).dict()
        )
    except Exception as e:
        # Handle unexpected errors
        return JSONResponse(
            status_code=500,
            content=GenerationError(
                error_code="GENERATION_FAILED",
                message="An unexpected error occurred",
                details={"error": str(e)} if current_user.get("is_admin") else None
            ).dict()
        )


@router.get("/content-types", tags=["generation"])
async def get_content_types():
    """Get list of supported content types."""
    return {
        "content_types": [
            {
                "id": "study_guide",
                "name": "Study Guide",
                "description": "Comprehensive study guide with key concepts"
            },
            {
                "id": "flashcards",
                "name": "Flashcards",
                "description": "Q&A format for memorization"
            },
            {
                "id": "podcast_script",
                "name": "Podcast Script",
                "description": "Conversational script for audio content"
            },
            # Add all content types...
        ]
    }
```

**Step 5: Update main.py**:

```python
# In app/main.py, add:
from app.api import generation

# After health router
app.include_router(
    generation.router,
    prefix="/api/v1",
    tags=["generation"]
)
```

**Step 6: Create placeholder auth** (`app/api/auth.py`):

```python
"""Placeholder authentication for testing."""
from fastapi import Header, HTTPException, status


async def get_current_user(
    authorization: str = Header(None)
) -> dict:
    """
    Placeholder auth check.
    Will be properly implemented in API-003.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication"
        )

    # For now, return a mock user
    return {
        "id": "user_123",
        "api_key": authorization.split(" ")[1],
        "is_admin": False
    }
```

**🧪 Testing the Structure**:

```bash
# Run the tests
pytest tests/integration/test_generation.py -v

# Test manually with curl
# Should return 401 (no auth)
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"content_type": "study_guide", "topic": "Python"}'

# Should return 501 (not implemented)
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-key" \
  -d '{"content_type": "study_guide", "topic": "Python"}'

# Test content types endpoint
curl http://localhost:8000/api/v1/content-types
```

**📝 OpenAPI Documentation**:

The endpoint will automatically appear in `/docs` with:

- Request/response schemas
- Validation rules
- Example payloads
- Authentication requirements

**⚠️ Common Pitfalls**:

1. **Synchronous code in async endpoint**:

   ```python
   # Wrong: Blocking call
   @router.post("/generate")
   async def generate():
       time.sleep(1)  # Blocks event loop!

   # Right: Use async
   @router.post("/generate")
   async def generate():
       await asyncio.sleep(1)
   ```

2. **Poor error messages**:

   ```python
   # Wrong: Generic error
   raise HTTPException(400, "Bad request")

   # Right: Specific error
   raise HTTPException(400, "Topic must be 3-500 characters")
   ```

3. **Missing validation**:

   ```python
   # Wrong: Trust input
   content = generate_for_type(request["content_type"])

   # Right: Use Pydantic
   content = generate_for_type(request.content_type)  # Validated!
   ```

**✅ Quality Gates**:

- [ ] Tests written and passing
- [ ] Pydantic models with validation
- [ ] Proper error handling
- [ ] Async patterns used correctly
- [ ] OpenAPI docs generated
- [ ] Ready for AI integration
- [ ] Placeholder responses working

**📤 Expected Outputs**:

1. `/api/v1/generate` endpoint structure
2. `/api/v1/content-types` listing endpoint
3. Proper validation and error responses
4. OpenAPI documentation
5. Ready for AI service integration

**🔗 Impact on Other Tasks**:

- **API-003**: Provides auth dependency
- **API-004**: Will integrate AI service here
- **FRONT-002**: Will call this endpoint
- **DB-003**: May store generation history

### **API-003**: Implement simple authentication (3h)

[To be enhanced next...]

### **API-004**: Add AI provider integration (4h)

**🎯 Objective**: Integrate OpenAI/Anthropic for content generation with Langfuse observability. Focus on reliability, cost tracking, and simple prompt management for 1-10 users.

**🤖 AI Provider Selection (August 2025 Context)**:

```python
# Provider comparison for educational content generation
"""
1. OpenAI GPT-4-turbo (Recommended for start)
   - Cost: ~$0.01/1K input, $0.03/1K output tokens
   - Best for: General content, study guides
   - Latency: 2-5 seconds

2. Anthropic Claude-3-Sonnet
   - Cost: ~$0.003/1K input, $0.015/1K output tokens
   - Best for: Long-form content, detailed explanations
   - Latency: 3-7 seconds

3. Start with ONE provider, add others later
"""
```

**🔍 Langfuse Integration (Observability)**:

```bash
# Install Langfuse Python SDK (Aug 2025 version)
pip install langfuse==2.38.2

# Set environment variables in Railway
railway variables set LANGFUSE_PUBLIC_KEY=pk-lf-...
railway variables set LANGFUSE_SECRET_KEY=sk-lf-...
railway variables set LANGFUSE_HOST=https://cloud.langfuse.com  # or self-hosted
```

**📦 Dependencies Setup**:

```txt
# requirements.txt additions
openai==1.35.10          # OpenAI Python SDK
anthropic==0.28.1        # Anthropic SDK (if needed)
langfuse==2.38.2         # Observability
pydantic==2.7.4          # For response models
tenacity==8.4.2          # For retries
tiktoken==0.7.0          # Token counting
```

**🏗️ AI Service Implementation**:

```python
# app/services/ai_service.py
import os
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from langfuse import Langfuse
from langfuse.openai import openai as langfuse_openai
from tenacity import retry, stop_after_attempt, wait_exponential
import tiktoken

class AIService:
    def __init__(self):
        # Initialize OpenAI with Langfuse wrapper
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        # Initialize Langfuse
        self.langfuse = Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )

        # Patch OpenAI for automatic tracing
        langfuse_openai.register(self.langfuse)

        # Token counter for cost estimation
        self.encoder = tiktoken.encoding_for_model("gpt-4-turbo-preview")

        # Model configuration
        self.model = "gpt-4-turbo-preview"  # Latest as of Aug 2025
        self.max_tokens = 4000
        self.temperature = 0.7

    def count_tokens(self, text: str) -> int:
        """Count tokens for cost estimation"""
        return len(self.encoder.encode(text))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_content(
        self,
        content_type: str,
        topic: str,
        additional_context: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """Generate content with retry logic and observability"""

        # Create Langfuse trace
        trace = self.langfuse.trace(
            name=f"generate_{content_type}",
            user_id=user_id,
            metadata={
                "content_type": content_type,
                "topic": topic,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        try:
            # Get prompt from templates
            prompt = self._get_prompt(content_type, topic, additional_context)

            # Count input tokens for cost tracking
            input_tokens = self.count_tokens(prompt)

            # Create generation span
            generation = trace.span(
                name="openai_generation",
                input={"prompt": prompt, "model": self.model}
            )

            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract content
            content = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens

            # Update generation span
            generation.update(
                output={"content": content},
                usage={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "estimated_cost": self._calculate_cost(input_tokens, output_tokens)
                }
            )

            # Log success
            trace.update(status="SUCCESS")

            return {
                "content": content,
                "content_type": content_type,
                "model_used": self.model,
                "token_usage": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens
                },
                "estimated_cost": self._calculate_cost(input_tokens, output_tokens),
                "trace_id": trace.id
            }

        except Exception as e:
            # Log error to Langfuse
            trace.update(status="ERROR", status_message=str(e))
            raise

    def _get_prompt(self, content_type: str, topic: str, context: Optional[str]) -> str:
        """Get prompt template for content type"""
        # Load from extracted prompts (from previous migration)
        prompts = {
            "study_guide": f"""Create a comprehensive study guide about {topic}.
Include:
1. Overview (2-3 paragraphs)
2. Key concepts (5-7 main points)
3. Important details for each concept
4. Summary of main takeaways
{f'Additional context: {context}' if context else ''}""",

            "flashcards": f"""Create 10 educational flashcards about {topic}.
Format each as:
Q: [Question]
A: [Answer]

Make questions specific and answers concise but complete.
{f'Additional context: {context}' if context else ''}""",

            # Add other content types from extracted prompts
        }

        return prompts.get(content_type, prompts["study_guide"])

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost in USD"""
        # GPT-4-turbo pricing as of Aug 2025
        input_cost = (input_tokens / 1000) * 0.01
        output_cost = (output_tokens / 1000) * 0.03
        return round(input_cost + output_cost, 4)

# Singleton instance
ai_service = AIService()
```

**🔌 FastAPI Endpoint Integration**:

```python
# app/api/generate.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from app.services.ai_service import ai_service
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1")

class GenerateRequest(BaseModel):
    content_type: str = Field(..., pattern="^(study_guide|flashcards|podcast_script)$")
    topic: str = Field(..., min_length=3, max_length=200)
    additional_context: Optional[str] = Field(None, max_length=1000)

class GenerateResponse(BaseModel):
    content: str
    content_type: str
    token_usage: dict
    estimated_cost: float
    trace_url: Optional[str] = None

@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate educational content with AI"""
    try:
        result = await ai_service.generate_content(
            content_type=request.content_type,
            topic=request.topic,
            additional_context=request.additional_context,
            user_id=current_user.get("id")
        )

        # Add Langfuse trace URL if available
        result["trace_url"] = f"https://cloud.langfuse.com/trace/{result['trace_id']}"

        return GenerateResponse(**result)

    except Exception as e:
        # Log to Langfuse dashboard
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
```

**🧪 Testing AI Integration**:

```python
# tests/test_ai_service.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.ai_service import AIService

@pytest.fixture
def ai_service():
    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'LANGFUSE_PUBLIC_KEY': 'test-pk',
        'LANGFUSE_SECRET_KEY': 'test-sk'
    }):
        return AIService()

@pytest.mark.asyncio
async def test_generate_content_success(ai_service):
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test study guide content"
    mock_response.usage.completion_tokens = 500

    with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
        result = await ai_service.generate_content(
            content_type="study_guide",
            topic="Python basics"
        )

        assert result["content"] == "Test study guide content"
        assert result["content_type"] == "study_guide"
        assert "estimated_cost" in result
        assert result["estimated_cost"] > 0

# Add more tests for error cases, retries, etc.
```

**💰 Cost Management & Monitoring**:

```python
# Add to your Railway variables
railway variables set DAILY_TOKEN_LIMIT=100000  # ~$3/day
railway variables set ALERT_EMAIL=admin@example.com

# app/services/cost_monitor.py
class CostMonitor:
    async def check_daily_usage(self):
        """Check daily token usage via Langfuse API"""
        # Query Langfuse for today's usage
        today = datetime.utcnow().date()
        usage = self.langfuse.get_usage(
            start_date=today,
            end_date=today + timedelta(days=1)
        )

        if usage.total_tokens > int(os.environ.get("DAILY_TOKEN_LIMIT", 100000)):
            # Send alert or disable service
            await self.send_alert(f"Daily limit exceeded: {usage.total_tokens} tokens")
```

**🚨 Common Pitfalls & Solutions**:

1. **API Key Exposure**:

   ```python
   # WRONG: Hardcoded key
   client = OpenAI(api_key="sk-proj-...")

   # RIGHT: Environment variable
   client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
   ```

2. **No Retry Logic**:

   ```python
   # Add tenacity for automatic retries
   @retry(stop=stop_after_attempt(3))
   async def generate_with_retry():
       # API calls here
   ```

3. **Missing Cost Tracking**:

   ```python
   # Always log token usage
   langfuse.trace(usage={"tokens": count, "cost": estimate})
   ```

4. **Blocking Calls**:

   ```python
   # Use async for better performance
   async def generate_content():  # Not def generate_content()
   ```

**📊 Langfuse Dashboard Setup**:

1. Sign up at <https://cloud.langfuse.com>
2. Create new project: "la-factoria-simple"
3. Get API keys from settings
4. Set up alerts:
   - Daily spend > $5
   - Error rate > 5%
   - P95 latency > 10s

**✅ Quality Gates**:

- [ ] OpenAI API key set in Railway variables
- [ ] Langfuse keys configured
- [ ] Token counting implemented
- [ ] Cost calculation accurate
- [ ] Retry logic in place
- [ ] Error handling comprehensive
- [ ] Tests pass with mocked API calls
- [ ] Langfuse dashboard shows traces

**📤 Expected Outputs**:

1. Working `/generate` endpoint
2. Langfuse traces for all API calls
3. Cost tracking in responses
4. Clear error messages on failures

**🔗 Impact on Other Tasks**:

- **FRONT-002**: Will call this endpoint
- **DB-003**: May store generation history
- **MON-001**: Monitor via Langfuse dashboard
- **TEST-001**: Include AI service tests

## Enhancement Progress Tracking

- [x] DISCOVER-001: Fully enhanced with anti-hallucination context
- [x] DISCOVER-002: Fully enhanced with anti-hallucination context
- [x] DISCOVER-003: Fully enhanced with anti-hallucination context
- [x] SETUP-001: Fully enhanced with repository structure details
- [x] SETUP-002: Fully enhanced with Railway-specific context
- [x] SETUP-003: Fully enhanced with pytest testing framework
- [x] API-001: Fully enhanced with health check implementation
- [x] API-002: Fully enhanced with content generation endpoint structure
- [ ] API-003: Pending enhancement
- [x] API-004: Fully enhanced with AI provider and Langfuse integration
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
