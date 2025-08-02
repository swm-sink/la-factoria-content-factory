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

**🎯 Objective**: Create a simple, secure API key authentication system suitable for 1-10 users. Focus on simplicity while maintaining security best practices.

**🔐 Authentication Strategy**:

- API key based (no OAuth complexity needed for 1-10 users)
- Keys stored hashed in database (or in-memory for MVP)
- Bearer token format for consistency
- Rate limiting per key
- Key generation and management endpoints

**📋 TDD Implementation Steps**:

**Step 1: Write authentication tests** (`tests/unit/test_auth_service.py`):

```python
"""Test authentication service."""
import pytest
from app.services.auth_service import AuthService


class TestAuthService:
    """Test authentication functionality."""

    @pytest.fixture
    def auth_service(self):
        """Create auth service instance."""
        return AuthService()

    def test_generate_api_key_format(self, auth_service):
        """Test API key generation has correct format."""
        key = auth_service.generate_api_key()

        # Should start with prefix
        assert key.startswith("lfs_")
        # Should be 36 chars total (4 prefix + 32 random)
        assert len(key) == 36
        # Should be alphanumeric after prefix
        assert key[4:].replace("-", "").isalnum()

    def test_generate_unique_keys(self, auth_service):
        """Test that generated keys are unique."""
        keys = [auth_service.generate_api_key() for _ in range(100)]
        assert len(set(keys)) == 100  # All unique

    def test_hash_and_verify_api_key(self, auth_service):
        """Test API key hashing and verification."""
        key = "lfs_test123"
        hashed = auth_service.hash_api_key(key)

        # Hash should be different from original
        assert hashed != key
        # Should verify correctly
        assert auth_service.verify_api_key(key, hashed) is True
        # Wrong key should not verify
        assert auth_service.verify_api_key("wrong_key", hashed) is False

    def test_extract_api_key_from_header(self, auth_service):
        """Test extracting API key from auth header."""
        # Valid header
        header = "Bearer lfs_abc123"
        key = auth_service.extract_api_key(header)
        assert key == "lfs_abc123"

        # Invalid headers
        assert auth_service.extract_api_key("") is None
        assert auth_service.extract_api_key("Bearer") is None
        assert auth_service.extract_api_key("Basic abc123") is None
```

**Step 2: Create auth models** (`app/models/auth.py`):

```python
"""Authentication models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class APIKey(BaseModel):
    """API Key model."""
    id: str
    name: str
    key_hash: str
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True

    # Rate limiting
    requests_per_minute: int = 60
    requests_per_day: int = 1000

    class Config:
        # Don't expose the hash
        fields = {"key_hash": {"exclude": True}}


class CreateAPIKeyRequest(BaseModel):
    """Request to create new API key."""
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Descriptive name for the API key"
    )


class CreateAPIKeyResponse(BaseModel):
    """Response with new API key."""
    api_key: str = Field(
        ...,
        description="The API key (only shown once)"
    )
    key_id: str
    name: str
    created_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "api_key": "lfs_abc123def456...",
                "key_id": "key_123",
                "name": "My App Key",
                "created_at": "2025-08-02T10:30:45.123456"
            }
        }


class APIKeyInfo(BaseModel):
    """Public API key information."""
    id: str
    name: str
    created_at: datetime
    last_used: Optional[datetime]
    is_active: bool
```

**Step 3: Implement auth service** (`app/services/auth_service.py`):

```python
"""Authentication service."""
import secrets
import hashlib
from datetime import datetime
from typing import Optional, Dict, List
from passlib.context import CryptContext


class AuthService:
    """Handle authentication logic."""

    def __init__(self):
        """Initialize auth service."""
        # Password hashing context
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )

        # In-memory storage for MVP (replace with DB in production)
        self.api_keys: Dict[str, dict] = {}

        # Create default admin key for initial setup
        self._create_default_admin_key()

    def _create_default_admin_key(self):
        """Create default admin API key for initial access."""
        admin_key = "lfs_admin_default_key_change_this"
        self.api_keys["admin"] = {
            "id": "admin",
            "name": "Default Admin Key",
            "key_hash": self.hash_api_key(admin_key),
            "created_at": datetime.utcnow(),
            "is_active": True,
            "is_admin": True
        }
        print(f"⚠️  Default admin API key: {admin_key}")
        print("⚠️  Change this immediately in production!")

    def generate_api_key(self) -> str:
        """Generate a new API key."""
        # Generate 32 random bytes (256 bits)
        random_bytes = secrets.token_urlsafe(24)  # 24 bytes = 32 chars base64
        # Add prefix for easy identification
        return f"lfs_{random_bytes}"

    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage."""
        return self.pwd_context.hash(api_key)

    def verify_api_key(self, api_key: str, hashed: str) -> bool:
        """Verify an API key against its hash."""
        try:
            return self.pwd_context.verify(api_key, hashed)
        except Exception:
            return False

    def extract_api_key(self, auth_header: Optional[str]) -> Optional[str]:
        """Extract API key from Authorization header."""
        if not auth_header:
            return None

        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    def create_api_key(self, name: str) -> tuple[str, str]:
        """
        Create a new API key.

        Returns: (key_id, api_key)
        """
        # Generate key
        api_key = self.generate_api_key()
        key_id = f"key_{secrets.token_hex(6)}"

        # Store hashed
        self.api_keys[key_id] = {
            "id": key_id,
            "name": name,
            "key_hash": self.hash_api_key(api_key),
            "created_at": datetime.utcnow(),
            "last_used": None,
            "is_active": True,
            "is_admin": False,
            "requests_per_minute": 60,
            "requests_per_day": 1000
        }

        return key_id, api_key

    def validate_api_key(self, api_key: str) -> Optional[dict]:
        """
        Validate an API key and return user info.

        Returns user dict if valid, None otherwise.
        """
        # Check all stored keys
        for key_id, key_data in self.api_keys.items():
            if not key_data["is_active"]:
                continue

            if self.verify_api_key(api_key, key_data["key_hash"]):
                # Update last used
                key_data["last_used"] = datetime.utcnow()

                # Return user info (don't include hash)
                return {
                    "id": key_id,
                    "name": key_data["name"],
                    "is_admin": key_data.get("is_admin", False),
                    "api_key_id": key_id
                }

        return None

    def list_api_keys(self) -> List[dict]:
        """List all API keys (without hashes)."""
        keys = []
        for key_data in self.api_keys.values():
            keys.append({
                "id": key_data["id"],
                "name": key_data["name"],
                "created_at": key_data["created_at"],
                "last_used": key_data["last_used"],
                "is_active": key_data["is_active"]
            })
        return keys

    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key."""
        if key_id in self.api_keys:
            self.api_keys[key_id]["is_active"] = False
            return True
        return False


# Singleton instance
auth_service = AuthService()
```

**Step 4: Create auth dependency** (`app/api/auth.py`):

```python
"""Authentication dependencies and endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Header, status
from typing import Optional

from app.models.auth import (
    CreateAPIKeyRequest,
    CreateAPIKeyResponse,
    APIKeyInfo
)
from app.services.auth_service import auth_service


router = APIRouter()


async def get_api_key(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """Extract API key from Authorization header."""
    if not authorization:
        return None
    return auth_service.extract_api_key(authorization)


async def get_current_user(
    api_key: Optional[str] = Depends(get_api_key)
) -> dict:
    """
    Validate API key and return current user.

    Raises 401 if invalid.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.validate_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Require admin privileges."""
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# API Key Management Endpoints

@router.post(
    "/keys",
    response_model=CreateAPIKeyResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_api_key(
    request: CreateAPIKeyRequest,
    current_user: dict = Depends(require_admin)
) -> CreateAPIKeyResponse:
    """
    Create a new API key.

    Requires admin privileges.
    The API key is only shown once in the response.
    """
    key_id, api_key = auth_service.create_api_key(request.name)

    return CreateAPIKeyResponse(
        api_key=api_key,
        key_id=key_id,
        name=request.name,
        created_at=datetime.utcnow()
    )


@router.get("/keys", response_model=List[APIKeyInfo])
async def list_api_keys(
    current_user: dict = Depends(require_admin)
) -> List[APIKeyInfo]:
    """
    List all API keys.

    Requires admin privileges.
    """
    keys = auth_service.list_api_keys()
    return [APIKeyInfo(**key) for key in keys]


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(require_admin)
):
    """
    Revoke an API key.

    Requires admin privileges.
    """
    if key_id == current_user["api_key_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke your own key"
        )

    if not auth_service.revoke_api_key(key_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    return {"message": "API key revoked"}


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current authenticated user info."""
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "is_admin": current_user.get("is_admin", False)
    }
```

**Step 5: Update main.py**:

