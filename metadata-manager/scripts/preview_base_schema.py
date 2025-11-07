#!/usr/bin/env python3
"""
Preview Base Schema Matching

Shows which fields in a query's schema would match base schemas (global.yaml or dataset.yaml)
before running `./bqetl query schema update --use-global-schema` or `--use-dataset-schema`.

Usage:
    python scripts/preview_base_schema.py <table_identifier>
    python scripts/preview_base_schema.py <table_identifier> --dataset-schema
    python scripts/preview_base_schema.py <table_identifier> --global-schema
    python scripts/preview_base_schema.py <table_identifier> --both

Examples:
    # Preview global schema matches
    python scripts/preview_base_schema.py telemetry_derived.clients_daily_v1

    # Preview dataset-specific schema matches
    python scripts/preview_base_schema.py ads_derived.impressions_v1 --dataset-schema

    # Preview both global and dataset schema matches
    python scripts/preview_base_schema.py ads_derived.impressions_v1 --both

Table identifier formats:
    - dataset.table (e.g., telemetry_derived.clients_daily_v1)
    - project.dataset.table (e.g., moz-fx-data-shared-prod.telemetry_derived.clients_daily_v1)
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import yaml


def parse_table_identifier(identifier: str) -> Dict[str, str]:
    """Parse table identifier into project, dataset, table components."""
    parts = identifier.split(".")

    if len(parts) == 2:
        dataset, table = parts
        project = "moz-fx-data-shared-prod"
    elif len(parts) == 3:
        project, dataset, table = parts
    else:
        raise ValueError(f"Invalid table identifier format: {identifier}")

    return {
        "project": project,
        "dataset": dataset,
        "table": table
    }


def load_schema_file(schema_path: Path) -> Optional[Dict]:
    """Load a YAML schema file."""
    if not schema_path.exists():
        return None

    try:
        with open(schema_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load {schema_path}: {e}", file=sys.stderr)
        return None


def find_query_schema(project: str, dataset: str, table: str, sql_dir: str = "sql") -> Optional[Dict]:
    """Find the schema.yaml file for a query."""
    schema_path = Path(sql_dir) / project / dataset / table / "schema.yaml"

    if not schema_path.exists():
        return None

    return load_schema_file(schema_path)


def find_field_in_base_schema(field_name: str, base_schema: Dict) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Find a field in base schema by name or alias.

    Returns:
        (field_dict, match_type) where match_type is 'name', 'alias', or None
    """
    for field in base_schema.get("fields", []):
        if field_name == field.get("name"):
            return field, "name"
        if field_name in field.get("aliases", []):
            return field, "alias"

    return None, None


def preview_base_schema_matches(
    query_schema: Dict,
    dataset_name: str,
    use_global: bool = True,
    use_dataset: bool = False,
    base_schemas_dir: str = "bigquery_etl/schema"
) -> Dict:
    """
    Preview which fields would be matched by base schemas.

    Returns a dict with:
        - matched_fields: List of (field_name, source, match_type, base_name, description)
        - overwritten_fields: List of (field_name, source, old_desc, new_desc)
        - missing_desc_fields: List of field names with no description
        - alias_recommendations: List of (alias, canonical_name)
    """
    results = {
        "matched_fields": [],
        "overwritten_fields": [],
        "missing_desc_fields": [],
        "alias_recommendations": []
    }

    dataset_schema_path = Path(base_schemas_dir) / f"{dataset_name}.yaml"
    global_schema_path = Path(base_schemas_dir) / "global.yaml"

    # Load base schemas
    dataset_schema = None
    global_schema = None

    if use_dataset and dataset_schema_path.exists():
        dataset_schema = load_schema_file(dataset_schema_path)

    if use_global and global_schema_path.exists():
        global_schema = load_schema_file(global_schema_path)

    # Check each field in query schema
    for field in query_schema.get("fields", []):
        field_name = field["name"]
        field_desc = field.get("description", "").strip()
        found_field = None
        match_type = None
        source = None

        # Try dataset schema first (higher priority)
        if dataset_schema:
            found_field, match_type = find_field_in_base_schema(field_name, dataset_schema)
            if found_field:
                source = f"{dataset_name}.yaml"

        # Fall back to global schema
        if not found_field and global_schema:
            found_field, match_type = find_field_in_base_schema(field_name, global_schema)
            if found_field:
                source = "global.yaml"

        if found_field:
            base_name = found_field["name"]
            base_desc = found_field.get("description", "").strip()

            results["matched_fields"].append((
                field_name,
                source,
                match_type,
                base_name,
                base_desc
            ))

            # Check if description would be overwritten
            if field_desc and field_desc != base_desc:
                results["overwritten_fields"].append((
                    field_name,
                    source,
                    field_desc,
                    base_desc
                ))

            # Check if matched by alias (recommend using canonical name)
            if match_type == "alias":
                results["alias_recommendations"].append((field_name, base_name))
        else:
            # Field not found in base schemas
            if not field_desc:
                results["missing_desc_fields"].append(field_name)

    return results


