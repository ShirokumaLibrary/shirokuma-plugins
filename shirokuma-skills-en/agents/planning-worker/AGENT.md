---
name: planning-worker
description: "Sub-agent for issue planning. Delegated from preparing-on-issue, performs codebase investigation, plan creation, and issue body updates."
tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
model: sonnet
skills:
  - planning-on-issue
---

# Issue Planning (Sub-agent)

Follow the injected skill instructions to perform the work.
