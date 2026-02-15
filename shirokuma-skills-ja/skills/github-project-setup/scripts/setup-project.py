#!/usr/bin/env python3
"""
GitHub Project Setup Script

Usage:
    python setup-project.py --lang=ja --field-id=FIELD_ID --project-id=PROJECT_ID
    python setup-project.py --lang=en --field-id=FIELD_ID --project-id=PROJECT_ID

To add a new language:
    1. Create locales/{lang}.json
    2. Use --lang={lang}
"""

import subprocess
import json
import argparse
from pathlib import Path

# =============================================================================
# Field Colors (shared across languages)
# =============================================================================

FIELD_COLORS = {
    "status": {
        "Icebox": "GRAY",
        "Backlog": "BLUE",
        "Planning": "PURPLE",
        "Spec Review": "PINK",
        "Ready": "GREEN",
        "In Progress": "YELLOW",
        "Pending": "RED",
        "Review": "PURPLE",
        "Testing": "ORANGE",
        "Done": "GREEN",
        "Not Planned": "GRAY",
        "Released": "GREEN",
    },
    "priority": {
        "Critical": "RED",
        "High": "ORANGE",
        "Medium": "YELLOW",
        "Low": "GRAY",
    },
    "type": {
        "Feature": "GREEN",
        "Bug": "RED",
        "Chore": "GRAY",
        "Docs": "BLUE",
        "Research": "PURPLE",
    },
    "size": {
        "XS": "GRAY",
        "S": "GREEN",
        "M": "YELLOW",
        "L": "ORANGE",
        "XL": "RED",
    },
}

# Date tracking TEXT fields (no options, no locale needed)
DATE_TEXT_FIELDS = [
    "Planning At",
    "Spec Review At",
    "In Progress At",
    "Review At",
    "Completed At",
]

# =============================================================================
# Locale Loading
# =============================================================================

def get_locales_dir() -> Path:
    """Get the locales directory path."""
    return Path(__file__).parent / "locales"


def list_available_languages() -> list[str]:
    """List available language codes from locales directory."""
    locales_dir = get_locales_dir()
    return [f.stem for f in locales_dir.glob("*.json")]


def load_locale(lang: str) -> dict:
    """Load locale file for specified language."""
    locale_file = get_locales_dir() / f"{lang}.json"
    if not locale_file.exists():
        available = list_available_languages()
        raise FileNotFoundError(
            f"Locale '{lang}' not found. Available: {available}"
        )
    with open(locale_file, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# GraphQL Helpers
# =============================================================================

def build_single_select_options(colors: dict, descriptions: dict) -> str:
    """Build singleSelectOptions array for GraphQL."""
    items = []
    for name, color in colors.items():
        desc = descriptions.get(name, name)
        items.append(f'{{name: "{name}", color: {color}, description: "{desc}"}}')
    return "[" + ", ".join(items) + "]"


SUBPROCESS_TIMEOUT = 30


def run_graphql(query: str) -> dict | None:
    """Execute GraphQL query via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={query}"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
        if not result.stdout.strip():
            return None
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        print(f"Error: Command timed out after {SUBPROCESS_TIMEOUT}s")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse response: {e}")
        return None


# =============================================================================
# Setup Functions
# =============================================================================

def setup_status(field_id: str, locale: dict) -> dict | None:
    """Update Status field with localized options."""
    options = build_single_select_options(
        FIELD_COLORS["status"],
        locale["status"]
    )
    query = f"""
    mutation {{
      updateProjectV2Field(input: {{
        fieldId: "{field_id}"
        name: "Status"
        singleSelectOptions: {options}
      }}) {{
        projectV2Field {{
          ... on ProjectV2SingleSelectField {{
            name
            options {{ name description }}
          }}
        }}
      }}
    }}
    """
    return run_graphql(query)


def create_field(project_id: str, name: str, field_key: str, locale: dict) -> dict | None:
    """Create a new single-select field."""
    options = build_single_select_options(
        FIELD_COLORS[field_key],
        locale[field_key]
    )
    query = f"""
    mutation {{
      createProjectV2Field(input: {{
        projectId: "{project_id}"
        dataType: SINGLE_SELECT
        name: "{name}"
        singleSelectOptions: {options}
      }}) {{
        projectV2Field {{
          ... on ProjectV2SingleSelectField {{
            name
            options {{ name }}
          }}
        }}
      }}
    }}
    """
    return run_graphql(query)


def create_text_field(project_id: str, name: str) -> dict | None:
    """Create a new TEXT field for date tracking."""
    query = f"""
    mutation {{
      createProjectV2Field(input: {{
        projectId: "{project_id}"
        dataType: TEXT
        name: "{name}"
      }}) {{
        projectV2Field {{
          ... on ProjectV2Field {{
            name
          }}
        }}
      }}
    }}
    """
    return run_graphql(query)


# =============================================================================
# Main
# =============================================================================

def main():
    available_langs = list_available_languages()

    parser = argparse.ArgumentParser(description="Setup GitHub Project fields")
    parser.add_argument(
        "--lang",
        choices=available_langs,
        default="en",
        help=f"Language for descriptions. Available: {available_langs}"
    )
    parser.add_argument("--field-id", help="Status field ID (for updating)")
    parser.add_argument("--project-id", help="Project ID (for creating new fields)")
    parser.add_argument("--status-only", action="store_true", help="Only update Status field")
    parser.add_argument("--list-langs", action="store_true", help="List available languages")

    args = parser.parse_args()

    if args.list_langs:
        print("Available languages:", available_langs)
        return

    # Load locale
    locale = load_locale(args.lang)
    print(f"Language: {args.lang}")

    if args.field_id:
        print(f"\n[Status] Updating field {args.field_id}...")
        result = setup_status(args.field_id, locale)
        if result:
            print("  ✓ Status updated")

    if args.project_id and not args.status_only:
        for field_name, field_key in [("Priority", "priority"), ("Type", "type"), ("Size", "size")]:
            print(f"\n[{field_name}] Creating field...")
            result = create_field(args.project_id, field_name, field_key, locale)
            if result:
                print(f"  ✓ {field_name} created")

        for field_name in DATE_TEXT_FIELDS:
            print(f"\n[{field_name}] Creating text field...")
            result = create_text_field(args.project_id, field_name)
            if result:
                print(f"  ✓ {field_name} created")

    print("\nDone!")


if __name__ == "__main__":
    main()