```python
# In app/main.py, add auth router:
from app.api import auth

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["authentication"]
)
```

**🔒 Security Best Practices**:

```python
# Rate limiting example (app/middleware/rate_limit.py)
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
import asyncio

class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """Check if request is within rate limit."""
        async with self.lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window_seconds)

            # Clean old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]

            # Check limit
            if len(self.requests[key]) >= max_requests:
                return False

            # Add current request
            self.requests[key].append(now)
            return True

rate_limiter = RateLimiter()

# Use in dependency
async def rate_limit_check(
    current_user: dict = Depends(get_current_user)
):
    """Check rate limits for current user."""
    key_id = current_user["api_key_id"]

    # Check per-minute limit
    if not await rate_limiter.check_rate_limit(key_id, 60, 60):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded (60 requests per minute)"
        )
```

**🧪 Testing Authentication**:

```bash
# Test with default admin key
export ADMIN_KEY="lfs_admin_default_key_change_this"

# Create new API key
curl -X POST http://localhost:8000/api/v1/auth/keys \
  -H "Authorization: Bearer $ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test App"}'

# Response:
# {
#   "api_key": "lfs_abc123...",
#   "key_id": "key_xyz",
#   "name": "Test App",
#   "created_at": "2025-08-02T..."
# }

# Use the new key
export API_KEY="lfs_abc123..."

# Test authentication
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $API_KEY"

# Test protected endpoint
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content_type": "study_guide", "topic": "Python"}'
```

**💾 Persistent Storage** (for production):

```python
# Migration to database storage (app/services/auth_service_db.py)
from sqlalchemy import select
from app.database import get_db
from app.models.database import APIKey as DBAPIKey

class AuthServiceDB(AuthService):
    """Database-backed auth service."""

    async def create_api_key(self, name: str, db_session) -> tuple[str, str]:
        """Create API key in database."""
        api_key = self.generate_api_key()

        db_key = DBAPIKey(
            name=name,
            key_hash=self.hash_api_key(api_key),
            created_at=datetime.utcnow(),
            is_active=True
        )

        db_session.add(db_key)
        await db_session.commit()

        return str(db_key.id), api_key

    async def validate_api_key(self, api_key: str, db_session) -> Optional[dict]:
        """Validate against database."""
        stmt = select(DBAPIKey).where(DBAPIKey.is_active == True)
        result = await db_session.execute(stmt)

        for db_key in result.scalars():
            if self.verify_api_key(api_key, db_key.key_hash):
                # Update last used
                db_key.last_used = datetime.utcnow()
                await db_session.commit()

                return {
                    "id": str(db_key.id),
                    "name": db_key.name,
                    "is_admin": db_key.is_admin
                }

        return None
```

**⚠️ Common Pitfalls**:

1. **Storing plain text keys**:

   ```python
   # Wrong: Store plain key
   self.api_keys[id] = {"key": api_key}

   # Right: Store hash only
   self.api_keys[id] = {"key_hash": self.hash_api_key(api_key)}
   ```

2. **Weak key generation**:

   ```python
   # Wrong: Predictable
   key = f"key_{user_id}_{timestamp}"

   # Right: Cryptographically secure
   key = secrets.token_urlsafe(32)
   ```

3. **No rate limiting**:

   ```python
   # Wrong: Unlimited requests
   @app.post("/api/endpoint")
   async def endpoint():
       return data

   # Right: Rate limited
   @app.post("/api/endpoint", dependencies=[Depends(rate_limit_check)])
   ```

**✅ Quality Gates**:

- [ ] API keys are hashed before storage
- [ ] Bearer token format used
- [ ] Admin endpoints protected
- [ ] Rate limiting implemented
- [ ] Keys can be created/revoked
- [ ] Default admin key documented
- [ ] Tests cover all auth paths

**📤 Expected Outputs**:

1. Working authentication system
2. API key management endpoints
3. Secure key storage (hashed)
4. Rate limiting per key
5. Admin vs regular user roles

**🔗 Impact on Other Tasks**:

- **API-002**: Uses auth dependency
- **DB-002**: Will store keys in database
- **FRONT-002**: Needs to handle API keys
- **DOC-001**: Document key management

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

---

### FRONT-001: Create Basic HTML Structure

**⏱️ Estimated Time**: 2 hours  
**📋 Prerequisites**: API-001, API-002, API-003 completed

**🎯 Task Objective**: Create a minimal, functional HTML interface that works without JavaScript frameworks, optimized for simplicity and Railway deployment.

**🔧 Tool Selection (August 2025)**:

1. **Pure HTML + Tailwind CSS** (RECOMMENDED)
   - Version: Tailwind CSS v3.4.0 via CDN
   - Why: Zero build step, instant deployment
   - CDN: <https://cdn.tailwindcss.com>

2. **Alpine.js for Interactivity** (For FRONT-002)
   - Version: Alpine.js v3.13.5 via CDN
   - Why: No build step, works with HTML
   - CDN: <https://cdn.jsdelivr.net/npm/alpinejs@3.13.5/dist/cdn.min.js>

**📁 File Structure**:

```
frontend/
├── index.html          # Main application page
├── static/
│   ├── style.css      # Custom styles (if needed)
│   └── favicon.ico    # Browser icon
└── templates/         # For server-side rendering (optional)
    └── base.html
```

**💻 Complete Implementation**:

**Step 1: Create Basic HTML Structure**

