#!/bin/bash

# GitHub PAT Authentication Setup Script
# This script configures git to use the PAT stored in .env.local

set -e

echo "🔐 Setting up GitHub PAT authentication..."

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "❌ Error: .env.local file not found"
    echo "Please create .env.local with:"
    echo "  GITHUB_PAT=your-pat-token"
    echo "  GITHUB_USER=your-username"
    exit 1
fi

# Source the environment file
source .env.local

# Validate required variables
if [ -z "$GITHUB_PAT" ] || [ -z "$GITHUB_USER" ]; then
    echo "❌ Error: GITHUB_PAT or GITHUB_USER not set in .env.local"
    exit 1
fi

# Configure git to use the PAT for this repository
echo "📝 Configuring repository-specific credentials..."

# Set the remote URL with embedded credentials (stored in git config, not in URL)
REMOTE_URL=$(git remote get-url origin)

# Parse the URL to extract the repository path
if [[ $REMOTE_URL == https://* ]]; then
    # Extract repository path from HTTPS URL
    REPO_PATH=$(echo $REMOTE_URL | sed 's|https://github.com/||')
elif [[ $REMOTE_URL == git@* ]]; then
    # Extract repository path from SSH URL
    REPO_PATH=$(echo $REMOTE_URL | sed 's|git@github.com:||')
else
    echo "⚠️  Warning: Unexpected remote URL format: $REMOTE_URL"
    REPO_PATH="swm-sink/la-factoria-content-factory"
fi

# Configure credential helper for this repository
git config --local credential.helper store
git config --local credential.https://github.com.username "$GITHUB_USER"

# Create credentials file in git config directory
GIT_DIR=$(git rev-parse --git-dir)
CREDS_FILE="$GIT_DIR/credentials"

# Write credentials to local git directory (not global)
echo "https://${GITHUB_USER}:${GITHUB_PAT}@github.com" > "$CREDS_FILE"
chmod 600 "$CREDS_FILE"

# Configure git to use the local credentials file
git config --local credential.helper "store --file=$CREDS_FILE"

# Verify configuration
echo "✅ GitHub PAT authentication configured!"
echo "📦 Repository: $REPO_PATH"
echo "👤 User: $GITHUB_USER"
echo ""
echo "🔧 Configuration details:"
echo "  - Credentials stored in: $CREDS_FILE"
echo "  - Configuration is repository-specific (--local)"
echo "  - PAT will be used for all git operations"
echo ""
echo "🚀 You can now push/pull without entering credentials:"
echo "  git push origin main"
echo ""
echo "⚠️  Security notes:"
echo "  - Never commit .env.local (it's in .gitignore)"
echo "  - Credentials are stored locally in .git/credentials"
echo "  - To remove credentials, run: git config --local --unset credential.helper"