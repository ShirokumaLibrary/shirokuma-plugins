#!/bin/bash
set -euo pipefail

# Prevent premature stop when workflow chain steps are incomplete.
# Used as a Stop hook to enforce chain autonomous progression.
#
# The CLI handles:
#   - Reading transcript JSONL to find latest TodoWrite
#   - Detecting incomplete chain steps (pending/in_progress)
#   - Outputting block JSON when chain is incomplete
#   - Infinite loop prevention via stop_hook_active check
#
# Input: JSON on stdin (Claude Code Stop hook format)
# Output: JSON with decision: "block" or exit 0 (allow stop)

# Fail-open: if shirokuma-docs is not available, allow stop
if ! command -v shirokuma-docs >/dev/null 2>&1; then
  exit 0
fi

# Pipe stdin to CLI for evaluation
# CLI outputs block JSON on incomplete chain, nothing on allow, and always exits 0
shirokuma-docs hooks evaluate-stop || exit 0
