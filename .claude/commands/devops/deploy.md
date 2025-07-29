---
name: /deploy
description: "Deploy . to production using GitHub Actions"
usage: /deploy [environment] [--strategy blue-green|canary|rolling]
category: devops
tools: Bash, Read, Write, Edit
security_level: CRITICAL
---

# Deploy .

<!-- SECURITY: Include command security wrapper for injection prevention -->
<include>components/security/command-security-wrapper.md</include>
<!-- SECURITY: Include functional credential protection -->
<include>components/security/credential-protection.md</include>
<include>components/security/protection-feedback.md</include>

**CRITICAL SECURITY NOTICE**: This command executes deployment operations with elevated privileges. ALL inputs are validated using security wrapper functions to prevent command injection, path traversal, and credential exposure.

**🔒 ADVANCED CREDENTIAL PROTECTION ACTIVE**: 
- AWS, GCP, Azure credentials automatically detected and masked using 13 detection patterns
- Kubernetes secrets, Docker registry tokens, and API keys protected
- Deployment error messages sanitized to prevent credential leakage
- Real-time feedback when protection activates

I'll help you deploy **.** to **production** using your configured **GitHub Actions** pipeline with proper validation.

## Deployment Configuration

- **Project**: .
- **Tech Stack**: Python
- **Target**: production
- **CI/CD**: GitHub Actions
- **Security**: standard

## Deployment Strategies

### For small Teams

Based on your team size and agile workflow:

#### Blue-Green Deployment
Zero-downtime deployment for users (with validation):
```bash
/deploy production --strategy blue-green
# SECURITY: Environment 'production' validated using validateEnvironmentName()
# SECURITY: Strategy 'blue-green' validated against allowed deployment strategies
# SECURITY: All deployment commands validated against DEPLOY_ALLOWED_COMMANDS
```

#### Canary Deployment
Gradual rollout for balanced systems (with validation):
```bash
/deploy production --strategy canary --percentage 10
# SECURITY: Environment validated, strategy validated, percentage value sanitized
# SECURITY: All canary deployment commands validated against security allowlist
```

#### Rolling Update
Standard deployment for production (with validation):
```bash
/deploy staging --strategy rolling
# SECURITY: Environment 'staging' validated using validateEnvironmentName()
# SECURITY: Rolling update commands validated against DEPLOY_ALLOWED_COMMANDS
```

## Pre-Deployment Checks

Your standard level requires:
- Input validation
- Environment name validation
- Deployment strategy validation
- Command allowlist validation
- Code analysis with results
- Dependency compatibility check with reporting
- Configuration validation
- Health check endpoints
- Credential protection
- Error message handling

## Environment-Specific Settings

### production Configuration
- Auto-scaling policies
- Load balancer settings
- Database connection strings
- Environment variables

## Integration with GitHub Actions

Your deployment pipeline includes:
- Build stage for Python
- Test execution with pytest
- Code analysis
- Deployment automation
- Post-deployment validation

## Rollback Strategy

For users protection:
- Automatic rollback triggers
- Manual rollback command
- Database migration reversal
- State preservation

## Monitoring Integration

Post-deployment for .:
- Application metrics
- Error rate monitoring
- Performance baselines
- User experience tracking

**DEPLOYMENT EXECUTION PROCESS:**

1. **Input Validation**: All deployment parameters validated
2. **Environment Validation**: Environment name validated
3. **Strategy Validation**: Deployment strategy validated against policies
4. **Command Validation**: All deployment commands validated against allowlist
5. **ENHANCED CREDENTIAL PROTECTION**: 
   - Pre-execution: Scan all command arguments for credentials (13 patterns)
   - During execution: Protect streaming output from kubectl, docker, helm, terraform
   - Post-execution: Mask all sensitive data in results and logs
6. **Secure Execution**: Deployment executed using executeCommandWithCredentialProtection() wrapper
7. **Audit Logging**: Complete security audit trail maintained (credentials masked)
8. **Enhanced Error Sanitization**: All error messages sanitized using credential-aware error handling

**Cloud Provider Credential Protection:**
- **AWS**: Access keys (AKIA*), secret keys, session tokens automatically masked
- **GCP**: Service account keys, OAuth tokens, project IDs protected
- **Azure**: Subscription IDs, client secrets, tenant IDs masked
- **Kubernetes**: Service account tokens, secrets, config files protected
- **Docker**: Registry authentication, private registry credentials masked

**ALLOWED ENVIRONMENTS**: development, staging, production, test, dev, stage, prod
**ALLOWED STRATEGIES**: blue-green, canary, rolling
**ALLOWED COMMANDS**: docker, kubectl, helm, systemctl, aws, gcloud, az, terraform

Which environment would you like to deploy to? (Environment will be validated for security compliance)