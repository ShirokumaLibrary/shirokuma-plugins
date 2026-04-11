---
name: reviewing-security
description: Runs /security-review. Invoked via the finalize-changes skill from implement-flow and review-flow chains. Can also be called directly.
allowed-tools: Bash
---

# Security Review

Skill that runs `/security-review`. Called via the `finalize-changes` skill from `implement-flow` and `review-flow` chains.

!`claude -p '/security-review'`

The above is the security review result. Display the result as-is. If the `claude` command is not available and an error occurred, output a warning and continue.
