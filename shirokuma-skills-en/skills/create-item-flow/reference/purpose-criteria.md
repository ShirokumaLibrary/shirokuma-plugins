# Purpose Clarity Criteria

Based on the JTBD (Jobs-to-be-Done) framework, this document defines how to determine whether a user's message describes a "means" (what to do) versus a "purpose" (why / outcome).

## Means vs Purpose

| | Means (What to do) | Purpose (Why / Outcome) |
|--|-------------------|------------------------|
| Focus | Implementation or operation content | Value delivered to beneficiary |
| Question | "What to do?" | "Who can do what, and why?" |
| Example | "Consolidate the show command" | "Users can navigate a simpler command structure. Current split between show and individual commands causes confusion." |

## Detecting Means Patterns

Statements matching the following patterns are classified as "means."

### Verb Patterns (EN)

| Pattern | Example |
|---------|---------|
| want to fix / fix ... | "I want to fix the bug" |
| want to add / add ... | "Add a --format option" |
| want to consolidate / merge ... | "Consolidate the commands" |
| want to investigate / explore ... | "Investigate the architecture options" |
| want to implement / implement ... | "Implement the feature" |
| want to change / change ... | "Change the interface" |
| want to refactor / refactor ... | "Refactor the code" |
| want to reorganize / clean up ... | "Reorganize the file structure" |
| want to migrate / migrate ... | "Migrate to the new library" |
| want to update / update ... | "Update the dependency" |
| want to remove / remove ... | "Remove the unused code" |

### Contextual Patterns

- Imperative requests without stated outcome: "Please add X to Y"
- Requests that only mention a technical object (file name, command name, API) without explaining why
- "We need to / should ..." constructions without a user benefit stated

## Decision Flow

```
Receive user message
    │
    ▼
Does it match a means pattern?
    │
    ├─ YES → Means detected
    │            │
    │            ▼
    │        Infer purpose (using the following)
    │            - Surrounding conversation context
    │            - Role and function of the target being changed
    │            - Root cause ("why is this means needed?")
    │            │
    │            ▼
    │        Confirm via AskUserQuestion
    │            - Present 2-3 inferred purpose candidates
    │            - Always include "Other (please specify)"
    │
    └─ NO  → Check whether "who, what, why" are present
                 │
                 ├─ All present → Proceed to create Issue
                 └─ Missing    → Present candidates and confirm
```

## Purpose Components

A well-formed purpose contains all three JTBD "Job Statement" elements:

| Element | Description | Example |
|---------|-------------|---------|
| Beneficiary | Who benefits | CLI users, developers, team |
| Expected outcome | What becomes possible | "can do X" |
| Motivation | Why it is needed | "because Y", "so that Z" |

## How to Infer Purpose Candidates

When a means pattern is detected, use this approach to infer purpose candidates:

1. **Understand the role of the target**: What does the command, skill, or file do, and for whom?
2. **Ask "why is this means needed?"**: What is wrong with the current state? What is inconvenient?
3. **Identify the beneficiary**: End user, developer, or team?
4. **Generate multiple hypotheses**: Create 2-3 plausible purposes the user may have intended

## Examples

### Example 1: Command Consolidation

```
User: "The show command and the individual commands are doing similar things.
       I want to consolidate them into the bundled one."

→ Means pattern detected: "want to consolidate"

→ Inferred purpose candidates:
A) "Users can navigate a simpler command structure.
    The current duplication between show and individual commands
    causes confusion about which to use."
B) "Developers can maintain less code while reducing context size.
    Duplicate implementation increases maintenance cost and
    scatters documentation."
C) Other (please specify)
```

### Example 2: Adding an Option

```
User: "Add a --format option to the deps command."

→ Means pattern detected: imperative request without stated outcome

→ Inferred purpose candidates:
A) "CLI users can choose output format based on their use case.
    Currently SVG-only, which is inconvenient for CI or document embedding."
B) "CLI users can get dependency info in JSON format
    for pipeline integration with other tools."
C) Other (please specify)
```

### Example 3: No Means Pattern (Purpose is Clear)

```
User: "Users should be able to start using the CLI without a config file.
       The setup overhead is a barrier to adoption."

→ No means pattern detected (who/what/why is clear)
→ Proceed to Issue creation directly
```

## Preventing Over-Detection

Even when a means pattern matches, skip the confirmation step when the purpose is already sufficiently clear from context:

| Case | Decision |
|------|----------|
| Purpose was already stated in the conversation | Skip confirmation |
| XS size (typo fix, single-line change) | Skip (one-sentence purpose is sufficient) |
| User says "make this an issue" with a prior purpose statement | Skip confirmation |
