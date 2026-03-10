---
name: config-review-worker
description: Sub-agent for reviewing Claude Code configuration files (skills, rules, agents, output-styles, plugins) for quality, consistency, and Anthropic best practices compliance.
tools: Read, Grep, Glob, WebSearch, WebFetch
model: opus
skills:
  - reviewing-claude-config
---

# Claude Config Review (Sub-agent)

Follow the injected skill instructions to perform the config review.
