---
name: /secure-audit
description: "Comprehensive code audit for . with standard requirements"
usage: /secure-audit [--scope full|code|infrastructure|compliance] [--report-format detailed|executive|compliance]
category: security
tools: Bash, Read, Write, Grep
---

# Code Audit for .

I'll perform a comprehensive code audit of **.** aligned with your **standard** requirements and **users** compliance needs.

## Audit Configuration

- **Project**: .
- **Security Level**: standard
- **Tech Stack**: Python
- **Compliance**: Based on users

## Audit Scopes

### Full Code Audit
Complete code assessment:
```bash
/secure-audit --scope full
```
- Code quality review
- Infrastructure audit
- Access control review
- Compliance validation

### Code Quality Audit
Source code focus:
```bash
/secure-audit --scope code
```
- Python code issues
- Dependency analysis
- Secret detection
- Code quality metrics

### Infrastructure Audit
production configuration:
```bash
/secure-audit --scope infrastructure
```
- Configuration review
- Network configuration
- Access controls
- Encryption status

### Compliance Audit
users requirements:
```bash
/secure-audit --scope compliance
```
- Regulatory compliance
- Data protection
- Privacy controls
- Audit trail review

## standard Checks

Your analysis level includes:
- OWASP Top 10 patterns
- Authentication mechanisms
- Authorization controls
- Data encryption standards
- API security ([INSERT_API_STYLE])
- Session management
- Input validation

## Automated Analysis

### Static Analysis
For Python:
- Code pattern analysis
- Configuration analysis
- Dependency checking
- License compliance

### Dynamic Analysis
Runtime behavior testing:
- API testing
- Input validation testing
- Authentication flow testing
- Session management tests

## Manual Review Areas

### Architecture Review
- System design review
- Data flow analysis
- Component boundaries
- Risk modeling

### Access Control
For small teams:
- User permissions
- Role definitions
- Service accounts
- API keys management

## Reporting Options

### Executive Summary
High-level overview:
```bash
/secure-audit --report-format executive
```
- Risk summary
- Critical findings
- Recommendations
- Compliance status

### Detailed Report
Technical deep-dive:
```bash
/secure-audit --report-format detailed
```
- Full vulnerability list
- Code examples
- Remediation steps
- Timeline estimates

### Compliance Report
Regulatory focus:
```bash
/secure-audit --report-format compliance
```
- Standards mapping
- Gap analysis
- Evidence collection
- Certification readiness

## Integration Points

### With GitHub Actions
- Automated audit triggers
- Pipeline integration
- Fail-fast on critical issues
- Trend tracking

### With agile
- Approval workflows
- Issue tracking
- Remediation planning
- Progress monitoring

## Risk Scoring

Based on:
- Severity levels
- Exploitability
- Business impact
- Data sensitivity

## Remediation Guidance

For each finding:
- Risk assessment
- Fix recommendations
- Code examples
- Testing approach
- Verification steps

Which type of code audit would you like to perform?