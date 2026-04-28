---
name: requirements-flow
description: "Orchestrator for the requirements definition phase at the Discussion level. Does not change Issue status; only searches existing ADRs/Discussions for consistency, delegates ADR creation to write-adr, and creates specification Discussions. Decision rule: if an Issue already exists and its status needs to move forward, use /prepare-flow; if you only need to record a decision at the Discussion level, use /requirements-flow; to simply register a GitHub Issue/Discussion right now, use /create-item-flow. Triggers: \"requirements\", \"requirements definition\", \"create ADR\", \"create spec\", \"define requirements\", \"record architecture decision\", \"technology selection\"."
allowed-tools: Bash, AskUserQuestion, Agent, TaskCreate, TaskUpdate, TaskGet, TaskList
---

!`shirokuma-docs rules inject --scope orchestrator`

# Requirements Definition Phase (Orchestrator)

Orchestrate the requirements definition phase: determine task type from user input, delegate to `requirements-worker` (`write-adr` / specification Discussion creation), and persist the deliverables. **Does not change Issue status (operates at the Discussion level).**

## Task Registration (Required)

Register all chain steps via TaskCreate **before starting work**.

| # | content | activeForm | Method |
|---|---------|------------|--------|
| 1 | Context analysis (task type detection) | Analyzing task type | Manager direct |
| 2 | Search related Discussions | Searching existing Discussions | Bash: `shirokuma-docs discussion adr list` + `discussion search` |
| 3 | Delegate to requirements-worker | Executing ADR creation / spec drafting | Agent: `requirements-worker` |
| 4 | Complete and guide next steps | Creating completion report | Manager direct |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3.

Update each step to `in_progress` at start and `completed` on finish via TaskUpdate.

## Workflow

### Step 1: Context Analysis

Determine the task type from the user's input and conversation context.

#### Routing Determination

| Condition | Route |
|-----------|-------|
| ADR-related keywords ("ADR", "architecture decision", "technology selection", "record decision", "tech choice") | `write-adr` (mode detection delegated to write-adr) |
| Spec-related keywords ("spec", "requirements", "define requirements", "functional requirements", "non-functional requirements") | Specification Discussion creation (Bash: `shirokuma-docs discussion add`) |
| Contains both types of keywords (compound) | `write-adr` then specification Discussion creation, in sequence |
| Cannot determine | Ask via AskUserQuestion |

#### Confirmation When Cannot Determine

```text
AskUserQuestion(
  "What type of requirements work do you need?\n- Create an ADR (Architecture Decision Record)\n- Create a specification Discussion\n- Both"
)
```

### Step 2: Search Related Discussions

Check for duplicates or contradictions with existing ADRs and specs.

```bash
# List existing ADRs
shirokuma-docs discussion adr list

# Search by related keywords
shirokuma-docs discussion search "{keyword}"
```

Include search results in the delegation prompt to requirements-worker for duplicate/contradiction checking.

### Step 3: Delegate to requirements-worker via Agent Tool

Start `requirements-worker` via the Agent tool based on the routing result.

#### ADR Creation Route

```text
Agent(
  description: "requirements-worker ADR",
  subagent_type: "requirements-worker",
  prompt: "Use write-adr to create an ADR.\n\nContext:\n{user input}\n\nRelated Discussions (reference):\n{summary of Step 2 search results}"
)
```

#### Specification Discussion Creation Route

```text
Agent(
  description: "requirements-worker spec",
  subagent_type: "requirements-worker",
  prompt: "Create a specification Discussion.\nRun `shirokuma-docs discussion add` directly via Bash (Ideas category, with [Spec] title prefix).\n\nContext:\n{user input}\n\nRelated Discussions (reference):\n{summary of Step 2 search results}"
)
```

#### Compound Route (ADR + Spec)

```text
Agent(
  description: "requirements-worker ADR+spec",
  subagent_type: "requirements-worker",
  prompt: "Execute the following two tasks in order:\n1. Use write-adr to create an ADR\n2. Run `shirokuma-docs discussion add` directly via Bash to create a specification Discussion (Ideas category, with [Spec] title prefix)\n\nContext:\n{user input}\n\nRelated Discussions (reference):\n{summary of Step 2 search results}"
)
```

