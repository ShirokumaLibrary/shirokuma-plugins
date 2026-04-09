---
name: design-flow
description: Routes to the appropriate design skill based on design type, managing discovery and visual evaluation loops. Delegates to framework-specific design skills discovered via `skills routing designing`, falling back to `designing-generic` (generic architecture design) when no match is found. Triggers: "design", "UI", "memorable", "impressive", "architecture".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList, Skill, Agent
---

!`shirokuma-docs rules inject --scope orchestrator`

# Design Workflow (Orchestrator)

Route to the appropriate skill based on design type, orchestrating discovery, implementation delegation, and visual evaluation loops. Delegates to framework-specific design skills discovered dynamically via `shirokuma-docs skills routing designing`, falling back to `designing-generic` (generic architecture design) when no match is found.

## Task Registration (Required)

Register all chain steps with TaskCreate **before starting work**.

| # | content | activeForm | Phase |
|---|---------|------------|-------|
| 1 | Route to design skill | Routing to design skill | Phases 1-2 |
| 2 | Execute design | Executing design | Phase 3 |
| 3 | Conduct design review | Conducting design review | Phase 3b |
| 4 | Revise and re-review | Revising and re-reviewing | Phase 3b (conditional: only on NEEDS_REVISION) |
| 5 | Conduct visual evaluation | Conducting visual evaluation | Phase 4 (conditional: only for visual design types) |
| 6 | Update status | Updating status | Phase 5 |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3, step 5 blockedBy 4, step 6 blockedBy 5.

Update each step to `in_progress` at start and `completed` on finish via TaskUpdate. Skip conditional steps (steps 4, 5) when not applicable (mark as `completed` and move to next).

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

### Phase 2: Design Discovery

Establish design direction before writing code.

#### 2a. Create Design Brief

```markdown
## Design Brief

**Purpose**: What problem does this interface solve?
**Context**: Technical constraints, existing design system
**Differentiation**: What makes this UNFORGETTABLE?
```

#### 2b. Reference Design Research (Optional)

Use `WebSearch` to research design references and trends as needed.

#### 2c. Determine Aesthetic Direction

```markdown
## Aesthetic Direction

**Tone**: [Choose ONE]
- Brutally minimal / Maximalist chaos / Retro-futuristic
- Organic/natural / Luxury/refined / Playful/toy-like
- Editorial/magazine / Brutalist/raw / Art deco/geometric

**Typography**: [Font pairing and rationale]
**Color Palette**: [5-7 HEX codes]
**Motion Strategy**: [Key animation moments]
```

#### 2d. User Confirmation

Present design direction via `AskUserQuestion` and obtain approval:

- Design Brief summary
- Aesthetic Direction
- Reference designs (if researched)

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

- Design Brief
- Requirements specific to the design type (from Phase 1 context)
- Technical constraints (framework version, existing patterns, DB engine, etc.)
- Plan section (if available)

### Phase 3b: Post-Skill Completion Handling

Design skills run via Agent tool (`design-worker`). review-issue runs via Agent tool (`review-worker`).

- **Design skills**: If no errors, proceed to Phase 4 (visual evaluation)
- **review-issue (design role)**: Determine result from the `**Review result:**` string in Agent tool (`review-worker`) output. `PASS` → proceed to next step, `NEEDS_REVISION` → return to Phase 3 for revision

### Phase 4: Visual Evaluation Loop

After implementation completes, conduct visual evaluation with user.

**Skip condition**: For non-visual design types (e.g., data model design), skip Phase 4 and proceed directly to Phase 5.

#### 4a. Dev Server Check

```bash
# Check if dev server is running
lsof -i :3000 2>/dev/null || echo "dev server not running"
```

Suggest starting it if needed.

#### 4b. User Review

Present via `AskUserQuestion`:

- List of changed file paths
- Review URL (if dev server is running)
- Review checklist:
  - [ ] Typography is distinctive
  - [ ] Color palette is cohesive
  - [ ] Motion/animation impression
  - [ ] Layout visual interest
  - [ ] Overall impression

Present choices:
1. **Approve** → Proceed to Phase 5
2. **Request changes** → Receive feedback, return to Phase 3
3. **Change direction** → Return to Phase 2

#### 4c. Safety Limit

Visual evaluation loop is limited to **3 iterations maximum**. On reaching the limit, proceed with current state and suggest follow-up Issue for further improvements.

### Phase 5: Completion

Design work is complete once approved. Transition the Issue Status to Review:

```bash
shirokuma-docs items transition {number} --to Review
```

> **Status transition**: When `create-item-flow` determines a design phase is needed via design assessment (`review-issue requirements`), the Issue is handed off from Backlog to `design-flow`. Transitioning unconditionally to Review on `design-flow` completion signals design completion. Skip the update if Status is already Review (idempotent).

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
| AskUserQuestion | Design direction confirmation, visual evaluation loop |
| TaskCreate, TaskUpdate | Phase progress tracking |
| Agent (design-worker) | Delegation to discovered `designing-*` skills (sub-agent, context isolation) |
| WebSearch | Design reference research (optional) |
| Bash | Dev server check, build verification |

## Notes

- Invoked via `/design-flow` from `create-item-flow` completion report (recommended chain after design assessment by `review-issue requirements`)
- Confirm design direction with user before implementation — implementing without alignment risks extensive rework
- Visual evaluation loop limited to 3 iterations maximum
- The delegated design skill handles build verification (not needed in this skill)