def print_preview(results: Dict, verbose: bool = False):
    """Print the preview results in a user-friendly format."""
    matched = results["matched_fields"]
    overwritten = results["overwritten_fields"]
    missing = results["missing_desc_fields"]
    aliases = results["alias_recommendations"]

    print("\n" + "="*80)
    print("BASE SCHEMA MATCHING PREVIEW")
    print("="*80)

    if matched:
        print(f"\n✅ {len(matched)} field(s) would be matched by base schemas:\n")
        for field_name, source, match_type, base_name, base_desc in matched:
            match_indicator = " (via alias)" if match_type == "alias" else ""
            print(f"  • {field_name}{match_indicator}")
            print(f"    Source: {source}")
            if match_type == "alias":
                print(f"    Canonical name: {base_name}")
            if verbose:
                print(f"    Description: {base_desc[:80]}...")
            print()
    else:
        print("\n❌ No fields matched base schemas")

    if overwritten:
        print(f"\n⚠️  {len(overwritten)} existing description(s) would be OVERWRITTEN:\n")
        for field_name, source, old_desc, new_desc in overwritten:
            print(f"  • {field_name} (from {source})")
            if verbose:
                print(f"    Old: {old_desc[:80]}...")
                print(f"    New: {new_desc[:80]}...")
            print()

    if missing:
        print(f"\n📝 {len(missing)} field(s) missing descriptions (not in base schemas):\n")
        for field_name in missing:
            print(f"  • {field_name}")
        print()

    if aliases:
        print(f"\n💡 {len(aliases)} field(s) matched by alias - consider renaming:\n")
        for alias, canonical in aliases:
            print(f"  • {alias} → {canonical}")
        print()

    print("="*80)
    if matched:
        print("\nTo apply these changes, run:")
        print("  ./bqetl query schema update <dataset>.<table> --use-global-schema")
        print("  # or")
        print("  ./bqetl query schema update <dataset>.<table> --use-dataset-schema --use-global-schema")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Preview base schema matching before applying",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "table",
        help="Table identifier (dataset.table or project.dataset.table)"
    )
    parser.add_argument(
        "--global-schema",
        action="store_true",
        help="Preview matches against global.yaml (default)"
    )
    parser.add_argument(
        "--dataset-schema",
        action="store_true",
        help="Preview matches against dataset-specific schema"
    )
    parser.add_argument(
        "--both",
        action="store_true",
        help="Preview matches against both global and dataset schemas"
    )
    parser.add_argument(
        "--sql-dir",
        default="sql",
        help="Path to sql directory (default: sql)"
    )
    parser.add_argument(
        "--base-schemas-dir",
        default="bigquery_etl/schema",
        help="Path to base schemas directory (default: bigquery_etl/schema)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show full descriptions in preview"
    )

    args = parser.parse_args()

    # Determine which schemas to use
    use_global = args.global_schema or args.both or (not args.dataset_schema and not args.both)
    use_dataset = args.dataset_schema or args.both

    try:
        # Parse table identifier
        table_info = parse_table_identifier(args.table)
        project = table_info["project"]
        dataset = table_info["dataset"]
        table = table_info["table"]

        print(f"\nAnalyzing: {project}.{dataset}.{table}")
        print(f"Using: ", end="")
        if use_dataset:
            print(f"{dataset}.yaml", end="")
        if use_dataset and use_global:
            print(" + ", end="")
        if use_global:
            print("global.yaml", end="")
        print()

        # Find query schema
        query_schema = find_query_schema(project, dataset, table, args.sql_dir)

        if not query_schema:
            print(f"\nError: No schema.yaml found for {project}.{dataset}.{table}", file=sys.stderr)
            print(f"Expected location: {args.sql_dir}/{project}/{dataset}/{table}/schema.yaml", file=sys.stderr)
            print("\nRun `./bqetl query schema update {dataset}.{table}` first to generate schema.", file=sys.stderr)
            sys.exit(1)

        # Preview matches
        results = preview_base_schema_matches(
            query_schema,
            dataset,
            use_global=use_global,
            use_dataset=use_dataset,
            base_schemas_dir=args.base_schemas_dir
        )

        # Print results
        print_preview(results, verbose=args.verbose)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
