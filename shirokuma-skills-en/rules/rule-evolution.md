# Rule & Skill Evolution

## Overview

Apply the closed-loop concept from RLAnything to systematically evolve project-specific rules and skills.

```
Policy execution (daily work) → Reward observation (signal collection) → Policy update (improvement proposals) → Environment adaptation (plugin promotion)
```

## Feedback Signals

| Signal Type | Collection Timing | Example |
|------------|-------------------|---------|
| Rule friction | Anytime | Ignored rule X and manually corrected |
| Redo instruction | Anytime | Had to correct skill Z output |
| Review pattern | PR review | Same feedback pattern 3+ times |
| Lint trend | Lint execution | Rule A violations increasing |
| Task success rate | Session end | Issue completion rate |
| PR merge rate | PR merge | First-review pass rate |

## Signal Persistence

Accumulate signals as comments in Evolution Issues.

| Item | Value |
|------|-------|
| Issue Type | Evolution |
| Emoji | 🧬 |
| Title format | `[Evolution] {topic}` |

**Comment format:**

```markdown
**Type:** {Rule friction | Missing pattern | Skill improvement | Lint trend | Success rate}
**Target:** {rule name or skill name or general}
**Context:** {situation description}
**Proposal:** {improvement suggestion}
```

## Evolution Triggers

| Trigger | Condition | Action |
|---------|-----------|--------|
| Reactive | Same signal accumulated 3+ times | Analyze and propose via `evolving-rules` skill |
| Preventive | Pattern recognized during signal recording | Include proposal in comment |
| Periodic | User explicitly invokes `evolving-rules` | Analyze all accumulated signals |
| Session start | `starting-session` detects accumulated signals | Recommend `evolving-rules` invocation (no auto-execution) |
| Skill completion | `working-on-issue`, `preparing-on-issue`, `creating-item` complete | Auto-record via detection checklist. Display reminder as fallback when no signals detected |
| Eval failure | `skill eval` or `skill optimize` shows failures | Record eval result pattern as evolution signal. Propose description improvement via `evolving-rules` |

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

## Responsibility Boundaries

| Skill | Responsibility | Input |
|-------|---------------|-------|
| `discovering-codebase-rules` | Code patterns → new rule proposals | Codebase analysis |
| `evolving-rules` | Existing rule/skill improvement proposals | Evolution signals |
| `managing-rules` | Rule file creation/update (executor) | Proposal content |

**Ambiguous area:** When `discovering-codebase-rules` detects existing rule deficiencies, record as a comment in an Evolution Issue. `discovering-codebase-rules` itself does not modify rules (new proposals only).

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

## Auto-Recording Procedure at Skill Completion

At the completion of major skills (`working-on-issue`, `preparing-on-issue`, `creating-item`), auto-record Evolution signals detected during the session using the following procedure. Each skill references this section to perform auto-recording.

### Signal Detection Checklist

Self-check the following at skill completion. When in doubt, do not record (avoid false positives).

#### Introspection Checks (All Target Skills)

| Check Item | Signal Type | Detect (examples) | Do NOT detect (examples) |
|-----------|------------|-------------------|--------------------------|
| Did the user correct or override rule-based behavior? | Rule friction | User overrides commit message language rule | Typo correction request (not a rule issue) |
| Did the user instruct output redo? | Redo instruction | "PR body format is wrong, match the template" | "Add more detail" (normal quality improvement) |
| Did unexpected obstacles or workarounds occur? | Missing pattern | Fallback execution due to unsupported CLI option | Taking time to understand unfamiliar file structure (normal exploration) |
| Did the same pattern of issue repeat during the session? | Review pattern | Same type of self-review finding appeared 2+ times | Sequential fixes of different types (not repetition) |

#### Environment Checks (`working-on-issue` only)

At the completion of skills involving code changes, verify the project's objective state. `preparing-on-issue` / `creating-item` do not involve code changes and are excluded.

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
Skill completion → Introspection checks → Environment checks (working-on-issue only)
  ├─ Signals detected → Search Evolution Issue → Post comment → Display 1-line recording confirmation
  └─ No signals → Check accumulated signals → Display reminder (fallback)
```

#### When Signals Are Detected

1. Search for Evolution Issues:
   ```bash
   shirokuma-docs issues list --issue-type Evolution --limit 1
   ```
2. If 0 issues found, create a general-purpose Evolution Issue:
   ```bash
   shirokuma-docs issues create --from-file /tmp/shirokuma-docs/evolution.md
   ```
3. Post signals as a comment (consolidate multiple signals into 1 comment):
   ```bash
   shirokuma-docs issues comment {number} --body-file - <<'EOF'
   **Type:** {type}
   **Target:** {rule name or skill name}
   **Context:** {situation description} (during Issue #{number} work)
   **Proposal:** {improvement suggestion}
   EOF
   ```
4. Display 1-line recording confirmation:
   > 🧬 Evolution signal recorded ({type}: {target}).

#### When No Signals Are Detected (Fallback)

Check for accumulated signals and display a reminder:

```bash
shirokuma-docs issues list --issue-type Evolution --limit 1
```

- 0 issues → display nothing
- 1+ issues → display one line:

> 🧬 Evolution signals are accumulated. Run `/evolving-rules` to analyze.

### Constraints

- Maximum 1 comment per skill completion (consolidate multiple signals)
- Do not register in TodoWrite (non-blocking processing)
- Self-review uses concise checklist format to minimize context consumption
- When no signals detected, minimize CLI command execution (`issues list` once only)
- When `creating-item` creates an item with Issue Type Evolution, skip the entire signal recording (the Evolution Issue itself is an improvement proposal, preventing duplicate recording)

## Standalone Signal Recording

Signals can be recorded even without a session (standalone skill invocations, direct edits, etc.).

### Use Cases

| Use Case | Signal Type | Recording Method |
|----------|------------|-----------------|
| Standalone `/working-on-issue` | Rule friction, redo instruction | Recording template + reminder. Include Issue number in **Context** |
| Standalone `/preparing-on-issue` | Rule friction, skill improvement | Recording template + reminder. Include rule/skill name in **Target** |
| Standalone `/creating-item` | Skill improvement | Recording template + reminder. Include improvement idea in **Proposal** |
| Direct file editing & commit | Rule friction | See recording template. Include rule name in **Target** |
| Review-only short sessions | Review pattern | Reports accumulation (existing). Include pattern improvement in **Proposal** |
| Lint result review | Lint violation trend | See recording template. Include violation count trends in **Context** |

### Recording Template

Command snippet to record signals in Evolution Issues:

```bash
# 1. Find Evolution Issue
shirokuma-docs issues list --issue-type Evolution --limit 5

# 2. Post signal as comment
shirokuma-docs issues comment {issue-number} --body-file - <<'EOF'
**Type:** {Rule friction | Missing pattern | Skill improvement | Lint trend | Success rate}
**Target:** {rule name or skill name or general}
**Context:** {situation description}
**Proposal:** {improvement suggestion}
EOF
```

When a reminder is displayed at skill completion, copy and use the template above.

## Rules

1. **Record signals in Issues** — Accumulate in Evolution Issues, not memory
2. **Respect thresholds** — Trigger analysis at 3+ accumulated signals, no auto-proposals below
3. **Propose cautiously** — Excessive proposals become noise. Reflect DemyAgent's "fewer tool calls are more effective"
4. **No overlap with existing skills** — `discovering-codebase-rules` discovers new patterns, `evolving-rules` improves existing
5. **User approval required** — Apply rule/skill changes only after user confirmation