Create `frontend/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>La Factoria - Educational Content Generator</title>

    <!-- Tailwind CSS via CDN (August 2025 version) -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Meta tags for SEO -->
    <meta name="description" content="Generate educational content with AI">
    <meta name="keywords" content="education, AI, content generation">

    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">

    <!-- Custom configuration for Tailwind -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#3B82F6',    // Blue-500
                        secondary: '#10B981',  // Green-500
                        danger: '#EF4444'      // Red-500
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Navigation Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <h1 class="text-2xl font-bold text-gray-900">La Factoria</h1>
                <div class="flex items-center space-x-4">
                    <span class="text-sm text-gray-500">API Status: <span id="api-status" class="font-medium">Checking...</span></span>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Content Type Selection -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 class="text-xl font-semibold mb-4">Select Content Type</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button class="content-type-btn p-4 bg-gray-50 rounded-lg hover:bg-primary hover:text-white transition-colors" data-type="study_guide">
                    <svg class="w-8 h-8 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                        <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 1 1 0 000 2H6a2 2 0 00-2 2v6a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-1a1 1 0 100-2h1a4 4 0 014 4v6a4 4 0 01-4 4H6a4 4 0 01-4-4V7a4 4 0 014-4z" clip-rule="evenodd"/>
                    </svg>
                    Study Guide
                </button>

                <button class="content-type-btn p-4 bg-gray-50 rounded-lg hover:bg-primary hover:text-white transition-colors" data-type="flashcards">
                    <svg class="w-8 h-8 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1z"/>
                        <path d="M2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z"/>
                    </svg>
                    Flashcards
                </button>

                <button class="content-type-btn p-4 bg-gray-50 rounded-lg hover:bg-primary hover:text-white transition-colors" data-type="quiz">
                    <svg class="w-8 h-8 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm9 0a1 1 0 011 1v1h1a1 1 0 110 2h-1v1a1 1 0 11-2 0V6h-1a1 1 0 110-2h1V3a1 1 0 011-1zM5 11a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zm9 0a1 1 0 011 1v1h1a1 1 0 110 2h-1v1a1 1 0 11-2 0v-1h-1a1 1 0 110-2h1v-1a1 1 0 011-1z" clip-rule="evenodd"/>
                    </svg>
                    Quiz
                </button>

                <button class="content-type-btn p-4 bg-gray-50 rounded-lg hover:bg-primary hover:text-white transition-colors" data-type="summary">
                    <svg class="w-8 h-8 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 0h8v12H6V4z" clip-rule="evenodd"/>
                    </svg>
                    Summary
                </button>
            </div>
        </div>

        <!-- Input Form (Hidden by default) -->
        <div id="input-form" class="bg-white rounded-lg shadow-md p-6 mb-6 hidden">
            <h2 class="text-xl font-semibold mb-4">Generate <span id="content-type-display"></span></h2>

            <form id="generation-form" class="space-y-4">
                <!-- Topic Input -->
                <div>
                    <label for="topic" class="block text-sm font-medium text-gray-700 mb-1">
                        Topic or Content
                    </label>
                    <textarea
                        id="topic"
                        name="topic"
                        rows="4"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                        placeholder="Enter the topic or paste content you want to generate educational materials from..."
                        required
                    ></textarea>
                </div>

                <!-- Audience Level -->
                <div>
                    <label for="audience" class="block text-sm font-medium text-gray-700 mb-1">
                        Audience Level
                    </label>
                    <select
                        id="audience"
                        name="audience"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                        required
                    >
                        <option value="">Select audience level...</option>
                        <option value="elementary">Elementary School</option>
                        <option value="middle-school">Middle School</option>
                        <option value="high-school">High School</option>
                        <option value="university">University</option>
                    </select>
                </div>

                <!-- API Key -->
                <div>
                    <label for="api-key" class="block text-sm font-medium text-gray-700 mb-1">
                        API Key
                    </label>
                    <input
                        type="password"
                        id="api-key"
                        name="api_key"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                        placeholder="Enter your API key..."
                        required
                    >
                    <p class="mt-1 text-xs text-gray-500">Your API key is never stored and is only used for this request.</p>
                </div>

                <!-- Submit Buttons -->
                <div class="flex gap-4">
                    <button
                        type="submit"
                        class="flex-1 bg-primary text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Generate Content
                    </button>
                    <button
                        type="button"
                        id="cancel-btn"
                        class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>

        <!-- Loading State -->
        <div id="loading-state" class="hidden">
            <div class="bg-white rounded-lg shadow-md p-8 text-center">
                <div class="inline-flex items-center">
                    <svg class="animate-spin h-8 w-8 text-primary mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span class="text-lg">Generating content...</span>
                </div>
                <p class="mt-4 text-sm text-gray-500">This usually takes 10-30 seconds</p>
            </div>
        </div>

        <!-- Results Display -->
        <div id="results" class="hidden">
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex justify-between items-start mb-4">
                    <h2 class="text-xl font-semibold">Generated Content</h2>
                    <button
                        id="new-generation-btn"
                        class="text-sm bg-secondary text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors"
                    >
                        New Generation
                    </button>
                </div>

                <!-- Content Display Area -->
                <div id="content-display" class="prose max-w-none">
                    <!-- Generated content will be inserted here -->
                </div>

                <!-- Metadata Footer -->
                <div class="mt-6 pt-4 border-t border-gray-200 text-sm text-gray-500">
                    <div class="flex justify-between">
                        <span>Generated with <span id="model-used"></span></span>
                        <span>Cost: $<span id="generation-cost"></span></span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Error Display -->
        <div id="error-display" class="hidden">
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <div class="flex">
                    <svg class="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                    </svg>
                    <div>
                        <h3 class="text-sm font-medium text-red-800">Error</h3>
                        <p id="error-message" class="mt-1 text-sm text-red-700"></p>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Basic JavaScript for API Status Check -->
    <script>
        // Check API health status
        async function checkAPIStatus() {
            const statusElement = document.getElementById('api-status');
            try {
                const response = await fetch('/health');
                if (response.ok) {
                    statusElement.textContent = 'Online';
                    statusElement.className = 'font-medium text-green-600';
                } else {
                    statusElement.textContent = 'Offline';
                    statusElement.className = 'font-medium text-red-600';
                }
            } catch (error) {
                statusElement.textContent = 'Offline';
                statusElement.className = 'font-medium text-red-600';
            }
        }

        // Check status on page load
        checkAPIStatus();

        // Check status every 30 seconds
        setInterval(checkAPIStatus, 30000);

        // Store selected content type
        let selectedContentType = null;

        // Content type button handlers
        document.querySelectorAll('.content-type-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                selectedContentType = this.dataset.type;
                document.getElementById('content-type-display').textContent =
                    this.textContent.trim();
                document.getElementById('input-form').classList.remove('hidden');

                // Highlight selected button
                document.querySelectorAll('.content-type-btn').forEach(b =>
                    b.classList.remove('ring-2', 'ring-primary'));
                this.classList.add('ring-2', 'ring-primary');
            });
        });

        // Cancel button handler
        document.getElementById('cancel-btn').addEventListener('click', function() {
            document.getElementById('input-form').classList.add('hidden');
            document.querySelectorAll('.content-type-btn').forEach(b =>
                b.classList.remove('ring-2', 'ring-primary'));
            selectedContentType = null;
        });
    </script>
</body>
</html>
```

**Step 2: Create Minimal FastAPI Static File Serving**

Update `app/main.py` to serve the HTML:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="La Factoria Simple")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Serve index.html at root
@app.get("/")
async def read_index():
    return FileResponse("frontend/index.html")

# Existing endpoints...
```

**Step 3: Create Simple Favicon**

Create `frontend/static/favicon.ico`:

```bash
# Create a simple text favicon (for development)
echo "LF" > frontend/static/favicon.ico

# Or download a free education icon:
curl -L "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f4da.png" \
     -o frontend/static/favicon.png

# Convert to .ico (optional, requires imagemagick)
# convert frontend/static/favicon.png -resize 16x16 frontend/static/favicon.ico
```

**📋 Common Pitfalls & Solutions**:

1. **CDN Blocked by Corporate Firewall**:

   ```html
   <!-- Fallback to local Tailwind -->
   <script>
       if (!window.tailwind) {
           document.write('<link href="/static/tailwind.min.css" rel="stylesheet">');
       }
   </script>
   ```

2. **CORS Issues During Development**:

   ```python
   # Add to FastAPI for development
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],  # Vite default
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Mobile Responsiveness**:
   - Already handled with Tailwind's responsive classes
   - Test with Chrome DevTools mobile view

**🧪 Testing the Implementation**:

```bash
# 1. Start the FastAPI server
cd la-factoria-simple-v2
uvicorn app.main:app --reload

# 2. Open browser
open http://localhost:8000

# 3. Test mobile view
# Chrome: F12 → Toggle device toolbar

# 4. Test API health check
curl http://localhost:8000/health
```

**✅ Quality Gates**:

- [ ] HTML validates at <https://validator.w3.org/>
- [ ] Page loads in under 1 second
- [ ] All buttons are clickable (no JS errors)
- [ ] Mobile responsive (320px to 1920px)
- [ ] API status shows "Online" when server running
- [ ] No console errors in browser
- [ ] Tailwind CSS loads from CDN
- [ ] Form inputs have proper labels for accessibility

**📤 Expected Outputs**:

1. Working HTML page at <http://localhost:8000>
2. Content type selection grid
3. Hidden form ready for FRONT-002
4. API health status indicator
5. Mobile-responsive design

**🔗 Impact on Other Tasks**:

- **FRONT-002**: Add JavaScript interactivity to this structure
- **DEPLOY-001**: This HTML will be served by Railway
- **API-002**: Form will submit to /generate endpoint
- **AUTH-001**: API key field ready for authentication

---

### FRONT-002: Add Form and Interaction

**⏱️ Estimated Time**: 3 hours  
**📋 Prerequisites**: FRONT-001, API-002, API-003 completed

**🎯 Task Objective**: Add JavaScript interactivity to make the form functional, connect to the backend API, and provide a smooth user experience.

**🔧 Tool Selection (August 2025)**:

1. **Vanilla JavaScript** (RECOMMENDED)
   - Why: No build step, works everywhere
   - ES2022 features supported in all modern browsers

2. **Alpine.js** (ALTERNATIVE for complex interactions)
   - Version: v3.13.5 via CDN
   - When to use: If you need reactive data binding

**💻 Complete Implementation**:

**Step 1: Enhance the HTML with Full JavaScript**

Update the `<script>` section in `frontend/index.html`:

