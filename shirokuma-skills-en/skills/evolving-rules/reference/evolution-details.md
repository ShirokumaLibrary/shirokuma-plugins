# Evolution Details

Supplementary details for the `rule-evolution` rule. Covers eval data reference, Evolution Issue lifecycle, auto-recording procedure at skill completion, and standalone signal recording.

## Eval Data Reference

When `evolving-rules` analyzes skills, eval data provides quantitative signals:

```bash
# Check saved eval results
ls .shirokuma/evals/{skill-name}/

# Read latest eval result
cat .shirokuma/evals/{skill-name}/eval_*.json | tail -1
```

Eval failure signals to record:
- Trigger rate < 50% for should_trigger queries → description too narrow
- Trigger rate > 50% for should_not_trigger queries → description too broad
- Consistent failures for specific query patterns → missing description keywords

## Evolution Issue Lifecycle

One analysis cycle corresponds to one Evolution Issue. After analysis, the Issue is closed to prevent re-reading stale signals in subsequent invocations.

```
Open → Accumulate signals → Analyze (evolving-rules) → Close → New Issue for next cycle
```

| Phase | State | Action |
|-------|-------|--------|
| Signal accumulation | Open | Auto-recording at skill completion, manual recording |
| Analysis triggered | Open | `evolving-rules` reads and processes all comments |
| Analysis complete | Closed | `evolving-rules` Step 7 closes the Issue after posting summary |
| New signals after close | — | New Evolution Issue is created automatically (auto-recording flow) |

**Rules:**
- Do not reopen a closed Evolution Issue — create a new one instead
- `evolving-rules` always operates on the most recent **open** Evolution Issue
- Closing ensures that previously analyzed signals are not re-processed

## Standard Search & Creation Flow

Standard flow for searching and creating Evolution Issues. Auto-recording and standalone recording procedures reference this flow.

### `--limit` Value Standards

| Use Case | `--limit` Value | Rationale |
|----------|----------------|-----------|
| Auto-recording (skill completion) | 1 | Latest 1 OPEN issue is sufficient |
| Standalone recording | 1 | Same as above |
| `evolving-rules` analysis phase | 10 | Cross-analyze signals across multiple Issues |

### Flow

```
Search (--limit 1) → Check results
  ├─ 1+ found → Use the most recent OPEN Issue
  └─ 0 found → Create a new Evolution Issue
```

### Search Command

```bash
shirokuma-docs issues list --issue-type Evolution --limit 1
```

### Body Template for New Issues

If 0 issues found, write the following to `/tmp/shirokuma-docs/evolution.md` and create via `issues create --from-file`:

```markdown
---
title: "[Evolution] Evolution Signals"
issueType: Evolution
priority: Low
size: XS
---

## Purpose

Accumulate improvement signals for rules and skills, serving as input for `/evolving-rules` analysis.

## Signals

(Accumulated via auto-recording at skill completion)
```

## Auto-Recording Procedure at Skill Completion

At the completion of major skills (`implement-flow`, `prepare-flow`, `creating-item`, `design-flow`, `review-flow`), auto-record Evolution signals detected during the session using the following procedure. Each skill references this section to perform auto-recording.

### Signal Detection Checklist

Self-check the following at skill completion. When in doubt, do not record (avoid false positives).

#### Introspection Checks (All Target Skills)

| Check Item | Signal Type | Detect (examples) | Do NOT detect (examples) |
|-----------|------------|-------------------|--------------------------|
| Did the user correct or override rule-based behavior? | Rule friction | User overrides commit message language rule | Typo correction request (not a rule issue) |
| Did the user instruct output redo? | Redo instruction | "PR body format is wrong, match the template" | "Add more detail" (normal quality improvement) |
| Did unexpected obstacles or workarounds occur? | Missing pattern | Fallback execution due to unsupported CLI option | Taking time to understand unfamiliar file structure (normal exploration) |
| Did the same pattern of issue repeat during the session? | Review pattern | Same type of self-review finding appeared 2+ times | Sequential fixes of different types (not repetition) |

