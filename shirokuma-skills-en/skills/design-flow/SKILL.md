---
name: design-flow
description: Routes to the appropriate design skill based on design type, managing discovery and visual evaluation loops. Delegates to framework-specific design skills discovered via `skills routing designing`, falling back to `designing-generic` (generic architecture design) when no match is found. Triggers: "design", "UI", "memorable", "impressive", "architecture".
allowed-tools: Read, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList, Skill, Agent
---

!`shirokuma-docs rules inject --scope orchestrator`

# Design Workflow (Orchestrator)

Route to the appropriate skill based on design type, orchestrating discovery, implementation delegation, and visual evaluation loops. Delegates to framework-specific design skills discovered dynamically via `shirokuma-docs skills routing designing`, falling back to `designing-generic` (generic architecture design) when no match is found.

## Task Registration (Required)

Register all chain steps with TaskCreate **before starting work**.

| # | content | activeForm | Phase |
|---|---------|------------|-------|
| 1 | Get Issue and update status | Getting Issue and updating status | Phase 1 |
| 2 | Conduct design discovery | Conducting design discovery | Phase 2 |
| 3 | Execute design | Executing design | Phase 3 |
| 4 | Conduct design review | Conducting design review | Phase 3b |
| 5 | Revise and re-review | Revising and re-reviewing | Phase 3b (conditional: only on NEEDS_REVISION) |
| 6 | Conduct visual evaluation | Conducting visual evaluation | Phase 4 (conditional: only for visual design types) |
| 7 | Update status | Updating status | Phase 5 |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3, step 5 blockedBy 4, step 6 blockedBy 5, step 7 blockedBy 6.

Update each step to `in_progress` at start and `completed` on finish via TaskUpdate. Skip conditional steps (steps 5, 6) when not applicable (mark as `completed` and move to next).

## Workflow

### Phase 1: Context Reception

Confirm issue number via `AskUserQuestion` or obtain from arguments. Fetch the issue to understand the plan section and design requirements.

```bash
shirokuma-docs items context {number}
# → Read .shirokuma/github/{org}/{repo}/issues/{number}/body.md
```

| Field | Required | Content |
|-------|----------|---------|
| Issue number | Yes | `#{number}` |
| Plan section | Yes (if exists) | Extracted from `## Plan` in issue body |
| Design requirements | No | Design-related requirements from issue body |

### Phase 1b: Update Status to In Progress

If the Issue status is Backlog, transition to In Progress to record the start of design work.

```bash
shirokuma-docs items transition {number} --to "In Progress"
```

Skip status update if already In Progress / Review (idempotent).

### Phase 2: Design Discovery

Call the `discovering-design` skill via Skill tool. Pass the issue context (design requirements, plan section, technical constraints):

```text
Skill(skill: "discovering-design")
```

`discovering-design` creates the Design Brief, determines Aesthetic Direction, obtains user confirmation, and returns the approved design direction.

### Phase 3: Delegate to Design Skill

#### Skill Discovery (Run Before Dispatch)

First run dynamic discovery to detect project-specific skills:

```bash
shirokuma-docs skills routing designing
```

Refer to the `description` of each entry in the output `routes` array and route to the skill that best matches the issue requirements.

- Entries with `source: "discovered"` / `source: "config"` are **project-specific skills** (higher priority)
- Entries with `source: "builtin"` are built-in skills (same as the dispatch table below)

When a project-specific skill matches the requirements, use it with higher priority. Fall back to the default dispatch table when no discovery result matches.

#### Routing Decision Flow

| Condition | Action |
|-----------|--------|
| `routes.length > 0` | Use discovered skills with priority |
| `routes.length === 0` and fallback table matches | Use skill from fallback dispatch table |
| Neither matches | Delegate to `designing-generic` (generic architecture design) |

#### Dispatch Table (Fallback)