```javascript
<script>
// API configuration
const API_BASE_URL = window.location.origin;

// Global state
let selectedContentType = null;

// Check API health status
async function checkAPIStatus() {
    const statusElement = document.getElementById('api-status');
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            statusElement.textContent = 'Online';
            statusElement.className = 'font-medium text-green-600';
        } else {
            statusElement.textContent = 'Offline';
            statusElement.className = 'font-medium text-red-600';
        }
    } catch (error) {
        statusElement.textContent = 'Offline';
        statusElement.className = 'font-medium text-red-600';
    }
}

// Helper function to show/hide elements
function toggleElement(elementId, show) {
    const element = document.getElementById(elementId);
    if (show) {
        element.classList.remove('hidden');
    } else {
        element.classList.add('hidden');
    }
}

// Helper function to display errors
function showError(message) {
    document.getElementById('error-message').textContent = message;
    toggleElement('error-display', true);
    // Auto-hide after 10 seconds
    setTimeout(() => toggleElement('error-display', false), 10000);
}

// Content type button handlers
document.querySelectorAll('.content-type-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        selectedContentType = this.dataset.type;
        document.getElementById('content-type-display').textContent =
            this.textContent.trim();
        toggleElement('input-form', true);
        toggleElement('results', false);
        toggleElement('error-display', false);

        // Highlight selected button
        document.querySelectorAll('.content-type-btn').forEach(b =>
            b.classList.remove('ring-2', 'ring-primary'));
        this.classList.add('ring-2', 'ring-primary');

        // Focus on topic input
        document.getElementById('topic').focus();
    });
});

// Cancel button handler
document.getElementById('cancel-btn').addEventListener('click', function() {
    toggleElement('input-form', false);
    document.querySelectorAll('.content-type-btn').forEach(b =>
        b.classList.remove('ring-2', 'ring-primary'));
    selectedContentType = null;
    document.getElementById('generation-form').reset();
});

// New generation button handler
document.getElementById('new-generation-btn').addEventListener('click', function() {
    toggleElement('results', false);
    toggleElement('input-form', false);
    document.getElementById('generation-form').reset();
    selectedContentType = null;
    document.querySelectorAll('.content-type-btn').forEach(b =>
        b.classList.remove('ring-2', 'ring-primary'));
});

// Form submission handler
document.getElementById('generation-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    // Get form data
    const formData = new FormData(this);
    const topic = formData.get('topic');
    const audience = formData.get('audience');
    const apiKey = formData.get('api_key');

    // Disable submit button
    const submitButton = this.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'Generating...';

    // Show loading state
    toggleElement('input-form', false);
    toggleElement('loading-state', true);
    toggleElement('error-display', false);

    try {
        // Make API request
        const response = await fetch(`${API_BASE_URL}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                content_type: selectedContentType,
                topic: topic,
                audience: audience
            })
        });

        // Parse response
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `Error: ${response.status}`);
        }

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Generation error:', error);
        showError(error.message || 'Failed to generate content. Please try again.');
        toggleElement('loading-state', false);
        toggleElement('input-form', true);
    } finally {
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.textContent = 'Generate Content';
    }
});

// Function to display results
function displayResults(data) {
    toggleElement('loading-state', false);
    toggleElement('results', true);

    // Display content based on type
    const contentDisplay = document.getElementById('content-display');
    contentDisplay.innerHTML = formatContent(data.content, selectedContentType);

    // Display metadata
    document.getElementById('model-used').textContent = data.model || 'Unknown';
    document.getElementById('generation-cost').textContent =
        (data.cost || 0).toFixed(4);
}

// Function to format content based on type
function formatContent(content, contentType) {
    // Parse JSON content if it's a string
    if (typeof content === 'string') {
        try {
            content = JSON.parse(content);
        } catch (e) {
            // If not JSON, display as is
            return `<div class="whitespace-pre-wrap">${escapeHtml(content)}</div>`;
        }
    }

    switch (contentType) {
        case 'flashcards':
            return formatFlashcards(content);
        case 'quiz':
            return formatQuiz(content);
        case 'study_guide':
            return formatStudyGuide(content);
        case 'summary':
            return formatSummary(content);
        default:
            return `<pre class="whitespace-pre-wrap">${JSON.stringify(content, null, 2)}</pre>`;
    }
}

// Format flashcards
function formatFlashcards(flashcards) {
    if (!Array.isArray(flashcards)) {
        flashcards = flashcards.flashcards || [];
    }

    let html = '<div class="space-y-4">';
    flashcards.forEach((card, index) => {
        html += `
            <div class="border rounded-lg p-4 bg-gray-50">
                <div class="font-medium text-gray-900 mb-2">
                    Card ${index + 1}: ${escapeHtml(card.question || card.front)}
                </div>
                <div class="text-gray-700 pl-4 border-l-4 border-primary">
                    ${escapeHtml(card.answer || card.back)}
                </div>
            </div>
        `;
    });
    html += '</div>';
    return html;
}

// Format quiz
function formatQuiz(quiz) {
    if (!Array.isArray(quiz)) {
        quiz = quiz.questions || [];
    }

    let html = '<div class="space-y-6">';
    quiz.forEach((q, index) => {
        html += `
            <div class="border rounded-lg p-4 bg-gray-50">
                <div class="font-medium text-gray-900 mb-3">
                    ${index + 1}. ${escapeHtml(q.question)}
                </div>
                <div class="space-y-2 pl-4">
        `;

        if (q.options) {
            q.options.forEach((option, i) => {
                const letter = String.fromCharCode(65 + i); // A, B, C, D
                const isCorrect = option === q.correct_answer ||
                                 (q.correct === i) ||
                                 (q.correct === letter);
                html += `
                    <div class="flex items-center space-x-2">
                        <span class="font-medium">${letter}.</span>
                        <span class="${isCorrect ? 'text-green-600 font-medium' : ''}">
                            ${escapeHtml(option)}
                        </span>
                    </div>
                `;
            });
        }

        html += '</div></div>';
    });
    html += '</div>';
    return html;
}

// Format study guide
function formatStudyGuide(guide) {
    if (typeof guide === 'string') {
        return `<div class="prose max-w-none">${marked.parse(guide)}</div>`;
    }

    let html = '<div class="prose max-w-none">';
    if (guide.title) {
        html += `<h2>${escapeHtml(guide.title)}</h2>`;
    }
    if (guide.objectives) {
        html += '<h3>Learning Objectives</h3><ul>';
        guide.objectives.forEach(obj => {
            html += `<li>${escapeHtml(obj)}</li>`;
        });
        html += '</ul>';
    }
    if (guide.content) {
        html += marked.parse(guide.content);
    }
    html += '</div>';
    return html;
}

// Format summary
function formatSummary(summary) {
    if (typeof summary === 'string') {
        return `<div class="prose max-w-none">${marked.parse(summary)}</div>`;
    }
    return `<div class="prose max-w-none">${marked.parse(summary.content || JSON.stringify(summary))}</div>`;
}

// Helper to escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Save API key to localStorage (optional)
document.getElementById('api-key').addEventListener('change', function() {
    if (this.value && confirm('Save API key for future use?')) {
        localStorage.setItem('la-factoria-api-key', this.value);
    }
});

// Load saved API key on page load
window.addEventListener('DOMContentLoaded', function() {
    const savedKey = localStorage.getItem('la-factoria-api-key');
    if (savedKey) {
        document.getElementById('api-key').value = savedKey;
    }
});

// Initialize
checkAPIStatus();
setInterval(checkAPIStatus, 30000);
</script>

<!-- Add Marked.js for Markdown parsing -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
```

**Step 2: Add Loading States and Animations**

Add this CSS to the `<head>` section:

```html
<style>
    /* Smooth transitions */
    .content-type-btn {
        transition: all 0.2s ease;
    }

    .content-type-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Pulse animation for loading */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .animate-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    /* Flashcard hover effect */
    .flashcard:hover {
        transform: rotateY(180deg);
    }

    .flashcard {
        transition: transform 0.6s;
        transform-style: preserve-3d;
    }
</style>
```

**Step 3: Add Error Handling and Retry Logic**

Add enhanced error handling:

```javascript
// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Enhanced fetch with retry
async function fetchWithRetry(url, options, retries = MAX_RETRIES) {
    try {
        const response = await fetch(url, options);
        if (response.status === 429) { // Rate limited
            const retryAfter = response.headers.get('Retry-After') || 5;
            throw new Error(`Rate limited. Please wait ${retryAfter} seconds.`);
        }
        return response;
    } catch (error) {
        if (retries > 0 && !error.message.includes('Rate limited')) {
            await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
            return fetchWithRetry(url, options, retries - 1);
        }
        throw error;
    }
}
```

**📋 Common Pitfalls & Solutions**:

1. **CORS Errors in Development**:

   ```javascript
   // Add to development API calls
   const isDev = window.location.hostname === 'localhost';
   const API_BASE_URL = isDev ? 'http://localhost:8000' : window.location.origin;
   ```

2. **Large Content Display Issues**:

   ```javascript
   // Truncate very long content
   function truncateContent(content, maxLength = 10000) {
       if (content.length > maxLength) {
           return content.substring(0, maxLength) + '... (truncated)';
       }
       return content;
   }
   ```

3. **API Key Security**:

   ```javascript
   // Clear API key from memory after use
   formData.set('api_key', '[REDACTED]');
   ```

**🧪 Testing the Implementation**:

```bash
# 1. Test with mock API response
# Add to main.py temporarily:
@app.post("/api/generate")
async def mock_generate():
    return {
        "content": {"flashcards": [
            {"front": "What is 2+2?", "back": "4"},
            {"front": "Capital of France?", "back": "Paris"}
        ]},
        "model": "gpt-3.5-turbo",
        "cost": 0.0015
    }

# 2. Test all content types
# Click each button and submit form

# 3. Test error handling
# Use invalid API key

