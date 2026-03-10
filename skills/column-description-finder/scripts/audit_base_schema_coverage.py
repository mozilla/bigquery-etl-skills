#!/usr/bin/env python3
"""
Audit Base Schema Coverage

Analyzes a schema.yaml file and reports which columns have descriptions available
in global.yaml and/or application-specific schema YAML files.

Usage:
    python scripts/audit_base_schema_coverage.py <dataset>.<table>
    python scripts/audit_base_schema_coverage.py <dataset>.<table> --dataset-schema
    python scripts/audit_base_schema_coverage.py <dataset>.<table> --missing-only
    python scripts/audit_base_schema_coverage.py --list-schemas

Examples:
    # Check coverage from global.yaml only
    python scripts/audit_base_schema_coverage.py telemetry_derived.clients_daily_v1

    # Check coverage from global + ads_derived.yaml
    python scripts/audit_base_schema_coverage.py ads_derived.impressions_v1 --dataset-schema

    # Show only columns missing descriptions
    python scripts/audit_base_schema_coverage.py telemetry_derived.clients_daily_v1 --missing-only

    # List all available base schema files
    python scripts/audit_base_schema_coverage.py --list-schemas
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


DEFAULT_SQL_DIR = "sql"
DEFAULT_BASE_SCHEMAS_DIR = "bigquery_etl/schema"
DEFAULT_PROJECT = "moz-fx-data-shared-prod"


def load_yaml(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}", file=sys.stderr)
        return None


def read_app_schema_from_metadata(
    project: str,
    dataset: str,
    table: str,
    sql_dir: str = DEFAULT_SQL_DIR,
) -> Optional[str]:
    """Read app_schema field from a table's metadata.yaml, if present."""
    metadata_path = Path(sql_dir) / project / dataset / table / "metadata.yaml"
    data = load_yaml(metadata_path)
    if data:
        return data.get("app_schema")
    return None


def find_available_schemas(base_schemas_dir: Path) -> List[str]:
    if not base_schemas_dir.exists():
        return []
    return sorted(p.stem for p in base_schemas_dir.glob("*.yaml"))


def schema_marker(stem: str) -> str:
    """Return a display marker for a schema file based on its naming convention."""
    if stem == "global":
        return "(global)"
    if stem.startswith("app_"):
        return "(app-specific)"
    return "(dataset-specific)"


def find_in_base(field_name: str, base_data: Dict) -> Optional[Dict]:
    """Find a field by name or alias in base schema fields."""
    for field in base_data.get("fields", []):
        if field.get("name") == field_name or field_name in field.get("aliases", []):
            return field
    return None


def flatten_fields(fields: List[Dict], prefix: str = "") -> List[Dict]:
    """Flatten nested fields into a flat list with dotted names."""
    result = []
    for field in fields:
        name = field.get("name", "")
        full_name = f"{prefix}.{name}" if prefix else name
        result.append({**field, "_full_name": full_name})
        nested = field.get("fields", [])
        if nested:
            result.extend(flatten_fields(nested, prefix=full_name))
    return result


def audit_coverage(
    query_schema: Dict,
    dataset_name: str,
    use_dataset_schema: bool = False,
    app_schema_name: Optional[str] = None,
    base_schemas_dir: str = DEFAULT_BASE_SCHEMAS_DIR,
) -> Dict:
    """
    Returns a coverage report dict with:
      - covered: fields found in base schemas (with description)
      - not_covered_but_described: fields not in base schemas but have own description
      - missing: fields not in base schemas and have no description

    Priority order (highest to lowest):
      1. App-specific schema (app_<name>.yaml)
      2. Dataset-specific schema (<dataset>.yaml)
      3. Global schema (global.yaml)
    """
    base_dir = Path(base_schemas_dir)
    global_schema = load_yaml(base_dir / "global.yaml")
    dataset_schema = load_yaml(base_dir / f"{dataset_name}.yaml") if use_dataset_schema else None
    app_schema = load_yaml(base_dir / f"{app_schema_name}.yaml") if app_schema_name else None

    covered = []
    not_covered_described = []
    missing = []

    # Only check top-level fields for base schema matching (bqetl CLI behavior)
    for field in query_schema.get("fields", []):
        name = field.get("name", "")
        own_desc = (field.get("description") or "").strip()

        # Priority: app-specific > dataset-specific > global
        match = None
        source = None
        if app_schema:
            match = find_in_base(name, app_schema)
            if match:
                source = f"{app_schema_name}.yaml"
        if not match and dataset_schema:
            match = find_in_base(name, dataset_schema)
            if match:
                source = f"{dataset_name}.yaml"
        if not match and global_schema:
            match = find_in_base(name, global_schema)
            if match:
                source = "global.yaml"

        if match:
            base_desc = (match.get("description") or "").strip()
            covered.append({
                "name": name,
                "source": source,
                "base_description": base_desc,
                "own_description": own_desc,
                "will_overwrite": bool(own_desc and own_desc != base_desc),
                "matched_as_alias": match.get("name") != name,
                "canonical_name": match.get("name"),
            })
        elif own_desc:
            not_covered_described.append({"name": name, "description": own_desc})
        else:
            missing.append({"name": name})

    return {
        "covered": covered,
        "not_covered_described": not_covered_described,
        "missing": missing,
        "total": len(query_schema.get("fields", [])),
    }


