#!/bin/bash

# Consolidation script for .claude directories
# Applies DRY/SSOT principles by keeping the most recent/complete versions

echo "=== La Factoria .claude Directory Consolidation ==="
echo "Consolidating duplicate .claude directories into single SSOT"
echo ""

ROOT_CLAUDE="/Users/smenssink/Developer/la-factoria-content-factory/.claude"
BANGUI_CLAUDE="/Users/smenssink/Developer/la-factoria-content-factory/.conductor/bangui/.claude"
BACKUP_DIR="/Users/smenssink/Developer/la-factoria-content-factory/.conductor/bangui/backup_claude_$(date +%Y%m%d_%H%M%S)"

# Create backup
echo "1. Creating backup of both .claude directories..."
mkdir -p "$BACKUP_DIR"
cp -r "$ROOT_CLAUDE" "$BACKUP_DIR/root_claude_backup"
cp -r "$BANGUI_CLAUDE" "$BACKUP_DIR/bangui_claude_backup"
echo "   Backup created at: $BACKUP_DIR"

# Files to copy from bangui to root (more recent/complete)
echo ""
echo "2. Updating files with more recent versions from bangui..."

# Copy the more recent git_commit_patterns.md (has Phase 3C learnings)
echo "   - Copying git_commit_patterns.md (Phase 3C anti-patterns)..."
cp "$BANGUI_CLAUDE/memory/git_commit_patterns.md" "$ROOT_CLAUDE/memory/git_commit_patterns.md"

# Copy validation files that only exist in bangui
if [ -f "$BANGUI_CLAUDE/validation/agent-2.3-completion-report.md" ]; then
    echo "   - Copying agent-2.3-completion-report.md..."
    cp "$BANGUI_CLAUDE/validation/agent-2.3-completion-report.md" "$ROOT_CLAUDE/validation/"
fi

if [ -f "$BANGUI_CLAUDE/validation/import-chain-analysis.md" ]; then
    echo "   - Copying import-chain-analysis.md..."
    cp "$BANGUI_CLAUDE/validation/import-chain-analysis.md" "$ROOT_CLAUDE/validation/"
fi

# Compare and update architecture files
echo ""
echo "3. Comparing architecture files..."
if [ -f "$BANGUI_CLAUDE/architecture/project-overview.md" ]; then
    BANGUI_SIZE=$(stat -f%z "$BANGUI_CLAUDE/architecture/project-overview.md" 2>/dev/null || stat -c%s "$BANGUI_CLAUDE/architecture/project-overview.md" 2>/dev/null)
    ROOT_SIZE=$(stat -f%z "$ROOT_CLAUDE/architecture/project-overview.md" 2>/dev/null || stat -c%s "$ROOT_CLAUDE/architecture/project-overview.md" 2>/dev/null)
    
    if [ "$BANGUI_SIZE" -gt "$ROOT_SIZE" ]; then
        echo "   - Updating project-overview.md (bangui version is larger)..."
        cp "$BANGUI_CLAUDE/architecture/project-overview.md" "$ROOT_CLAUDE/architecture/project-overview.md"
    else
        echo "   - Keeping root version of project-overview.md"
    fi
fi

# Update indexes if bangui version is more recent
echo ""
echo "4. Checking index files..."
BANGUI_INDEX_DATE=$(stat -f%m "$BANGUI_CLAUDE/indexes/master-context-index.md" 2>/dev/null || stat -c%Y "$BANGUI_CLAUDE/indexes/master-context-index.md" 2>/dev/null)
ROOT_INDEX_DATE=$(stat -f%m "$ROOT_CLAUDE/indexes/master-context-index.md" 2>/dev/null || stat -c%Y "$ROOT_CLAUDE/indexes/master-context-index.md" 2>/dev/null)

if [ "$BANGUI_INDEX_DATE" -gt "$ROOT_INDEX_DATE" ]; then
    echo "   - Updating master-context-index.md (bangui version is more recent)..."
    cp "$BANGUI_CLAUDE/indexes/master-context-index.md" "$ROOT_CLAUDE/indexes/master-context-index.md"
else
    echo "   - Keeping root version of master-context-index.md"
fi

echo ""
echo "5. Consolidation complete!"
echo ""
echo "Next steps:"
echo "1. Review consolidated .claude directory at: $ROOT_CLAUDE"
echo "2. Delete duplicate bangui .claude directory: rm -rf $BANGUI_CLAUDE"
echo "3. Update all references to point to root .claude directory"
echo "4. Test context loading with /memory command"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "To restore if needed:"
echo "  cp -r $BACKUP_DIR/root_claude_backup/* $ROOT_CLAUDE/"
echo "  cp -r $BACKUP_DIR/bangui_claude_backup/* $BANGUI_CLAUDE/"