#### Post-Completion Handling

If requirements-worker completes successfully, proceed to Step 4. If an error occurs, stop and report to the user.

### Step 4: Completion and Next Steps Guidance

Display a deliverable summary and guide next steps. Follow the `completion-report-style` rule for formatting.

**Required fields**:
- **Created deliverables:** Discussion number + title (ADR / Spec)
- **Type:** ADR / Spec / Compound

**Next steps guidance (by condition)**:

| Condition | Next steps |
|-----------|-----------|
| ADR or spec created | If Issue tracking needed, suggest `/create-item-flow` |
| Related implementation Issue exists | Suggest `/implement-flow` for `#IssueNumber` |
| Standalone (no Issue) | Suggest `create-item-flow` for Issue creation if needed |

## Arguments

| Format | Example | Behavior |
|--------|---------|----------|
| Keyword (ADR/spec) | "Create ADR for authentication approach" | Auto-detect task type and start |
| No argument | — | Ask task type via AskUserQuestion |

## Edge Cases

| Situation | Action |
|-----------|--------|
| Possible duplicate of existing ADR | Include Step 2 search results in delegation prompt; let write-adr decide |
| Spec Discussion Spec category not configured | requirements-worker asks via AskUserQuestion to confirm category |
| User cannot determine | Ask type via AskUserQuestion before delegating |

## No Status Transitions

`requirements-flow` does not manipulate Issues. It is a Discussion-level orchestrator and does not handle Issue status changes. Status management when an Issue exists is the responsibility of the caller (e.g., `implement-flow`).

## Standalone Path

Both `write-adr` and specification Discussion creation can be invoked standalone without going through `requirements-flow`. `requirements-flow` is an orchestrator that routes to these — it does not prevent direct invocation.

## Rule References

| Reference | Usage |
|-----------|-------|
| `output-language` rule | Output language for Discussion body and comments |
| `github-writing-style` rule | Bullet-point vs prose guidelines |
| `completion-report-style` rule | Completion report format |

## Tool Usage

| Tool | When |
|------|------|
| Bash | `shirokuma-docs discussion adr list` / `discussion search` |
| AskUserQuestion | Confirm task type when it cannot be determined |
| Agent (requirements-worker) | Step 3: Delegate ADR creation and spec drafting (subagent, context isolation) |
| TaskCreate, TaskUpdate, TaskGet, TaskList | Progress tracking for all steps |

## Skill Selection Guide

This skill and `create-item-flow` can both create GitHub items, but they serve different purposes.

| Goal | Which skill to use |
|------|-------------------|
| "I want to run the full requirements definition process" / "I want to create an ADR" / "I want to create a spec Discussion" | `requirements-flow` (this skill) |
| "I want to register this conversation as an Issue right now" / "I need a follow-up Issue" | `/create-item-flow` |

**Decision rule**: If the goal is "run the requirements definition / ADR creation process," use `requirements-flow`. If the goal is only "register a GitHub Issue/Discussion right now," use `create-item-flow`.

### Responsibility Boundary with `create-item-flow`

- `requirements-flow` is the **requirements phase orchestrator** — it handles the full pipeline: searching existing ADRs/Discussions for consistency → creating ADRs and spec Discussions → guiding next steps
- `create-item-flow` is the **UI layer** — it immediately registers an Issue/Discussion from the current conversation context. It does not handle the requirements definition process
- Requests like "create a spec" or "write an ADR" should route to this skill. `create-item-flow` does not handle the requirements definition process

## Notes

- This skill is the **orchestrator** — actual ADR creation and specification drafting are delegated to `requirements-worker` via the Agent tool
- **Does not change Issue status** — Discussion-level operations only
- Mode detection for `write-adr` (create / update / supersede) is delegated to the `write-adr` skill itself (requirements-flow does not make this determination)
