#!/usr/bin/env python3
"""
Extract collections and notification channels from existing bigconfig.yml files.

This script scans the sql/ directory for bigconfig.yml files and extracts:
- Collection names
- Notification channels (Slack, email)
- Usage frequency by dataset/product area

Output is written to references/existing_collections.md for Claude to reference.
"""

import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

import yaml


def extract_collections_from_bigconfig(bigconfig_path: Path) -> List[Dict]:
    """Extract collection info from a single bigconfig.yml file."""
    try:
        with open(bigconfig_path, "r") as f:
            config = yaml.safe_load(f)

        if not config:
            return []

        collections = []

        # Check tag_deployments
        for deployment_suite in config.get("tag_deployments", []):
            collection = deployment_suite.get("collection")
            if collection:
                collections.append({
                    "name": collection.get("name"),
                    "notification_channels": collection.get("notification_channels", []),
                    "path": str(bigconfig_path.parent.relative_to(bigconfig_path.parents[3])),
                })

        # Check table_deployments
        for deployment_suite in config.get("table_deployments", []):
            collection = deployment_suite.get("collection")
            if collection:
                collections.append({
                    "name": collection.get("name"),
                    "notification_channels": collection.get("notification_channels", []),
                    "path": str(bigconfig_path.parent.relative_to(bigconfig_path.parents[3])),
                })

        return collections

    except Exception as e:
        print(f"Error processing {bigconfig_path}: {e}", file=sys.stderr)
        return []


def aggregate_collections(sql_dir: Path) -> Dict:
    """Scan all bigconfig.yml files and aggregate collection data."""
    collection_data = defaultdict(lambda: {
        "count": 0,
        "channels": set(),
        "datasets": set(),
        "tables": []
    })

    # Find all bigconfig.yml files
    bigconfig_files = list(sql_dir.rglob("bigconfig.yml"))

    print(f"Found {len(bigconfig_files)} bigconfig.yml files", file=sys.stderr)

    for bigconfig_path in bigconfig_files:
        collections = extract_collections_from_bigconfig(bigconfig_path)

        for collection in collections:
            if not collection["name"]:
                continue

            name = collection["name"]
            collection_data[name]["count"] += 1

            # Extract dataset from path (format: project/dataset/table)
            path_parts = collection["path"].split("/")
            if len(path_parts) >= 2:
                dataset = path_parts[1]
                collection_data[name]["datasets"].add(dataset)

            collection_data[name]["tables"].append(collection["path"])

            # Extract notification channels
            for channel in collection["notification_channels"]:
                if isinstance(channel, dict):
                    if "slack" in channel:
                        collection_data[name]["channels"].add(f"slack:{channel['slack']}")
                    if "email" in channel:
                        collection_data[name]["channels"].add(f"email:{channel['email']}")

    # Convert sets to sorted lists for output
    for name in collection_data:
        collection_data[name]["channels"] = sorted(list(collection_data[name]["channels"]))
        collection_data[name]["datasets"] = sorted(list(collection_data[name]["datasets"]))

    return dict(collection_data)


def generate_markdown_reference(collection_data: Dict, output_path: Path):
    """Generate a markdown reference file for Claude to use."""

    # Sort by usage count (most used first)
    sorted_collections = sorted(
        collection_data.items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )

    with open(output_path, "w") as f:
        f.write("# Existing Bigeye Collections\n\n")
        f.write("This file is auto-generated from existing bigconfig.yml files.\n")
        f.write("Use this to guide users toward consistent collection naming and notification channels.\n\n")
        f.write(f"**Last updated:** Run `./scripts/extract_collections.py` to refresh\n\n")
        f.write("---\n\n")

        f.write("## Most Common Collections\n\n")

        for name, data in sorted_collections[:10]:  # Top 10
            f.write(f"### {name}\n\n")
            f.write(f"- **Usage:** {data['count']} tables\n")
            f.write(f"- **Datasets:** {', '.join(data['datasets']) if data['datasets'] else 'Various'}\n")

            if data['channels']:
                f.write(f"- **Notification Channels:**\n")
                for channel in data['channels']:
                    f.write(f"  - `{channel}`\n")
            else:
                f.write(f"- **Notification Channels:** None configured\n")

            f.write("\n")

        f.write("---\n\n")
        f.write("## All Collections\n\n")
        f.write("| Collection Name | Usage Count | Datasets | Channels |\n")
        f.write("|----------------|-------------|----------|----------|\n")

        for name, data in sorted_collections:
            datasets_str = ", ".join(data['datasets'][:3])
            if len(data['datasets']) > 3:
                datasets_str += f" (+{len(data['datasets']) - 3} more)"

            channels_str = f"{len(data['channels'])} configured"

            f.write(f"| {name} | {data['count']} | {datasets_str} | {channels_str} |\n")

        f.write("\n")
        f.write("---\n\n")
        f.write("## Guidance for New Monitoring\n\n")
        f.write("**When adding monitoring to a new table:**\n\n")
        f.write("1. **Check the dataset** - If your dataset appears above, use the existing collection\n")
        f.write("2. **Check the team** - Look for collections related to your team/product\n")
        f.write("3. **Match notification channels** - Use the same channels as similar tables\n")
        f.write("4. **Create new collection** - Only if none of the above apply\n\n")

        # Group by dataset
        dataset_collections = defaultdict(set)
        for name, data in collection_data.items():
            for dataset in data['datasets']:
                dataset_collections[dataset].add(name)

        f.write("### Collections by Dataset\n\n")
        for dataset in sorted(dataset_collections.keys())[:20]:  # Top 20 datasets
            collections = sorted(dataset_collections[dataset])
            f.write(f"- **{dataset}:** {', '.join(collections)}\n")


def main():
    """Main execution."""
    # Find sql directory (go up from script location)
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    repo_root = skill_dir.parent.parent.parent

    sql_dir = repo_root / "bigquery-etl" / "sql"

    if not sql_dir.exists():
        # Try alternative path
        sql_dir = repo_root / "sql"

    if not sql_dir.exists():
        print(f"Error: Could not find sql directory at {sql_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {sql_dir} for bigconfig.yml files...", file=sys.stderr)

    # Extract collection data
    collection_data = aggregate_collections(sql_dir)

    print(f"Found {len(collection_data)} unique collections", file=sys.stderr)

    # Generate reference file
    output_path = skill_dir / "references" / "existing_collections.md"
    output_path.parent.mkdir(exist_ok=True)

    generate_markdown_reference(collection_data, output_path)

    print(f"✓ Reference file created: {output_path}", file=sys.stderr)
    print(f"✓ Found {len(collection_data)} collections across {sum(d['count'] for d in collection_data.values())} tables")


if __name__ == "__main__":
    main()
