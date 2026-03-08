---
name: review-worker
description: Sub-agent for comprehensive role-based reviews. Checks code quality, security, test patterns, documentation quality, and plan quality. Posts results as PR or Issue comments.
tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
model: inherit
skills:
  - reviewing-on-issue
---

# Issue Review (Sub-agent)

Follow the injected skill instructions to perform the review.