# 4. Test mobile responsiveness
# Use browser dev tools
```

**✅ Quality Gates**:

- [ ] All content types display correctly
- [ ] Form validation works (required fields)
- [ ] API errors show user-friendly messages
- [ ] Loading states display properly
- [ ] Results render correctly for each content type
- [ ] Mobile interaction works smoothly
- [ ] API key can be saved/loaded (optional)
- [ ] No console errors during normal use

**📤 Expected Outputs**:

1. Fully functional content generation
2. Smooth loading states
3. Clear error messages
4. Properly formatted results
5. Responsive interactions

**🔗 Impact on Other Tasks**:

- **API-002**: Calls the /generate endpoint
- **API-003**: Uses Bearer token authentication
- **DEPLOY-001**: No changes needed for Railway
- **MON-001**: User actions trackable via Langfuse

---

### DEPLOY-001: Deploy to Railway

**⏱️ Estimated Time**: 2 hours  
**📋 Prerequisites**: API-001, API-002, API-003, FRONT-001 completed

**🎯 Task Objective**: Deploy the application to Railway's free tier with automatic sleep functionality to minimize costs.

**🔧 Railway Platform (August 2025)**:

- **URL**: <https://railway.app>
- **Free Tier**: $5 credit/month
- **Auto-sleep**: After 30 min inactivity
- **Wake time**: ~5-10 seconds
- **Perfect for**: 1-10 user applications

**💻 Complete Implementation**:

**Step 1: Create Railway Account**

```bash
# 1. Go to https://railway.app
# 2. Sign up with GitHub (RECOMMENDED)
# 3. Verify email
# 4. You get $5 free credits monthly
```

**Step 2: Install Railway CLI**

```bash
# macOS/Linux (via npm - August 2025)
npm install -g @railway/cli@latest
# Current version: 3.5.2

# Or via Homebrew (macOS)
brew install railway

# Verify installation
railway --version
# Expected: railway version 3.5.2

# Login to Railway
railway login
# Opens browser for authentication
```

**Step 3: Create railway.json Configuration**

Create `railway.json` in project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Step 4: Create Procfile for Deployment**

Create `Procfile` in project root:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Step 5: Update requirements.txt**

Ensure all dependencies are listed:

```txt
fastapi==0.110.0
uvicorn[standard]==0.27.1
python-dotenv==1.0.1
pydantic==2.6.1
httpx==0.26.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
openai==1.12.0
anthropic==0.18.1
langfuse==2.20.1
```

**Step 6: Environment Variables Setup**

Create `.env.example`:

```bash
# API Keys (get from providers)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Langfuse (get from https://cloud.langfuse.com)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# App Config
APP_ENV=production
LOG_LEVEL=INFO
```

**Step 7: Deploy to Railway**

```bash
# 1. Initialize Railway project
railway link
# Select "Create new project"
# Name it: la-factoria-simple

# 2. Set environment variables
railway variables set OPENAI_API_KEY=sk-...
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set LANGFUSE_PUBLIC_KEY=pk-lf-...
railway variables set LANGFUSE_SECRET_KEY=sk-lf-...
railway variables set LANGFUSE_HOST=https://cloud.langfuse.com
railway variables set APP_ENV=production

# 3. Deploy
railway up
# This will:
# - Detect Python app automatically
# - Install dependencies
# - Start the server
# - Provide a URL like: la-factoria-simple.up.railway.app
```

**Step 8: Configure Custom Domain (Optional)**

```bash
# In Railway dashboard:
# 1. Go to Settings → Domains
# 2. Add custom domain
# 3. Update DNS records as instructed

# Or use Railway subdomain:
# yourapp.up.railway.app (free)
```

**Step 9: Monitor Deployment**

```bash
# View logs
railway logs

# Check deployment status
railway status

# Open app in browser
railway open
```

**📋 Common Pitfalls & Solutions**:

1. **Port Binding Error**:

   ```python
   # Always use $PORT env variable
   port = int(os.environ.get("PORT", 8000))
   ```

2. **Static Files Not Serving**:

   ```python
   # Add to main.py
   app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
   ```

3. **CORS Issues**:

   ```python
   # Add your Railway URL
   origins = [
       "https://la-factoria-simple.up.railway.app",
       "http://localhost:3000"  # for local dev
   ]
   ```

4. **Environment Variables Missing**:

   ```bash
   # Always check
   railway variables
   ```

**🧪 Testing the Deployment**:

```bash
# 1. Test health endpoint
curl https://your-app.up.railway.app/health

# 2. Test with browser
open https://your-app.up.railway.app

# 3. Monitor logs for errors
railway logs --tail

# 4. Check sleep/wake behavior
# Wait 30 minutes, then access
# Should wake in 5-10 seconds
```

**💰 Cost Optimization**:

1. **Auto-sleep Configuration**:
   - Happens automatically after 30 min
   - No configuration needed
   - Saves ~90% of costs

2. **Resource Limits**:

   ```json
   {
     "deploy": {
       "maxMemoryMB": 512,
       "maxCPU": 0.5
     }
   }
   ```

3. **Monthly Cost Estimate** (1-10 users):
   - Active time: ~2 hours/day
   - Memory: 512MB
   - **Cost: ~$0.50-$1.00/month**
   - Well within free $5 credit

**✅ Quality Gates**:

- [ ] Railway CLI installed and logged in
- [ ] Environment variables set correctly
- [ ] Application deploys without errors
- [ ] Health check endpoint responds
- [ ] Frontend loads properly
- [ ] API endpoints work with auth
- [ ] Auto-sleep activates after 30 min
- [ ] Wake-up time under 10 seconds
- [ ] Logs show no critical errors

**📤 Expected Outputs**:

1. Live URL: `https://[your-app].up.railway.app`
2. Deployment logs showing success
3. Working health check
4. Functional web interface
5. Auto-sleep after inactivity

**🔗 Impact on Other Tasks**:

- **DB-001**: Will add Railway Postgres to this project
- **MON-001**: Railway provides basic monitoring
- **BACKUP-001**: Can use Railway's backup features
- **SCALE-001**: Easy to scale up when needed

**🚀 Advanced Railway Features**:

1. **GitHub Integration**:

   ```bash
   # Auto-deploy on push
   # In Railway dashboard:
   # Settings → GitHub → Connect repo
   ```

2. **Preview Environments**:

   ```bash
   # Automatic PR deployments
   # Each PR gets unique URL
   ```

3. **Cron Jobs** (if needed):

   ```json
   {
     "cron": {
       "schedule": "0 0 * * *",
       "command": "python scripts/cleanup.py"
     }
   }
   ```

---

### DB-001: Set up Railway Postgres

**⏱️ Estimated Time**: 2 hours  
**📋 Prerequisites**: DEPLOY-001 completed, Railway project created

**🎯 Task Objective**: Add Railway's managed Postgres database to store user data, API keys, and generation history.

**🔧 Railway Postgres (August 2025)**:

- **Free Tier**: 1GB storage, 100MB RAM
- **Connection Pooling**: Built-in
- **Automatic Backups**: Daily
- **Zero Config**: Works instantly
- **Perfect for**: 1-10 users, ~10k generations

**💻 Complete Implementation**:

**Step 1: Add Postgres to Railway Project**

```bash
# Option 1: Via CLI
railway add postgres

# Option 2: Via Dashboard
# 1. Go to your Railway project
# 2. Click "New Service"
# 3. Select "Database" → "PostgreSQL"
# 4. Click "Deploy"
```

**Step 2: Get Database URL**

```bash
# View all variables
railway variables

# You'll see:
# DATABASE_URL=postgresql://user:pass@host:5432/railway

# Copy this URL - Railway auto-injects it
```

**Step 3: Install Database Dependencies**

Update `requirements.txt`:

```txt
# Existing dependencies...

# Database
sqlalchemy==2.0.27
asyncpg==0.29.0
alembic==1.13.1
psycopg2-binary==2.9.9
```

**Step 4: Create Database Configuration**

Create `app/core/database.py`:

```python
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Fix for Railway's postgres:// URL (convert to postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Convert to async URL for asyncpg
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Better for serverless
    echo=False,  # Set True for SQL logging
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

**Step 5: Create Database Models**

Create `app/models/models.py`:

```python
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    api_key_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # GDPR fields
    consent_given_at = Column(DateTime(timezone=True))
    deletion_requested_at = Column(DateTime(timezone=True), nullable=True)

class Generation(Base):
    __tablename__ = "generations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    content_type = Column(String, nullable=False)
    topic = Column(Text, nullable=False)
    audience = Column(String, nullable=False)

    # Results
    content = Column(Text)
    model_used = Column(String)
    cost = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_time_ms = Column(Integer)

    # Tracking
    langfuse_trace_id = Column(String, index=True)
```

**Step 6: Create Alembic Configuration**

```bash
# Initialize Alembic
alembic init alembic