| Design Type | Condition | Route |
|-------------|-----------|-------|
| UI Design | shadcn/ui + Tailwind project, keywords: `UI`, `impressive`, `design` | Agent delegate (design-worker) to discovered `designing-*` UI skill |
| Architecture Design | `area:frontend`, API design, component composition, routing | Agent delegate (design-worker) to discovered `designing-*` architecture skill |
| Data Model Design | DB schema, migrations | Agent delegate (design-worker) to discovered `designing-*` data model skill |
| Generic Architecture Design | CLI tools, libraries, framework-agnostic design (all others) | Agent delegate (design-worker) to `designing-generic` |

#### Delegating to Discovered Design Skills

Invoke the matched design skill via Agent tool (`design-worker`). Pass the following context:

- Design Brief finalized in Phase 2
- Requirements specific to the design type (from Phase 1 context)
- Technical constraints (framework version, existing patterns, DB engine, etc.)
- Plan section (if available)

### Phase 3b: Post-Skill Completion Handling

Design skills run via Agent tool (`design-worker`). analyze-issue runs via Agent tool (`review-worker`).

- **Design skills**: If no errors, proceed to Phase 4 (visual evaluation)
- **analyze-issue (design role)**: Determine result from the `**Review result:**` string in Agent tool (`review-worker`) output. `PASS` → proceed to next step, `NEEDS_REVISION` → return to Phase 3 for revision

### Phase 4: Visual Evaluation Loop

**Skip condition**: For non-visual design types (e.g., data model design), skip Phase 4 and proceed directly to Phase 5.

Call the `evaluating-design` skill via Skill tool. Pass the list of changed file paths:

```text
Skill(skill: "evaluating-design")
```

`evaluating-design` checks the dev server, presents the review checklist, and collects feedback, returning one of the following:

| Result | Next Action |
|--------|------------|
| `APPROVED` | Proceed to Phase 5 |
| `NEEDS_REVISION: {feedback}` | Pass feedback to Agent (`design-worker`) and return to Phase 3 |
| `DIRECTION_CHANGE` | Re-invoke `discovering-design` and return to Phase 2 |

**Iteration management**: The visual evaluation loop is limited to **3 iterations maximum**. This skill (`design-flow`) counts iterations and proceeds directly to Phase 5 without calling `evaluating-design` when the limit is reached. Suggest a follow-up Issue for further improvements.

### Phase 5: Completion

Design work is complete once approved. Transition the Issue Status to Review:

```bash
shirokuma-docs items transition {number} --to Review
```

> **Status transition**: When `create-item-flow` determines a design phase is needed via design assessment (`analyze-issue requirements`), the Issue is handed off from Backlog to `design-flow`. Transitioning unconditionally to Review on `design-flow` completion signals design completion. Skip the update if Status is already Review (idempotent).

## Next Steps

```
Design complete. Next steps:
→ `/prepare-flow #{issue number}` to move to the planning phase (always plan after design)
→ Use `/commit-issue` to commit changes only
```

## Extensibility

Expand delegation to specialized skills per design type:

Design skills are discovered dynamically via `shirokuma-docs skills routing designing`. Any skill following the `designing-{domain}` naming convention is automatically discoverable. See the `coding-claude-config` skill for the discovery mechanism details.

## Tool Usage

| Tool | When |
|------|------|
| AskUserQuestion | Issue number confirmation (Phase 1) |
| TaskCreate, TaskUpdate | Phase progress tracking |
| Skill | `discovering-design` (Phase 2), `evaluating-design` (Phase 4) |
| Agent (design-worker) | Delegation to discovered `designing-*` skills (sub-agent, context isolation) |
| Bash | Skill discovery (Phase 3), status transition (Phase 1b, Phase 5) |

## Notes

- Invoked via `/design-flow` from `create-item-flow` completion report (recommended chain after design assessment by `analyze-issue requirements`)
- `discovering-design` and `evaluating-design` use `AskUserQuestion` and must be called via Skill tool (main context); Agent delegation is not allowed
- Visual evaluation loop limited to 3 iterations maximum
- The delegated design skill handles build verification (not needed in this skill)
