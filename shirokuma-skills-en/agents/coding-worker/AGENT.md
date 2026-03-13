---
name: coding-worker
description: Sub-agent for general coding tasks. Delegated from working-on-issue, dispatches to framework-specific skills or performs direct edits based on work type.
tools: Read, Write, Edit, Bash, Grep, Glob, Skill, WebSearch, WebFetch
model: sonnet
skills:
  - code-issue
---

# General Coding (Sub-agent)

Follow the injected skill instructions to perform the work.
