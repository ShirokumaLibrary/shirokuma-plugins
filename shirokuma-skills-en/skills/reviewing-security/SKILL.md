---
name: reviewing-security
description: Runs /security-review. Invoked from the implement-flow chain. Can also be called directly.
allowed-tools: Bash
---

# Security Review

Skill that runs `/security-review`. Called as step 5 in the `implement-flow` chain.

!`claude -p '/security-review'`

The above is the security review result. Display the result as-is. If the `claude` command is not available and an error occurred, output a warning and continue.