#### Environment Checks (`implement-flow`, `review-flow` only)

At the completion of skills involving code changes, verify the project's objective state. `prepare-flow` / `creating-item` / `design-flow` do not involve code changes and are excluded.

| Check Item | Signal Type | Detection Condition | Do NOT Record |
|-----------|------------|-------------------|---------------|
| Check `shirokuma-docs lint tests -p . --format json` result | Lint trend | `errorCount > 0`: always flag | `warningCount` only: report count only (no threshold) |

> **Note:** Use `shirokuma-docs lint all -p .` for running all lint types at once. However, environment checks require `--format json` parsing, so `lint tests` is run individually here.

**lint tests execution:**

```bash
shirokuma-docs lint tests -p . --format json 2>/dev/null
```

- `summary.errorCount > 0`: Record as Evolution signal + propose follow-up Issue creation
- `summary.warningCount`: Report count (no hardcoded threshold)
- Command failure: Skip (environment checks are best-effort)

### Auto-Recording Flow

```
Skill completion → Introspection checks → Environment checks (implement-flow only)
  ├─ Signals detected → Search Evolution Issue → Post comment → Display 1-line recording confirmation
  └─ No signals → Check accumulated signals → Display reminder (fallback)
```

#### When Signals Are Detected

1. Follow the "Standard Search & Creation Flow" to secure an Evolution Issue (search → create if 0 found)
2. Post signals as a comment (consolidate multiple signals into 1 comment):
   ```bash
   shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-signal.md
   ```
3. Display 1-line recording confirmation:
   > 🧬 Evolution signal recorded ({type}: {target}).

#### When No Signals Are Detected (Fallback)

Use the "Standard Search & Creation Flow" search command to check for accumulated signals and display a reminder:

- 0 issues → display nothing
- 1+ issues → display one line:

> 🧬 Evolution signals are accumulated. Run `/evolving-rules` to analyze.

### Constraints

- Maximum 1 comment per skill completion (consolidate multiple signals)
- Do not register as a task (non-blocking processing)
- Self-review uses concise checklist format to minimize context consumption
- When no signals detected, minimize CLI command execution (`issues list` once only)
- When `creating-item` creates an item with Issue Type Evolution, skip the entire signal recording (the Evolution Issue itself is an improvement proposal, preventing duplicate recording)

## Standalone Signal Recording

Signals can be recorded even without a session (standalone skill invocations, direct edits, etc.).

### Use Cases

| Use Case | Signal Type | Recording Method |
|----------|------------|-----------------|
| Standalone `/implement-flow` | Rule friction, redo instruction | Recording template + reminder. Include Issue number in **Context** |
| Standalone `/prepare-flow` | Rule friction, skill improvement | Recording template + reminder. Include rule/skill name in **Target** |
| Standalone `/creating-item` | Skill improvement | Recording template + reminder. Include improvement idea in **Proposal** |
| Direct file editing & commit | Rule friction | See recording template. Include rule name in **Target** |
| Review-only short sessions | Review pattern | Reports accumulation (existing). Include pattern improvement in **Proposal** |
| Lint result review | Lint violation trend | See recording template. Include violation count trends in **Context** |

### Recording Template

Follow the "Standard Search & Creation Flow" to secure an Evolution Issue, then post signals as a comment:

```bash
# 1. Secure Evolution Issue (follow Standard Search & Creation Flow)
shirokuma-docs issues list --issue-type Evolution --limit 1
# → If 0 found, create new (see body template in "Standard Search & Creation Flow")

# 2. Post signal as comment
shirokuma-docs items add comment {issue-number} --file /tmp/shirokuma-docs/{issue-number}-signal.md
```

When a reminder is displayed at skill completion, copy and use the template above.
