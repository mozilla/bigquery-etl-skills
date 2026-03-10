#!/usr/bin/env python3
"""
Find Column Description

Searches global and application-specific column definition YAML files for a column's
description, type, mode, and aliases.

Usage:
    python scripts/find_column_description.py <column_name>
    python scripts/find_column_description.py <column_name> --dataset <dataset_name>
    python scripts/find_column_description.py <column_name> --all-datasets
    python scripts/find_column_description.py --list-all
    python scripts/find_column_description.py --list-all --dataset <dataset_name>

Examples:
    # Find description from global.yaml only
    python scripts/find_column_description.py submission_date

    # Find description from global + ads_derived.yaml
    python scripts/find_column_description.py clicks --dataset ads_derived

    # Search all available base schema files
    python scripts/find_column_description.py client_id --all-datasets

    # List all columns in global.yaml
    python scripts/find_column_description.py --list-all

    # List all columns in ads_derived.yaml
    python scripts/find_column_description.py --list-all --dataset ads_derived
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


DEFAULT_BASE_SCHEMAS_DIR = "bigquery_etl/schema"


def load_yaml(path: Path) -> Optional[Dict]:
    """Load a YAML file, returning None if not found or invalid."""
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}", file=sys.stderr)
        return None


def find_available_app_schemas(base_schemas_dir: Path) -> List[str]:
    """Return list of available app-specific schema names (app_*.yaml, without extension)."""
    if not base_schemas_dir.exists():
        return []
    return sorted(
        p.stem
        for p in base_schemas_dir.glob("app_*.yaml")
    )


def find_available_dataset_schemas(base_schemas_dir: Path) -> List[str]:
    """Return list of available dataset schema names (without .yaml extension).

    Excludes global.yaml and app_*.yaml files (those are handled separately).
    """
    if not base_schemas_dir.exists():
        return []
    return sorted(
        p.stem
        for p in base_schemas_dir.glob("*.yaml")
        if p.stem != "global" and not p.stem.startswith("app_")
    )


def search_fields(fields: List[Dict], column_name: str, prefix: str = "") -> Optional[Dict]:
    """Recursively search for a column by name or alias in a fields list."""
    for field in fields:
        name = field.get("name", "")
        aliases = field.get("aliases", [])
        full_name = f"{prefix}.{name}" if prefix else name

        if name == column_name or column_name in aliases:
            return {**field, "_matched_as": name, "_full_path": full_name}

        # Search nested fields
        nested = field.get("fields", [])
        if nested:
            result = search_fields(nested, column_name, prefix=full_name)
            if result:
                return result

    return None


def find_column(column_name: str, schema_data: Dict) -> Optional[Dict]:
    """Find a column by name or alias in a schema dict."""
    return search_fields(schema_data.get("fields", []), column_name)


def list_all_columns(schema_data: Dict, prefix: str = "") -> List[Dict]:
    """Recursively list all columns with their descriptions."""
    results = []
    for field in schema_data.get("fields", []):
        name = field.get("name", "")
        full_name = f"{prefix}.{name}" if prefix else name
        results.append({
            "name": full_name,
            "type": field.get("type", ""),
            "mode": field.get("mode", "NULLABLE"),
            "description": field.get("description", ""),
            "aliases": field.get("aliases", []),
        })
        nested = field.get("fields", [])
        if nested:
            results.extend(list_all_columns({"fields": nested}, prefix=full_name))
    return results


def print_match(field: Dict, source: str):
    """Print a matched field in a readable format."""
    print(f"\n{'='*60}")
    print(f"  Column: {field.get('name', '')}")
    print(f"  Source: {source}")
    if field.get("_full_path") and field.get("_full_path") != field.get("name"):
        print(f"  Path:   {field['_full_path']}")
    print(f"  Type:   {field.get('type', 'N/A')}")
    print(f"  Mode:   {field.get('mode', 'NULLABLE')}")
    aliases = field.get("aliases", [])
    if aliases:
        print(f"  Aliases: {', '.join(aliases)}")
    desc = field.get("description", "")
    if desc:
        print(f"  Description: {desc}")
    else:
        print(f"  Description: [MISSING]")
    print(f"{'='*60}")


def print_column_list(columns: List[Dict], source: str):
    """Print all columns from a schema."""
    print(f"\n  Source: {source} ({len(columns)} columns)\n")
    for col in columns:
        desc_preview = col["description"][:60] + "..." if len(col["description"]) > 60 else col["description"]
        desc_str = f'"{desc_preview}"' if desc_preview else "[MISSING]"
        aliases_str = f"  (aliases: {', '.join(col['aliases'])})" if col["aliases"] else ""
        print(f"  {col['name']:<40} {col['type']:<12} {desc_str}{aliases_str}")


def main():
    parser = argparse.ArgumentParser(
        description="Find column descriptions in base schema YAML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "column",
        nargs="?",
        help="Column name to search for (name or alias)",
    )
    parser.add_argument(
        "--dataset",
        help="Dataset-specific schema to search (e.g., ads_derived). Searches global.yaml + this file.",
    )
    parser.add_argument(
        "--all-datasets",
        action="store_true",
        help="Search global.yaml and all available dataset schemas",
    )
    parser.add_argument(
        "--list-all",
        action="store_true",
        help="List all columns in the specified schema(s)",
    )
    parser.add_argument(
        "--base-schemas-dir",
        default=DEFAULT_BASE_SCHEMAS_DIR,
        help=f"Path to base schemas directory (default: {DEFAULT_BASE_SCHEMAS_DIR})",
    )

    args = parser.parse_args()

    if not args.column and not args.list_all:
        parser.print_help()
        sys.exit(1)

    base_dir = Path(args.base_schemas_dir)
    global_path = base_dir / "global.yaml"

    # Build list of schema files to search — priority: app-specific > dataset-specific > global
    schema_files: List[Tuple[str, Path]] = []

    if args.dataset:
        ds_path = base_dir / f"{args.dataset}.yaml"
        ds_data = load_yaml(ds_path)
        if ds_data:
            schema_files.append((f"{args.dataset}.yaml", ds_path, ds_data))
        else:
            print(f"Warning: {args.dataset}.yaml not found at {ds_path}", file=sys.stderr)
    elif args.all_datasets:
        # App-specific schemas come before dataset-specific schemas
        for app_name in find_available_app_schemas(base_dir):
            app_path = base_dir / f"{app_name}.yaml"
            app_data = load_yaml(app_path)
            if app_data:
                schema_files.append((f"{app_name}.yaml", app_path, app_data))
        for ds_name in find_available_dataset_schemas(base_dir):
            ds_path = base_dir / f"{ds_name}.yaml"
            ds_data = load_yaml(ds_path)
            if ds_data:
                schema_files.append((f"{ds_name}.yaml", ds_path, ds_data))

    global_data = load_yaml(global_path)
    if global_data:
        schema_files.append(("global.yaml", global_path, global_data))
    else:
        print(f"Warning: global.yaml not found at {global_path}", file=sys.stderr)

    if not schema_files:
        print(f"Error: No schema files found in {base_dir}", file=sys.stderr)
        print("Make sure you're running from the bigquery-etl repository root.", file=sys.stderr)
        sys.exit(1)

    # LIST MODE
    if args.list_all:
        for source_name, _, schema_data in schema_files:
            columns = list_all_columns(schema_data)
            print_column_list(columns, source_name)
        return

    # SEARCH MODE
    column_name = args.column
    found_any = False

    # Search dataset-specific schema first, then global (priority order)
    for source_name, _, schema_data in schema_files:
        match = find_column(column_name, schema_data)
        if match:
            print_match(match, source_name)
            found_any = True

    if not found_any:
        searched = ", ".join(s for s, _, _ in schema_files)
        print(f"\nColumn '{column_name}' not found in: {searched}")
        print("\nTips:")
        print("  - Check spelling and case (names are case-sensitive)")
        print("  - Try --all-datasets to search all dataset schemas")
        print("  - Column may only exist in a table's schema.yaml, not in base schemas")
        available_app = find_available_app_schemas(base_dir)
        available_ds = find_available_dataset_schemas(base_dir)
        if available_app:
            print(f"\nAvailable app-specific schemas: {', '.join(available_app)}")
        if available_ds:
            print(f"Available dataset schemas: {', '.join(available_ds)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
