#!/bin/bash
# Fix commit authorship for recent commits in La Factoria repository

echo "================================================"
echo "Git Commit Author Fix Script for La Factoria"
echo "================================================"
echo ""
echo "This script will fix the authorship of recent commits."
echo "Current configuration:"
echo "  Name: swm-sink"
echo "  Email: stefan.menssink@gmail.com"
echo ""

# First ensure local config is set
git config --local user.name "swm-sink"
git config --local user.email "stefan.menssink@gmail.com"

echo "Current last 10 commits:"
echo "------------------------"
git log --format="%h %an <%ae>" -10
echo ""

read -p "How many recent commits should be fixed? (Enter number, or 0 to skip): " num_commits

if [ "$num_commits" -eq 0 ]; then
    echo "Skipping commit fix."
    exit 0
fi

echo ""
echo "⚠️  WARNING: This will rewrite git history!"
echo "   - This changes commit hashes"
echo "   - Requires force push if already pushed"
echo "   - Should coordinate with team if branch is shared"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Fixing authorship for last $num_commits commits..."
echo ""

# Fix the commits
git rebase -i HEAD~$num_commits --exec 'git commit --amend --reset-author --no-edit'

echo ""
echo "✅ Done! New commit authors:"
echo "-----------------------------"
git log --format="%h %an <%ae>" -$num_commits
echo ""
echo "To push these changes (if branch was already pushed):"
echo "  git push --force-with-lease origin $(git branch --show-current)"
echo ""
echo "Note: --force-with-lease is safer than --force as it checks for remote changes first."