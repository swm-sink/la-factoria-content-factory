#!/bin/bash
# La Factoria Validation Commands - Manual Use
# These commands are available for on-demand validation, not blocking commits

# Full system validation
alias validate="python3 .claude/validation/scripts/validate_system.py"

# Individual component validation
alias validate-agents="python3 .claude/validation/scripts/validate_agents.py"
alias validate-context="python3 .claude/validation/scripts/validate_context.py"
alias validate-commands="python3 .claude/validation/scripts/validate_commands.py"

# Quick health checks
alias health-check="python3 -m json.tool .claude/settings.json > /dev/null && echo '✅ Claude Code settings valid' || echo '❌ Claude Code settings invalid'"

# Usage examples
echo "📋 La Factoria Validation Commands Available:"
echo ""
echo "🔍 Full validation:     validate"
echo "🤖 Agents only:        validate-agents"
echo "📄 Context only:       validate-context"
echo "⚡ Commands only:      validate-commands"
echo "💚 Health check:       health-check"
echo ""
echo "💡 These are now optional - use when needed, not blocking commits"
echo ""
echo "To add to your shell, run:"
echo "source .claude/validation-commands.sh"
