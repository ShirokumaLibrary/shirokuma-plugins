---
scope:
  - main
category: github
priority: required
---

# GitHub Discussions Usage

## Purpose

Discussions store human-readable knowledge; Rules store AI-readable extracts.

| Layer | Audience | Language | Content |
|-------|----------|----------|---------|
| Discussions | Human | English | Context, rationale, details |
| Rules/Skills | AI | English | Concise patterns, commands |

## Categories

| Category | Emoji | Format | When to Use |
|----------|-------|--------|-------------|
| ADR | 📐 | Open-ended discussion | Architecture decisions confirmed |
| Knowledge | 💡 | Open-ended discussion | Patterns/solutions confirmed |
| Research | 🔬 | Open-ended discussion | Investigation needed |

> Evolution signals are managed via Issues, not Discussions. See the `rule-evolution` rule for details.

## Workflow

```
Research → ADR (if decision) → Knowledge → Rule extract
```

### Discussion → Issue Flow

Ideas and proposals live in Discussions until a decision is made to implement them.

```
Discussion (idea) → Decision to implement → Issue (Backlog) → Ready → In Progress
```

| Action | When |
|--------|------|
| Create Discussion | New idea, proposal, or investigation topic |
| Convert to Issue | Team decides to implement the idea |
| Keep as Discussion | Idea is rejected, deferred, or purely informational |

Do NOT create Issues for undecided ideas. Use Discussions for exploration and decision-making first.

## AI Behavior

1. **Search**: Run `shirokuma-docs items discussions search "{keyword}"` or `shirokuma-docs items search --type discussions "{keyword}"` before creating new ones
2. **Read**: Check Discussions for context when researching
3. **Write**: Create Discussions for significant findings
4. **Extract**: Propose Rule via `managing-rules` skill when pattern is confirmed
5. **Body maintenance**: After posting a comment, update the body as consolidated version (see `project-items` rule)

Knowledge→Rule extraction workflow and search command details are auto-loaded when the `managing-github-items` skill is executed.

> Do NOT write detailed information in Auto Memory. Memory is for pointers only; record details in Discussions (see `memory-operations` rule).

## Title Formats

| Category | Format |
|----------|--------|
| ADR | `ADR-{NNN}: {title}` |
| Knowledge | `{Topic Name}` |
| Research | `[Research] {topic}` |
