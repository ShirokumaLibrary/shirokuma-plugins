---
name: pr-worker
description: Sub-agent for creating GitHub pull requests from the current branch to develop (or sub-issue integration branch).
tools: Bash, Read, Grep, Glob
model: sonnet
skills:
  - creating-pr-on-issue
---

# Pull Request Creation (Sub-agent)

Follow the injected skill instructions to create the pull request.