# Update alembic.ini
# Set the database URL line to:
# sqlalchemy.url = will_be_set_in_env_py
```

Update `alembic/env.py`:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

# Import your models
from app.core.database import Base, DATABASE_URL
from app.models.models import User, Generation

# Alembic Config object
config = context.config

# Set database URL from environment
config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("+asyncpg", ""))

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Step 7: Create Initial Migration**

```bash
# Create migration
alembic revision --autogenerate -m "Initial tables"

# Apply migration locally (for testing)
export DATABASE_URL=postgresql://user:pass@localhost/test
alembic upgrade head

# Apply to Railway
railway run alembic upgrade head
```

**Step 8: Add Database Health Check**

Update `app/api/health.py`:

```python
from app.core.database import engine

@router.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check database
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"

    return health_status
```

**📋 Common Pitfalls & Solutions**:

1. **Connection String Format**:

   ```python
   # Railway uses postgres:// but asyncpg needs postgresql+asyncpg://
   if DATABASE_URL.startswith("postgres://"):
       DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
   ```

2. **Connection Pool Issues**:

   ```python
   # Use NullPool for serverless environments
   engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
   ```

3. **Migration Failures**:

   ```bash
   # Always test migrations locally first
   docker run -p 5432:5432 -e POSTGRES_PASSWORD=test postgres:16
   ```

4. **SSL Required**:

   ```python
   # Railway Postgres requires SSL
   engine = create_async_engine(
       DATABASE_URL + "?sslmode=require"
   )
   ```

**🧪 Testing the Implementation**:

```bash
# 1. Test database connection
railway run python -c "
from app.core.database import engine
import asyncio

async def test():
    async with engine.connect() as conn:
        result = await conn.execute('SELECT version()')
        print(await result.scalar())

asyncio.run(test())
"

# 2. Run migrations
railway run alembic upgrade head

# 3. Verify tables created
railway run python -c "
from app.core.database import engine
import asyncio

async def test():
    async with engine.connect() as conn:
        result = await conn.execute('''
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        ''')
        print([row[0] for row in await result.fetchall()])

asyncio.run(test())
"
```

**✅ Quality Gates**:

- [ ] Postgres service added to Railway
- [ ] DATABASE_URL available in environment
- [ ] Database connection successful
- [ ] Migrations run without errors
- [ ] Tables created correctly
- [ ] Health check includes database status
- [ ] No connection pool exhaustion
- [ ] SSL connection working

**📤 Expected Outputs**:

1. Working Postgres database
2. Users and generations tables created
3. Database health check endpoint
4. Migration system ready
5. Connection pooling configured

**🔗 Impact on Other Tasks**:

- **DB-002**: Will create the schema using these models
- **DB-003**: Will implement CRUD operations
- **AUTH-001**: Will store API keys in database
- **GDPR-001**: Will use deletion fields

**💰 Cost Analysis**:

Railway Postgres Free Tier (August 2025):

- Storage: 1GB (enough for ~1M generations)
- RAM: 100MB
- Connections: 20 concurrent
- **Monthly Cost: $0** (included in free tier)

For 1-10 users:

- ~100 generations/day = 3000/month
- Storage used: ~10MB/month
- **Years before hitting limit: 8+**

---

### DB-002: Create Database Schema
**⏱️ Estimated Time**: 2 hours  
**📋 Prerequisites**: DB-001 completed, models created

**🎯 Task Objective**: Create and run migrations to set up the database schema for users, API keys, and generation history.

**💻 Complete Implementation**:

#### Step 1: Create Complete Models

Update `app/models/models.py` with full schema:

```python
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Boolean, Index
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    api_key = Column(String(100), unique=True, index=True, nullable=False)
    api_key_hash = Column(String(255), nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, nullable=False)
    
    # GDPR compliance
    consent_given_at = Column(DateTime(timezone=True), nullable=False)
    consent_version = Column(String(50), default="1.0")
    deletion_requested_at = Column(DateTime(timezone=True))
    
    # Usage tracking
    total_generations = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_active_email', 'is_active', 'email'),
        Index('idx_user_deletion', 'deletion_requested_at'),
    )

class Generation(Base):
    __tablename__ = "generations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Request data
    content_type = Column(String(50), nullable=False, index=True)
    topic = Column(Text, nullable=False)
    audience = Column(String(50), nullable=False)
    request_hash = Column(String(64))  # For deduplication
    
    # Response data
    content = Column(Text)
    model_used = Column(String(50))
    provider = Column(String(50))  # openai, anthropic
    cost = Column(Float, default=0.0)
    tokens_used = Column(Integer)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    processing_time_ms = Column(Integer)
    
    # Tracking
    langfuse_trace_id = Column(String(100), index=True)
    error_message = Column(Text)
    status = Column(String(20), default="completed")  # completed, failed
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_generation_user_date', 'user_id', 'created_at'),
        Index('idx_generation_type_date', 'content_type', 'created_at'),
        Index('idx_generation_request_hash', 'request_hash'),
    )

class APIKeyRotation(Base):
    """Track API key rotation history for security"""
    __tablename__ = "api_key_rotations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    old_key_prefix = Column(String(20))  # First 8 chars for identification
    new_key_prefix = Column(String(20))
    rotated_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(String(100))  # scheduled, user_requested, compromised
```

#### Step 2: Create Initial Migration

```bash
# Generate migration
alembic revision --autogenerate -m "Create initial schema with users, generations, and api key rotation"

