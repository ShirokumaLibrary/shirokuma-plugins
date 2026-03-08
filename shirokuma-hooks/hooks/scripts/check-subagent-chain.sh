#!/bin/bash
set -euo pipefail

# Notify the main agent to continue the workflow chain when a subagent completes.
# Used as a SubagentStop hook (Layer 0) to complement the existing Stop hook (Layers 1-2).
#
# The CLI handles:
#   - Resolving the main agent's transcript path from SubagentStop input
#   - Detecting incomplete chain steps (pending/in_progress)
#   - Outputting block JSON to prompt chain continuation
#   - Infinite loop prevention via stop_hook_active check
#
# Input: JSON on stdin (Claude Code SubagentStop hook format)
# Output: JSON with decision: "block" or exit 0 (allow normal return)

# Fail-open: if shirokuma-docs is not available, allow normal return
if ! command -v shirokuma-docs >/dev/null 2>&1; then
  exit 0
fi

# Pipe stdin to CLI for evaluation
# CLI outputs block JSON on incomplete chain, nothing on allow, and always exits 0
shirokuma-docs hooks evaluate-subagent-stop || exit 0