def print_report(report: Dict, table_id: str, missing_only: bool = False):
    covered = report["covered"]
    described = report["not_covered_described"]
    missing = report["missing"]
    total = report["total"]

    print(f"\n{'='*70}")
    print(f"  Base Schema Coverage Report: {table_id}")
    print(f"{'='*70}")
    print(f"  Total top-level fields: {total}")
    print(f"  Covered by base schemas: {len(covered)}")
    print(f"  Has own description (not in base): {len(described)}")
    print(f"  Missing description: {len(missing)}")
    print(f"{'='*70}\n")

    if not missing_only and covered:
        print(f"  COVERED BY BASE SCHEMAS ({len(covered)} fields):")
        for f in covered:
            alias_note = f" [alias -> {f['canonical_name']}]" if f["matched_as_alias"] else ""
            overwrite_note = " [WOULD OVERWRITE existing desc]" if f["will_overwrite"] else ""
            print(f"    + {f['name']:<40} from {f['source']}{alias_note}{overwrite_note}")
        print()

    if not missing_only and described:
        print(f"  HAS OWN DESCRIPTION ({len(described)} fields, not in base schemas):")
        for f in described:
            desc_preview = f["description"][:50] + "..." if len(f["description"]) > 50 else f["description"]
            print(f"    ~ {f['name']:<40} \"{desc_preview}\"")
        print()

    if missing:
        print(f"  MISSING DESCRIPTIONS ({len(missing)} fields):")
        for f in missing:
            print(f"    - {f['name']}")
        print()
        print("  To add descriptions from base schemas:")
        print("    ./bqetl query schema update <dataset>.<table> --use-global-schema")
        print("    # or also use dataset-specific:")
        print("    ./bqetl query schema update <dataset>.<table> --use-dataset-schema --use-global-schema")
        print("    # or also use app-specific (e.g., app_newtab):")
        print("    ./bqetl query schema update <dataset>.<table> --use-app-schema app_newtab --use-global-schema")
    else:
        print("  All fields have descriptions. No action needed.")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Audit base schema coverage for a table's schema.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "table",
        nargs="?",
        help="Table identifier: dataset.table or project.dataset.table",
    )
    parser.add_argument(
        "--app-schema",
        metavar="APP_SCHEMA",
        help="App-specific schema name to check (e.g., app_newtab). Checked before dataset schema.",
    )
    parser.add_argument(
        "--dataset-schema",
        action="store_true",
        help="Also check against dataset-specific schema (inferred from dataset name)",
    )
    parser.add_argument(
        "--missing-only",
        action="store_true",
        help="Show only fields missing descriptions",
    )
    parser.add_argument(
        "--list-schemas",
        action="store_true",
        help="List available base schema files",
    )
    parser.add_argument(
        "--sql-dir",
        default=DEFAULT_SQL_DIR,
        help=f"Path to sql directory (default: {DEFAULT_SQL_DIR})",
    )
    parser.add_argument(
        "--base-schemas-dir",
        default=DEFAULT_BASE_SCHEMAS_DIR,
        help=f"Path to base schemas directory (default: {DEFAULT_BASE_SCHEMAS_DIR})",
    )

    args = parser.parse_args()
    base_dir = Path(args.base_schemas_dir)

    if args.list_schemas:
        schemas = find_available_schemas(base_dir)
        if schemas:
            print(f"\nAvailable base schemas in {base_dir}:\n")
            for s in schemas:
                path = base_dir / f"{s}.yaml"
                data = load_yaml(path)
                count = len(data.get("fields", [])) if data else 0
                marker = schema_marker(s)
                print(f"  {s}.yaml  {marker}  [{count} top-level fields]")
            print()
        else:
            print(f"No base schemas found in {base_dir}")
        return

    if not args.table:
        parser.print_help()
        sys.exit(1)

    # Parse table identifier
    parts = args.table.split(".")
    if len(parts) == 2:
        project, dataset, table = DEFAULT_PROJECT, parts[0], parts[1]
    elif len(parts) == 3:
        project, dataset, table = parts
    else:
        print(f"Error: Invalid table identifier '{args.table}'", file=sys.stderr)
        sys.exit(1)

    schema_path = Path(args.sql_dir) / project / dataset / table / "schema.yaml"
    query_schema = load_yaml(schema_path)

    if not query_schema:
        print(f"Error: schema.yaml not found at {schema_path}", file=sys.stderr)
        print("Run './bqetl query schema update <dataset>.<table>' first.", file=sys.stderr)
        sys.exit(1)

    # Resolve app_schema: explicit flag takes priority, then metadata.yaml
    app_schema_name = args.app_schema
    if not app_schema_name:
        app_schema_name = read_app_schema_from_metadata(
            project, dataset, table, sql_dir=args.sql_dir
        )
        if app_schema_name:
            print(f"  [metadata] Using app_schema '{app_schema_name}' from metadata.yaml\n")

    report = audit_coverage(
        query_schema,
        dataset_name=dataset,
        use_dataset_schema=args.dataset_schema,
        app_schema_name=app_schema_name,
        base_schemas_dir=args.base_schemas_dir,
    )

    print_report(report, f"{project}.{dataset}.{table}", missing_only=args.missing_only)


if __name__ == "__main__":
    main()
