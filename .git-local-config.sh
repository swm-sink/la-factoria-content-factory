#!/bin/bash
# Repository-specific Git Configuration for La Factoria
# This script ensures consistent git attribution for this repository only

echo "Setting up repository-specific git configuration for La Factoria..."

# Set user configuration (local to this repository only)
git config --local user.name "swm-sink"
git config --local user.email "stefan.menssink@gmail.com"

# Additional recommended settings for this repository
git config --local core.autocrlf input  # Ensure consistent line endings
git config --local pull.rebase false    # Merge (not rebase) by default
git config --local commit.gpgsign false # Disable GPG signing for simplicity

# Set up commit template if needed
git config --local commit.template .gitmessage

# Verify configuration
echo ""
echo "✅ Git configuration set for this repository:"
echo "  User: $(git config --local user.name)"
echo "  Email: $(git config --local user.email)"
echo ""
echo "This configuration is LOCAL to this repository only and will NOT affect other projects."
echo ""
echo "To fix authorship on recent commits (if needed), run:"
echo "  git commit --amend --reset-author --no-edit  # For the last commit"
echo "  git rebase -i HEAD~N --exec 'git commit --amend --reset-author --no-edit'  # For last N commits"