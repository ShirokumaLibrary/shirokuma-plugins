# Manual Setup Steps

Step-by-step guide for GitHub Projects V2 initial configuration, from project creation to all required settings.

## Create the Project (Web UI)

**Web UI creation is recommended** because the GitHub API cannot enable workflows after project creation. Web UI creation enables workflows (Item closed→Done, etc.) by default.

**Steps:**
1. Navigate to `https://github.com/orgs/{org}/projects/new` (Organization) or open the "Projects" tab in your repository and click "New project"
2. Choose a template:
   - **"Blank project"**: Full manual configuration
   - **"Team planning"**: Includes pre-configured views (Backlog/Ready/In progress/In review/Done)
3. Set a title and click "Create project"

**Workflows enabled by default after Web UI creation:**

| Workflow | Behavior |
|----------|----------|
| Item closed | Sets Status → Done when issue is closed |
| Pull request merged | Sets Status → Done when PR is merged |
| Auto-close issue | Closes issue when Status is set to Done |

After creation, link the repository and configure fields via CLI:

```bash
shirokuma-docs project setup --lang=en
```

## Issue Types Configuration

Add custom Issue Types to the Organization.

**Steps:**
1. Navigate to `https://github.com/organizations/{org}/settings/issue-types`
2. Click "Create new type" to add:

| Type | Purpose | Color | Icon |
|------|---------|-------|------|
| Chore | Config, tooling, refactoring | Gray | gear |
| Docs | Documentation | Green | page facing up |
| Research | Investigation and research | Purple | magnifying glass |
| Evolution | Rule/skill evolution signals and improvement tracking | Pink | seedling |

## Discussion Category Creation

**Steps:**
1. Navigate to `https://github.com/{owner}/{repo}/discussions/categories`
2. Create the following 4 categories:

| Category | Emoji Search | Color | Format |
|----------|-------------|-------|--------|
| Handovers | handshake | Purple | Open-ended discussion |
| ADR | triangular ruler | Blue | Open-ended discussion |
| Knowledge | light bulb | Yellow | Open-ended discussion |
| Research | microscope | Green | Open-ended discussion |

**Important**: Format must be **Open-ended discussion**.

## Verify Built-in Automations

When created via Web UI, the following workflows are **enabled by default**. Verify and adjust as needed in the Settings page.

**Steps:**
1. Navigate to `https://github.com/orgs/{owner}/projects/{number}/workflows` (or Project → Settings → Workflows)
2. Verify the following states:

| Workflow | Recommended | Default (Web UI creation) |
|----------|-------------|--------------------------|
| Item closed | **Enabled** | Enabled — no change needed |
| Pull request merged | **Enabled** | Enabled — no change needed |
| Auto-close issue | **Enabled** | Enabled — no change needed |
| Item added to project | Disabled | Disabled — Status managed by CLI |
| Item reopened | Disabled | Disabled — manual decision per case |
| Auto-archive items | Disabled | Disabled — makes Done item history hard to access |

> **Note**: If the project was created via API (`projects create-project`), workflows default to disabled and must be manually enabled.

## Rename Views

**Steps:**
1. Open the Project page
2. Double-click View tab → Rename:

| Layout | Recommended Name |
|--------|-----------------|
| TABLE | Board |
| BOARD | Kanban |
| ROADMAP | Roadmap |
