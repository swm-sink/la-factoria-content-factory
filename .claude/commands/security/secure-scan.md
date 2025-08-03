---
name: /secure-scan
description: "Code analysis for . with standard requirements"
usage: /secure-scan [--type vulnerability|sast|dast|all] [--severity critical|high|medium|low]
category: security
tools: Bash, Read, Write, Grep
---

# Code Analysis for

I'll perform comprehensive code analysis appropriate for your **standard** requirements and **users** user base.

## Instructions

Use this command to perform comprehensive security analysis of your Python codebase. Choose from different scan types based on your security requirements.

**Quick Scan:**

```bash
/secure-scan                    # Default comprehensive scan
/secure-scan --type all         # Full security analysis
```

**Specific Scans:**

```bash
/secure-scan --type vulnerability   # Check dependencies
/secure-scan --type sast           # Static code analysis
/secure-scan --type dast           # Dynamic analysis
```

**Filter by Severity:**

```bash
/secure-scan --severity critical   # Critical issues only
/secure-scan --severity high       # High and critical
```

## Analysis Configuration

- **Project**: .
- **Analysis Level**: standard
- **Tech Stack**: Python
- **Primary Language**: Python
- **API Style**: [INSERT_API_STYLE]

## Scan Types

### Dependency Analysis

Analyze dependencies for Python:

```bash
/secure-scan --type vulnerability
```

### Static Analysis (SAST)

Code pattern analysis for Python:

```bash
/secure-scan --type sast
```

### Dynamic Analysis (DAST)

Runtime behavior analysis for [INSERT_API_STYLE] APIs:

```bash
/secure-scan --type dast
```

### Comprehensive Analysis

All code checks for standard:

```bash
/secure-scan --type all
```

## Analysis Requirements

### standard Level Checks

Your analysis level includes:

- OWASP Top 10 patterns
- Dependency compatibility analysis
- Hardcoded value detection
- Configuration review
- Access pattern validation

## Compliance for users

Based on your user base:

- Data protection requirements
- Privacy compliance
- Audit logging
- Encryption standards
- Access controls

## Integration with GitHub Actions

Automated analysis gates:

- Pre-commit pattern scanning
- PR code validation
- Build-time SAST
- Deployment configuration checks
- Continuous monitoring

## Remediation Guidance

For small teams:

- Prioritized findings
- Fix recommendations
- Code examples
- Security best practices
- Team training needs

## Reporting

Analysis reports tailored for:

- Development team
- Quality team
- Management overview
- Compliance documentation
- agile tracking

What type of code analysis would you like to run?
