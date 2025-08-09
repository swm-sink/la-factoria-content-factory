#!/bin/bash
# Validate git configuration for La Factoria repository

echo "========================================="
echo "Git Configuration Validation for La Factoria"
echo "========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Expected values
EXPECTED_NAME="swm-sink"
EXPECTED_EMAIL="stefan.menssink@gmail.com"

# Track validation status
ALL_GOOD=true

echo "1. Checking Local Repository Configuration"
echo "-------------------------------------------"

# Check user.name
CURRENT_NAME=$(git config --local user.name)
if [ "$CURRENT_NAME" = "$EXPECTED_NAME" ]; then
    echo -e "${GREEN}✅${NC} user.name: $CURRENT_NAME"
else
    echo -e "${RED}❌${NC} user.name: Expected '$EXPECTED_NAME', got '$CURRENT_NAME'"
    ALL_GOOD=false
fi

# Check user.email
CURRENT_EMAIL=$(git config --local user.email)
if [ "$CURRENT_EMAIL" = "$EXPECTED_EMAIL" ]; then
    echo -e "${GREEN}✅${NC} user.email: $CURRENT_EMAIL"
else
    echo -e "${RED}❌${NC} user.email: Expected '$EXPECTED_EMAIL', got '$CURRENT_EMAIL'"
    ALL_GOOD=false
fi

echo ""
echo "2. Checking Git Hooks Configuration"
echo "------------------------------------"

# Check hooks path
HOOKS_PATH=$(git config --local core.hooksPath)
if [ "$HOOKS_PATH" = ".githooks" ]; then
    echo -e "${GREEN}✅${NC} Hooks path: $HOOKS_PATH"
    
    # Check if pre-commit hook exists and is executable
    if [ -x ".githooks/pre-commit" ]; then
        echo -e "${GREEN}✅${NC} Pre-commit hook: Exists and is executable"
    else
        echo -e "${YELLOW}⚠️${NC} Pre-commit hook: Not found or not executable"
        ALL_GOOD=false
    fi
else
    echo -e "${YELLOW}⚠️${NC} Hooks path not configured (optional)"
fi

echo ""
echo "3. Checking Supporting Files"
echo "-----------------------------"

# Check for setup script
if [ -f ".git-local-config.sh" ] && [ -x ".git-local-config.sh" ]; then
    echo -e "${GREEN}✅${NC} Setup script: .git-local-config.sh (executable)"
else
    echo -e "${YELLOW}⚠️${NC} Setup script: Missing or not executable"
fi

# Check for fix script
if [ -f ".fix-commit-authors.sh" ] && [ -x ".fix-commit-authors.sh" ]; then
    echo -e "${GREEN}✅${NC} Fix script: .fix-commit-authors.sh (executable)"
else
    echo -e "${YELLOW}⚠️${NC} Fix script: Missing or not executable"
fi

# Check for documentation
if [ -f "GIT_CONFIGURATION.md" ]; then
    echo -e "${GREEN}✅${NC} Documentation: GIT_CONFIGURATION.md"
else
    echo -e "${YELLOW}⚠️${NC} Documentation: Missing"
fi

# Check for commit template
if [ -f ".gitmessage" ]; then
    echo -e "${GREEN}✅${NC} Commit template: .gitmessage"
    TEMPLATE_CONFIG=$(git config --local commit.template)
    if [ "$TEMPLATE_CONFIG" = ".gitmessage" ]; then
        echo -e "${GREEN}✅${NC} Template configured: Yes"
    else
        echo -e "${YELLOW}⚠️${NC} Template configured: No (optional)"
    fi
else
    echo -e "${YELLOW}⚠️${NC} Commit template: Missing (optional)"
fi

echo ""
echo "4. Recent Commits Check"
echo "-----------------------"

# Show last 3 commits' authors
echo "Last 3 commits:"
git log --format="  %h %an <%ae>" -3

echo ""
echo "5. Global Configuration Check"
echo "-----------------------------"

GLOBAL_NAME=$(git config --global user.name 2>/dev/null || echo "Not set")
GLOBAL_EMAIL=$(git config --global user.email 2>/dev/null || echo "Not set")

echo "Global user.name: $GLOBAL_NAME"
echo "Global user.email: $GLOBAL_EMAIL"

if [ "$GLOBAL_NAME" = "$EXPECTED_NAME" ] && [ "$GLOBAL_EMAIL" = "$EXPECTED_EMAIL" ]; then
    echo -e "${YELLOW}⚠️${NC} Note: Global config matches local - this may affect other repos"
else
    echo -e "${GREEN}✅${NC} Global config is different (good - won't affect other repos)"
fi

echo ""
echo "========================================="
if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}✅ Configuration is VALID${NC}"
    echo "All critical settings are correctly configured."
else
    echo -e "${RED}❌ Configuration needs attention${NC}"
    echo "Run ./.git-local-config.sh to fix configuration"
fi
echo "========================================="

# Exit with appropriate code
if [ "$ALL_GOOD" = true ]; then
    exit 0
else
    exit 1
fi