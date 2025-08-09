# Git Configuration Documentation for La Factoria

## Overview
This repository uses **repository-specific** git configuration to ensure consistent attribution while maintaining security and flexibility.

## Current Configuration

### Repository-Specific Settings
- **User Name**: `swm-sink`
- **Email**: `stefan.menssink@gmail.com`
- **Scope**: LOCAL to this repository only
- **Location**: `.git/config` (not tracked in version control)

## Multiple Perspective Analysis

### 1. Security Perspective ✅
- **Isolation**: Configuration is LOCAL only - does NOT affect other repositories
- **No Global Pollution**: User's global git config remains unchanged
- **Credential Safety**: No passwords or tokens stored (uses SSH/HTTPS separately)
- **Privacy**: Email is already public on GitHub profile

### 2. Persistence Perspective ✅
- **Local Persistence**: Settings stored in `.git/config` (survives pulls/fetches)
- **Setup Script**: `.git-local-config.sh` provided for fresh clones
- **Documentation**: This file serves as reference for configuration
- **Not in Version Control**: `.git/config` is never committed (Git ignores it)

### 3. Collaboration Perspective ✅
- **Team Flexibility**: Each developer can override with their own local config
- **No Forced Settings**: Configuration not enforced through tracked files
- **Clear Documentation**: Team members know expected configuration
- **Setup Script**: Easy onboarding with `.git-local-config.sh`

### 4. CI/CD Perspective ✅
- **GitHub Actions**: Uses GITHUB_ACTOR for attribution automatically
- **Railway Deployment**: Doesn't require git user configuration
- **Local Development**: Proper attribution for manual commits
- **Automated Commits**: CI systems use their own service accounts

### 5. History Perspective ✅
- **Future Commits**: All new commits will use correct attribution
- **Past Commits**: Can be fixed with `--reset-author` if needed
- **Audit Trail**: Clear attribution for project history
- **Blame Accuracy**: Correct author for `git blame` and history

## Setup Instructions

### For New Clones
```bash
# After cloning the repository
cd la-factoria-content-factory
chmod +x .git-local-config.sh
./.git-local-config.sh
```

### Manual Setup
```bash
# Set user configuration (local to this repo only)
git config --local user.name "swm-sink"
git config --local user.email "stefan.menssink@gmail.com"
```

### Verify Configuration
```bash
# Check current settings
git config --local user.name
git config --local user.email

# See all local settings
git config --local --list
```

## Fixing Existing Commits

### Fix Last Commit
```bash
git commit --amend --reset-author --no-edit
```

### Fix Multiple Recent Commits
```bash
# Fix last 14 commits (adjust number as needed)
git rebase -i HEAD~14 --exec 'git commit --amend --reset-author --no-edit'
```

### Important Notes on Rewriting History
⚠️ **WARNING**: Rewriting history changes commit hashes
- Only do this on branches not yet pushed
- Or coordinate with team if already pushed
- Force push will be required: `git push --force-with-lease`

## Configuration Hierarchy

Git uses this precedence (highest to lowest):
1. **Command line** flags (e.g., `git -c user.name="Name" commit`)
2. **Repository** config (`.git/config`) ← **WE USE THIS**
3. **Global** config (`~/.gitconfig`)
4. **System** config (`/etc/gitconfig`)

## Best Practices

### For This Repository
1. ✅ Always use repository-specific configuration
2. ✅ Run `.git-local-config.sh` after cloning
3. ✅ Verify attribution before pushing
4. ✅ Document any configuration changes

### What NOT to Do
1. ❌ Don't set global config to project-specific values
2. ❌ Don't commit `.git/config` file
3. ❌ Don't hardcode credentials in tracked files
4. ❌ Don't force push without team coordination

## Troubleshooting

### Config Not Working?
```bash
# Check if local config exists
git config --local --list

# Re-run setup script
./.git-local-config.sh

# Verify no global override
git config --global user.name
git config --global user.email
```

### Wrong Attribution on Commits?
```bash
# Check the author of recent commits
git log --format="%h %an <%ae>" -5

# If wrong, fix with reset-author (see above)
```

## Additional Configuration Files

### `.git-local-config.sh`
- Bash script to set up repository configuration
- Run after cloning repository
- Safe to run multiple times

### `.gitmessage`
- Commit message template
- Helps maintain consistent commit format
- Includes AI Agent Note section for autonomous development

### This Document
- Comprehensive reference for git configuration
- Explains rationale from multiple perspectives
- Provides troubleshooting guidance

## Conclusion

This configuration setup ensures:
- ✅ Correct attribution for project commits
- ✅ No interference with other projects
- ✅ Flexibility for team collaboration
- ✅ Compatibility with CI/CD systems
- ✅ Clear documentation and onboarding

Last Updated: 2025-01-09
Configuration By: AI Agent implementing user requirements for swm-sink/stefan.menssink@gmail.com