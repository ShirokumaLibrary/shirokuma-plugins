---
name: commit-worker
description: Sub-agent for staging, committing, and pushing changes. Operates as part of the working-on-issue workflow chain.
tools: Bash, Read, Grep, Glob
model: sonnet
skills:
  - committing-on-issue
---

# Commit (Sub-agent)

Follow the injected skill instructions to stage, commit, and push changes.
