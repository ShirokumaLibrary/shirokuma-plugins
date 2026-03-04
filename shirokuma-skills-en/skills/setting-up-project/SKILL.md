---
name: setting-up-project
description: Runs interactive end-to-end project initial setup including configuration, skill installation, and rule deployment. Triggers: "initial setup", "set up project", "setup project", "new project", "initialize".
allowed-tools: Bash, AskUserQuestion, Read, Write, Glob, TodoWrite
---

# Project Setup

Interactive end-to-end initial setup. Integrates `github-project-setup` and `project-config-generator` functionality.

## Workflow

Track progress with TodoWrite (5 steps).

### Step 1: Repository Check

Detect local/remote repository:

```bash
git remote -v
gh repo view --json name,owner 2>/dev/null
```

| State | Action |
|-------|--------|
| Remote exists | Continue |
| No remote | Suggest `gh repo create` |
| Git not initialized | Suggest `git init` → `gh repo create` |

### Step 2: Config File Generation

Create `shirokuma-docs.config.yaml` interactively via AskUserQuestion:

1. Project type (single app / monorepo)
2. App path (`apps/web`, `.`, etc.)
3. Language setting (Japanese / English)

```bash
shirokuma-docs init --project {path}
```

### Step 3: Plugin Installation

Install skills/rules + language setting:

```bash
shirokuma-docs init --with-skills --project {path}
```

### Step 4: GitHub Projects Setup

**Create the project via Web UI** (recommended over API creation):

1. Navigate to `https://github.com/orgs/{org}/projects/new` (for Organization) or click "New project" from the repository "Projects" tab
2. Choose a template:
   - **"Blank project"**: Configure everything manually
   - **"Team planning"**: Includes initial views (Backlog, Ready, In progress, In review, Done)
3. Set a title and click "Create project" → workflows (Item closed→Done, etc.) are enabled by default

After creation, configure fields automatically:

```bash
shirokuma-docs projects setup --lang={en|ja}
```

Then guide manual setup items:
- Issue Types configuration (requires org admin permissions)
- Discussion category creation
- View renaming

See [docs/manual-steps.md](docs/manual-steps.md) for details.

### Step 5: Project Config Generation

Tech stack detection + skill-specific config directory creation:

```bash
# Execute project-config-generator workflow
Skill: project-config-generator
```

### Verification

Verify all steps complete:

```bash
shirokuma-docs session check --setup
```

## Re-run Support

Detect existing settings at each step:

| Detection | AskUserQuestion Options |
|-----------|------------------------|
| Config exists | Overwrite / Skip / Update |
| Project exists | Skip / Add fields |
| Plugin exists | Update / Skip |

## Reference Documents

| Document | Content | When to Read |
|----------|---------|--------------|
| [reference/setup-checklist.md](reference/setup-checklist.md) | Setup checklist | During setup |
| [docs/manual-steps.md](docs/manual-steps.md) | Manual setup steps | Step 4 |

## Next Steps

```
Setup complete. Next steps:
→ `/working-on-issue` to start your first Issue
→ `/planning-on-issue` to create a plan
```

## Notes

- **`github-project-setup` is deprecated** — use this skill
- Confirm with user before executing each step
- `project-config-generator` maintained as internal utility