# This creates a file in alembic/versions/
```

The migration file will look like:

```python
"""Create initial schema with users, generations, and api key rotation

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-08-02

"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('api_key', sa.String(length=100), nullable=False),
        sa.Column('api_key_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('consent_given_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('consent_version', sa.String(length=50), nullable=True),
        sa.Column('deletion_requested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_generations', sa.Integer(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_active_email', 'users', ['is_active', 'email'])
    op.create_index('idx_user_deletion', 'users', ['deletion_requested_at'])
    op.create_index(op.f('ix_users_api_key'), 'users', ['api_key'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create generations table
    op.create_table('generations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('topic', sa.Text(), nullable=False),
        sa.Column('audience', sa.String(length=50), nullable=False),
        sa.Column('request_hash', sa.String(length=64), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('model_used', sa.String(length=50), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('langfuse_trace_id', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_generation_request_hash', 'generations', ['request_hash'])
    op.create_index('idx_generation_type_date', 'generations', ['content_type', 'created_at'])
    op.create_index('idx_generation_user_date', 'generations', ['user_id', 'created_at'])
    op.create_index(op.f('ix_generations_content_type'), 'generations', ['content_type'])
    op.create_index(op.f('ix_generations_created_at'), 'generations', ['created_at'])
    op.create_index(op.f('ix_generations_langfuse_trace_id'), 'generations', ['langfuse_trace_id'])
    op.create_index(op.f('ix_generations_user_id'), 'generations', ['user_id'])
    
    # Create api_key_rotations table
    op.create_table('api_key_rotations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('old_key_prefix', sa.String(length=20), nullable=True),
        sa.Column('new_key_prefix', sa.String(length=20), nullable=True),
        sa.Column('rotated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('reason', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_key_rotations_user_id'), 'api_key_rotations', ['user_id'])

def downgrade() -> None:
    op.drop_index(op.f('ix_api_key_rotations_user_id'), table_name='api_key_rotations')
    op.drop_table('api_key_rotations')
    op.drop_index(op.f('ix_generations_user_id'), table_name='generations')
    op.drop_index(op.f('ix_generations_langfuse_trace_id'), table_name='generations')
    op.drop_index(op.f('ix_generations_created_at'), table_name='generations')
    op.drop_index(op.f('ix_generations_content_type'), table_name='generations')
    op.drop_index('idx_generation_user_date', table_name='generations')
    op.drop_index('idx_generation_type_date', table_name='generations')
    op.drop_index('idx_generation_request_hash', table_name='generations')
    op.drop_table('generations')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_api_key'), table_name='users')
    op.drop_index('idx_user_deletion', table_name='users')
    op.drop_index('idx_user_active_email', table_name='users')
    op.drop_table('users')
```

#### Step 3: Run Migrations

```bash
# Test locally first
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=test postgres:16
export DATABASE_URL=postgresql://postgres:test@localhost:5432/postgres

# Run migration
alembic upgrade head

# Verify tables
psql $DATABASE_URL -c "\dt"

# Deploy to Railway
railway run alembic upgrade head
```

#### Step 4: Create Migration Helpers

Create `scripts/db_utils.py`:

```python
#!/usr/bin/env python3
"""Database utility commands"""
import asyncio
import click
from app.core.database import engine, Base
from app.models.models import User, Generation, APIKeyRotation

@click.group()
def cli():
    """Database management commands"""
    pass

@cli.command()
def create_tables():
    """Create all tables (for development)"""
    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully")
    
    asyncio.run(_create())

@cli.command()
def drop_tables():
    """Drop all tables (DANGER!)"""
    if click.confirm("⚠️  This will DELETE ALL DATA. Continue?"):
        async def _drop():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            print("✅ Tables dropped")
        
        asyncio.run(_drop())

@cli.command()
def check_schema():
    """Verify schema is up to date"""
    async def _check():
        async with engine.connect() as conn:
            # Check each table
            tables = ['users', 'generations', 'api_key_rotations']
            for table in tables:
                result = await conn.execute(
                    f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table}'"
                )
                exists = result.scalar() > 0
                print(f"{'✅' if exists else '❌'} Table '{table}' exists")
    
    asyncio.run(_check())

if __name__ == '__main__':
    cli()
```

#### Step 5: Add Schema Validation

Create `tests/test_schema.py`:

```python
import pytest
from sqlalchemy import inspect
from app.core.database import engine
from app.models.models import User, Generation, APIKeyRotation

@pytest.mark.asyncio
async def test_all_tables_exist():
    """Verify all required tables exist"""
    async with engine.connect() as conn:
        inspector = inspect(conn)
        tables = await conn.run_sync(lambda sync_conn: inspector.get_table_names())
        
        required_tables = ['users', 'generations', 'api_key_rotations']
        for table in required_tables:
            assert table in tables, f"Table {table} missing"

@pytest.mark.asyncio
async def test_indexes_exist():
    """Verify performance indexes are created"""
    async with engine.connect() as conn:
        # Check user indexes
        result = await conn.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'users' AND indexname LIKE 'idx_%'
        """)
        indexes = [row[0] for row in result]
        assert 'idx_user_active_email' in indexes
        assert 'idx_user_deletion' in indexes
        
        # Check generation indexes
        result = await conn.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'generations' AND indexname LIKE 'idx_%'
        """)
        indexes = [row[0] for row in result]
        assert 'idx_generation_user_date' in indexes
```

**📋 Common Pitfalls & Solutions**:

1. **Migration Order Issues**:
   ```bash
   # Always check current state
   alembic current
   # If stuck, stamp the head
   alembic stamp head
   ```

2. **Index Name Conflicts**:
   ```python
   # Use explicit index names
   Index('idx_unique_name', 'column1', 'column2')
   ```

3. **Schema Drift**:
   ```bash
   # Compare models to database
   alembic check
   ```

**🧪 Testing the Implementation**:

```bash
# 1. Run migration
railway run alembic upgrade head

# 2. Verify schema
railway run python scripts/db_utils.py check-schema

# 3. Test with sample data
railway run python -c "
from app.core.database import AsyncSessionLocal
from app.models.models import User
import asyncio

async def test():
    async with AsyncSessionLocal() as db:
        user = User(
            email='test@example.com',
            api_key='lfs_test123',
            api_key_hash='hashed',
            consent_given_at=datetime.utcnow()
        )
        db.add(user)
        await db.commit()
        print('✅ User created')

asyncio.run(test())
"
```

**✅ Quality Gates**:

- [ ] All migrations run without errors
- [ ] Tables created with correct columns
- [ ] All indexes created for performance
- [ ] Schema validation tests pass
- [ ] Can insert/query test data
- [ ] Rollback works if needed

**📤 Expected Outputs**:

1. Three tables created: users, generations, api_key_rotations
2. All indexes created for query performance
3. Migration history tracked in alembic_version
4. Schema validation passing

**🔗 Impact on Other Tasks**:

- **DB-003**: Will use this schema for CRUD operations
- **AUTH-001**: Will store API keys using this schema
- **GDPR-001**: Uses deletion_requested_at field
- **PERF-001**: Relies on indexes for performance

---

### DB-003: Implement User CRUD
**⏱️ Estimated Time**: 3 hours  
**📋 Prerequisites**: DB-002 completed, schema created

**🎯 Task Objective**: Implement Create, Read, Update, Delete operations for users with proper async patterns and error handling.

**💻 Complete Implementation**:

#### Step 1: Create User Repository

Create `app/repositories/user_repository.py`:

```python
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.exc import IntegrityError
from app.models.models import User
from app.core.exceptions import (
    UserNotFoundError, 
    UserAlreadyExistsError,
    DatabaseError
)
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    """Repository for user database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, 
                    email: str, 
                    api_key: str, 
                    api_key_hash: str,
                    consent_version: str = "1.0") -> User:
        """Create a new user"""
        try:
            user = User(
                email=email.lower(),  # Normalize email
                api_key=api_key,
                api_key_hash=api_key_hash,
                consent_given_at=datetime.utcnow(),
                consent_version=consent_version,
                is_active=True,
                total_generations=0,
                total_cost=0.0
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Created user: {user.id}")
            return user
            
        except IntegrityError as e:
            await self.db.rollback()
            if "email" in str(e.orig):
                raise UserAlreadyExistsError(f"User with email {email} already exists")
            elif "api_key" in str(e.orig):
                raise UserAlreadyExistsError(f"API key already in use")
            raise DatabaseError(f"Database error: {str(e)}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise DatabaseError(f"Failed to create user: {str(e)}")
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        query = select(User).where(
            and_(User.id == user_id, User.is_active == True)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        query = select(User).where(
            and_(
                User.email == email.lower(),
                User.is_active == True,
                User.deletion_requested_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_api_key(self, api_key: str) -> Optional[User]:
        """Get user by API key (for authentication)"""
        query = select(User).where(
            and_(
                User.api_key == api_key,
                User.is_active == True,
                User.deletion_requested_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        # Update last active timestamp
        if user:
            await self.update_last_active(user.id)
        
        return user
    
    async def update_last_active(self, user_id: str) -> None:
        """Update user's last active timestamp"""
        query = update(User).where(User.id == user_id).values(
            last_active_at=datetime.utcnow()
        )
        await self.db.execute(query)
        await self.db.commit()
    
    async def update_usage(self, user_id: str, cost: float) -> None:
        """Update user's usage statistics"""
        query = update(User).where(User.id == user_id).values(
            total_generations=User.total_generations + 1,
            total_cost=User.total_cost + cost,
            last_active_at=datetime.utcnow()
        )
        await self.db.execute(query)
        await self.db.commit()
    
    async def request_deletion(self, user_id: str) -> User:
        """Mark user for deletion (GDPR)"""
        user = await self.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        query = update(User).where(User.id == user_id).values(
            deletion_requested_at=datetime.utcnow(),
            is_active=False
        )
        await self.db.execute(query)
        await self.db.commit()
        
        logger.info(f"User {user_id} marked for deletion")
        return user
    
    async def list_pending_deletions(self) -> List[User]:
        """Get users pending deletion (for GDPR processing)"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        query = select(User).where(
            and_(
                User.deletion_requested_at.isnot(None),
                User.deletion_requested_at <= thirty_days_ago
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def permanently_delete(self, user_id: str) -> None:
        """Permanently delete user and their data"""
        # Delete generations first (cascade)
        await self.db.execute(
            delete(Generation).where(Generation.user_id == user_id)
        )
        
        # Delete API key rotations
        await self.db.execute(
            delete(APIKeyRotation).where(APIKeyRotation.user_id == user_id)
        )
        
        # Delete user
        await self.db.execute(
            delete(User).where(User.id == user_id)
        )
        
        await self.db.commit()
        logger.info(f"Permanently deleted user {user_id}")
    
    async def get_statistics(self, user_id: str) -> dict:
        """Get user statistics"""
        user = await self.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        # Get generation count by type
        query = select(
            Generation.content_type,
            func.count(Generation.id).label('count')
        ).where(
            Generation.user_id == user_id
        ).group_by(Generation.content_type)
        
        result = await self.db.execute(query)
        content_types = {row.content_type: row.count for row in result}
        
        return {
            "user_id": user.id,
            "email": user.email,
            "total_generations": user.total_generations,
            "total_cost": user.total_cost,
            "created_at": user.created_at.isoformat(),
            "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None,
            "content_types": content_types
        }
```

#### Step 2: Create User Service

Create `app/services/user_service.py`:

```python
from typing import Optional
from datetime import datetime
from passlib.context import CryptContext
import secrets
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserCreate, UserResponse, UserStats
from app.core.exceptions import UserNotFoundError, UserAlreadyExistsError

class UserService:
    """Business logic for user operations"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"lfs_{secrets.token_urlsafe(32)}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        # Only hash the secret part, not the prefix
        secret_part = api_key.split("_", 1)[1]
        return self.pwd_context.hash(secret_part)
    
    def verify_api_key(self, api_key: str, hashed: str) -> bool:
        """Verify an API key against its hash"""
        secret_part = api_key.split("_", 1)[1]
        return self.pwd_context.verify(secret_part, hashed)
    
    async def create_user(self, 
                         repo: UserRepository, 
                         user_data: UserCreate) -> UserResponse:
        """Create a new user with API key"""
        # Check if user exists
        existing = await repo.get_by_email(user_data.email)
        if existing:
            raise UserAlreadyExistsError(f"User with email {user_data.email} already exists")
        
        # Generate API key
        api_key = self.generate_api_key()
        api_key_hash = self.hash_api_key(api_key)
        
        # Create user
        user = await repo.create(
            email=user_data.email,
            api_key=api_key,
            api_key_hash=api_key_hash,
            consent_version=user_data.consent_version or "1.0"
        )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            api_key=api_key,  # Return the plain API key only on creation
            created_at=user.created_at,
            is_active=user.is_active
        )
    
    async def get_user_stats(self,
                           repo: UserRepository,
                           user_id: str) -> UserStats:
        """Get user statistics"""
        stats = await repo.get_statistics(user_id)
        return UserStats(**stats)
    
    async def rotate_api_key(self,
                           repo: UserRepository,
                           user_id: str,
                           reason: str = "user_requested") -> str:
        """Rotate user's API key"""
        user = await repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        # Generate new API key
        old_key_prefix = user.api_key[:8] + "..."
        new_api_key = self.generate_api_key()
        new_api_key_hash = self.hash_api_key(new_api_key)
        
        # Update user
        user.api_key = new_api_key
        user.api_key_hash = new_api_key_hash
        
        # Record rotation
        rotation = APIKeyRotation(
            user_id=user_id,
            old_key_prefix=old_key_prefix,
            new_key_prefix=new_api_key[:8] + "...",
            reason=reason
        )
        
        repo.db.add(rotation)
        await repo.db.commit()
        
        return new_api_key
```

#### Step 3: Create Pydantic Schemas

Create `app/schemas/user_schemas.py`:

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict

class UserCreate(BaseModel):
    """Schema for creating a user"""
    email: EmailStr
    consent_version: Optional[str] = "1.0"
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "consent_version": "1.0"
            }
        }

class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    api_key: Optional[str] = None  # Only returned on creation
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class UserStats(BaseModel):
    """Schema for user statistics"""
    user_id: str
    email: str
    total_generations: int
    total_cost: float
    created_at: str
    last_active_at: Optional[str]
    content_types: Dict[str, int]

class UserDeletionRequest(BaseModel):
    """Schema for deletion request"""
    confirmation: str = Field(..., pattern="^DELETE$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "confirmation": "DELETE"
            }
        }
```

#### Step 4: Create API Endpoints

Create `app/api/users.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user_schemas import (
    UserCreate, UserResponse, UserStats, UserDeletionRequest
)
from app.core.exceptions import UserNotFoundError, UserAlreadyExistsError

router = APIRouter(prefix="/api/users", tags=["users"])
user_service = UserService()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user and return API key"""
    try:
        repo = UserRepository(db)
        user = await user_service.create_user(repo, user_data)
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
        is_active=current_user.is_active
    )

@router.get("/me/stats", response_model=UserStats)
async def get_current_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user statistics"""
    try:
        repo = UserRepository(db)
        stats = await user_service.get_user_stats(repo, current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )

@router.post("/me/rotate-key", response_model=dict)
async def rotate_api_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rotate current user's API key"""
    try:
        repo = UserRepository(db)
        new_api_key = await user_service.rotate_api_key(
            repo, current_user.id, "user_requested"
        )
        return {
            "message": "API key rotated successfully",
            "api_key": new_api_key
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rotate API key: {str(e)}"
        )

@router.delete("/me", status_code=status.HTTP_202_ACCEPTED)
async def request_account_deletion(
    deletion_request: UserDeletionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request account deletion (GDPR)"""
    if deletion_request.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid confirmation. Must be 'DELETE'"
        )
    
    try:
        repo = UserRepository(db)
        await repo.request_deletion(current_user.id)
        return {
            "message": "Account deletion requested. Will be processed within 30 days.",
            "deletion_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request deletion: {str(e)}"
        )
```

#### Step 5: Create Tests

Create `tests/test_user_crud.py`:

```python
import pytest
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user_schemas import UserCreate

@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test user creation"""
    repo = UserRepository(db_session)
    service = UserService()
    
    user_data = UserCreate(email="test@example.com")
    user = await service.create_user(repo, user_data)
    
    assert user.email == "test@example.com"
    assert user.api_key.startswith("lfs_")
    assert len(user.api_key) > 40

@pytest.mark.asyncio
async def test_duplicate_email_error(db_session):
    """Test duplicate email handling"""
    repo = UserRepository(db_session)
    service = UserService()
    
    # Create first user
    user_data = UserCreate(email="test@example.com")
    await service.create_user(repo, user_data)
    
    # Try to create duplicate
    with pytest.raises(UserAlreadyExistsError):
        await service.create_user(repo, user_data)

@pytest.mark.asyncio
async def test_api_key_authentication(db_session):
    """Test API key lookup"""
    repo = UserRepository(db_session)
    service = UserService()
    
    # Create user
    user_data = UserCreate(email="test@example.com")
    created = await service.create_user(repo, user_data)
    
    # Find by API key
    found = await repo.get_by_api_key(created.api_key)
    assert found is not None
    assert found.email == "test@example.com"

@pytest.mark.asyncio
async def test_user_deletion_request(db_session):
    """Test GDPR deletion request"""
    repo = UserRepository(db_session)
    service = UserService()
    
    # Create user
    user_data = UserCreate(email="test@example.com")
    created = await service.create_user(repo, user_data)
    
    # Request deletion
    await repo.request_deletion(created.id)
    
    # User should be inactive
    user = await repo.get_by_id(created.id)
    assert user is None  # get_by_id filters inactive users
    
    # Should appear in pending deletions
    pending = await repo.list_pending_deletions()
    assert len(pending) == 0  # Not 30 days old yet

@pytest.mark.asyncio
async def test_usage_tracking(db_session):
    """Test usage statistics update"""
    repo = UserRepository(db_session)
    service = UserService()
    
    # Create user
    user_data = UserCreate(email="test@example.com")
    created = await service.create_user(repo, user_data)
    
    # Update usage
    await repo.update_usage(created.id, 0.0015)
    
    # Check stats
    stats = await service.get_user_stats(repo, created.id)
    assert stats.total_generations == 1
    assert stats.total_cost == 0.0015
```

**📋 Common Pitfalls & Solutions**:

1. **N+1 Query Problem**:
   ```python
   # Use eager loading for related data
   query = select(User).options(selectinload(User.generations))
   ```

2. **Race Conditions**:
   ```python
   # Use SELECT FOR UPDATE to lock rows
   query = select(User).where(User.id == user_id).with_for_update()
   ```

3. **Connection Pool Exhaustion**:
   ```python
   # Always use async context manager
   async with get_db() as session:
       # operations
   ```

**✅ Quality Gates**:

- [ ] All CRUD operations working
- [ ] API key authentication functional
- [ ] GDPR deletion request working
- [ ] Usage tracking accurate
- [ ] All tests passing
- [ ] No SQL injection vulnerabilities

**📤 Expected Outputs**:

1. Complete user management system
2. API key generation and rotation
3. GDPR-compliant deletion process
4. Usage statistics tracking
5. Full test coverage

**🔗 Impact on Other Tasks**:

- **AUTH-001**: Uses these CRUD operations
- **GDPR-001**: Implements the deletion workflow
- **API-002**: Uses update_usage for tracking
- **TEST-001**: Includes these tests

## Enhancement Progress Tracking

- [x] DISCOVER-001: Fully enhanced with anti-hallucination context
- [x] DISCOVER-002: Fully enhanced with anti-hallucination context
- [x] DISCOVER-003: Fully enhanced with anti-hallucination context
- [x] SETUP-001: Fully enhanced with repository structure details
- [x] SETUP-002: Fully enhanced with Railway-specific context
- [x] SETUP-003: Fully enhanced with pytest testing framework
- [x] API-001: Fully enhanced with health check implementation
- [x] API-002: Fully enhanced with content generation endpoint structure
- [x] API-003: Fully enhanced with simple authentication system
- [x] API-004: Fully enhanced with AI provider and Langfuse integration
- [x] FRONT-001: Fully enhanced with basic HTML structure
- [x] FRONT-002: Fully enhanced with form and interaction
- [x] DEPLOY-001: Fully enhanced with Railway deployment
- [x] DB-001: Fully enhanced with Railway Postgres setup
- [x] DB-002: Fully enhanced with database schema creation
- [x] DB-003: Fully enhanced with user CRUD operations
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
