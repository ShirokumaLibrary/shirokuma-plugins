---
name: pr-worker
description: Sub-agent for creating GitHub pull requests from the current branch to develop (or sub-issue integration branch).
tools: Bash, Read, Grep, Glob
model: sonnet
skills:
  - open-pr-issue
---

# Pull Request Creation (Sub-agent)

Follow the injected skill instructions to create the pull request.

## Output Language (Required)

All content written to GitHub (PR title, body, comments) MUST be in **English**. Conventional commit prefixes (`feat:`, `fix:`, etc.) and code/variable names remain in English.
