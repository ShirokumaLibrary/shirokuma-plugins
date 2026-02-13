#!/bin/bash
set -euo pipefail

# Block destructive git/GitHub commands based on configurable rules.
# Used as a PreToolUse hook for the Bash tool.
#
# Configuration:
#   Default rules:  ${CLAUDE_PLUGIN_ROOT}/hooks/blocked-commands.json
#   Project override: .claude/shirokuma-hooks.json (in project root)
#
# The project override can disable specific rules by ID:
#   { "disabled": ["pr-merge"] }
#
# False-positive prevention:
#   Quoted strings (single and double) are stripped from the command
#   before pattern matching, so text inside --body "..." or similar
#   arguments does not trigger blocks.
#
# Limitation: Commands constructed via eval or variable expansion
# (e.g., cmd="git push --force" && eval "$cmd") are not detected.
# This hook performs string matching on the direct command text only.
#
# Input: JSON on stdin (Claude Code hook format)
# Output: JSON with permissionDecision (deny) or exit 0 (allow)

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Strip quoted strings to avoid false positives on argument values.
# First collapse newlines (multi-line bodies), then remove quoted content.
COMMAND_STRIPPED=$(echo "$COMMAND" | tr '\n' ' ' | sed "s/'[^']*'//g" | sed 's/"[^"]*"//g')

# Locate config files
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
DEFAULT_CONFIG="${PLUGIN_ROOT}/hooks/blocked-commands.json"
PROJECT_CONFIG=".claude/shirokuma-hooks.json"

# Load disabled rule IDs from project override
DISABLED_IDS="[]"
if [ -f "$PROJECT_CONFIG" ]; then
  DISABLED_IDS=$(jq -r '.disabled // []' "$PROJECT_CONFIG" 2>/dev/null || echo "[]")
fi

# Load rules from default config
if [ ! -f "$DEFAULT_CONFIG" ]; then
  # No config found — allow all (fail open)
  exit 0
fi

RULES=$(jq -c '.rules[]' "$DEFAULT_CONFIG" 2>/dev/null) || exit 0

# Check each enabled rule against the stripped command
while IFS= read -r rule; do
  RULE_ID=$(echo "$rule" | jq -r '.id')
  ENABLED=$(echo "$rule" | jq -r '.enabled')
  PATTERN=$(echo "$rule" | jq -r '.pattern')
  REASON=$(echo "$rule" | jq -r '.reason')

  # Skip disabled rules
  if [ "$ENABLED" != "true" ]; then
    continue
  fi

  # Skip rules disabled by project override
  if echo "$DISABLED_IDS" | jq -e --arg id "$RULE_ID" 'index($id) != null' > /dev/null 2>&1; then
    continue
  fi

  # Match against stripped command (no quoted content)
  if echo "$COMMAND_STRIPPED" | grep -qE "$PATTERN"; then
    jq -n --arg reason "$REASON" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: $reason
      }
    }'
    exit 0
  fi
done <<< "$RULES"

# Allow all other commands
exit 0
