#!/usr/bin/env python3
"""
Metadata Completeness Auditor

Scans a bigquery-etl SQL directory and reports on missing metadata:
  - schema.yaml files with columns that have no description
  - metadata.yaml files that are missing a top-level description field
  - dataset_metadata.yaml files missing a description
  - Datasets missing a README.md
  - Tables missing a README.md

Usage:
    python scripts/audit_metadata_completeness.py
    python scripts/audit_metadata_completeness.py --dataset telemetry_derived
    python scripts/audit_metadata_completeness.py --dataset telemetry_derived --project moz-fx-data-shared-prod
    python scripts/audit_metadata_completeness.py --summary-only

Examples:
    # Audit all datasets across the project
    python scripts/audit_metadata_completeness.py

    # Audit a single dataset
    python scripts/audit_metadata_completeness.py --dataset telemetry_derived

    # Show only the summary stats, not the full item list
    python scripts/audit_metadata_completeness.py --dataset telemetry_derived --summary-only
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml


DEFAULT_SQL_DIR = "sql"
DEFAULT_PROJECT = "moz-fx-data-shared-prod"


def load_yaml(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: could not parse {path}: {e}", file=sys.stderr)
        return None


def collect_missing_field_descriptions(fields: List[Dict], parent: str = "") -> List[str]:
    """Recursively collect dotted paths of fields missing a description."""
    missing = []
    for field in fields or []:
        name = field.get("name", "<unnamed>")
        path = f"{parent}.{name}" if parent else name
        desc = field.get("description", "")
        if not desc or not str(desc).strip():
            missing.append(path)
        # Recurse into RECORD/nested fields
        subfields = field.get("fields", [])
        if subfields:
            missing.extend(collect_missing_field_descriptions(subfields, path))
    return missing


def audit_schema(schema_path: Path) -> List[str]:
    """Return list of field paths that are missing descriptions in schema.yaml."""
    data = load_yaml(schema_path)
    if data is None:
        return []
    return collect_missing_field_descriptions(data.get("fields", []))


def audit_metadata(metadata_path: Path) -> bool:
    """Return True if metadata.yaml is missing or has no top-level description."""
    data = load_yaml(metadata_path)
    if data is None:
        return True
    desc = data.get("description", "")
    return not desc or not str(desc).strip()


def audit_dataset_metadata(dm_path: Path) -> bool:
    """Return True if dataset_metadata.yaml is missing or has no description."""
    data = load_yaml(dm_path)
    if data is None:
        return True
    desc = data.get("description", "")
    return not desc or not str(desc).strip()


def audit_dataset(dataset_dir: Path) -> Dict:
    """Audit one dataset directory; return a structured result dict."""
    result = {
        "dataset": dataset_dir.name,
        "dataset_metadata_missing_description": False,
        "dataset_missing_readme": False,
        "tables": [],
    }

    # dataset_metadata.yaml
    dm_path = dataset_dir / "dataset_metadata.yaml"
    result["dataset_metadata_missing_description"] = audit_dataset_metadata(dm_path)

    # dataset-level README
    result["dataset_missing_readme"] = not (dataset_dir / "README.md").exists()

    # iterate table subdirectories (those that look like versioned tables)
    for table_dir in sorted(dataset_dir.iterdir()):
        if not table_dir.is_dir():
            continue
        # Skip hidden dirs and files without schema/metadata
        schema_path = table_dir / "schema.yaml"
        metadata_path = table_dir / "metadata.yaml"
        if not schema_path.exists() and not metadata_path.exists():
            continue

        table_result = {
            "table": table_dir.name,
            "missing_schema_descriptions": [],
            "metadata_missing_description": False,
            "missing_readme": False,
        }

        if schema_path.exists():
            table_result["missing_schema_descriptions"] = audit_schema(schema_path)

        table_result["metadata_missing_description"] = audit_metadata(metadata_path)
        table_result["missing_readme"] = not (table_dir / "README.md").exists()

        result["tables"].append(table_result)

    return result


def print_report(results: List[Dict], summary_only: bool = False) -> None:
    total_datasets = len(results)
    total_tables = sum(len(r["tables"]) for r in results)
    datasets_missing_dm_desc = [r["dataset"] for r in results if r["dataset_metadata_missing_description"]]
    datasets_missing_readme = [r["dataset"] for r in results if r["dataset_missing_readme"]]

    tables_missing_schema_desc = []
    tables_missing_metadata_desc = []
    tables_missing_readme = []

    for r in results:
        dataset = r["dataset"]
        for t in r["tables"]:
            fqn = f"{dataset}.{t['table']}"
            if t["missing_schema_descriptions"]:
                tables_missing_schema_desc.append((fqn, t["missing_schema_descriptions"]))
            if t["metadata_missing_description"]:
                tables_missing_metadata_desc.append(fqn)
            if t["missing_readme"]:
                tables_missing_readme.append(fqn)

    # --- Summary ---
    print("=" * 70)
    print("METADATA COMPLETENESS AUDIT — SUMMARY")
    print("=" * 70)
    print(f"  Total datasets scanned:                {total_datasets}")
    print(f"  Total tables scanned:                  {total_tables}")
    print()
    print(f"  Datasets missing dataset_metadata desc: {len(datasets_missing_dm_desc)}", end="")
    if total_datasets:
        print(f"  ({100 * len(datasets_missing_dm_desc) / total_datasets:.1f}%)")
    else:
        print()
    print(f"  Datasets missing README:               {len(datasets_missing_readme)}", end="")
    if total_datasets:
        print(f"  ({100 * len(datasets_missing_readme) / total_datasets:.1f}%)")
    else:
        print()
    print()
    print(f"  Tables with missing schema descriptions: {len(tables_missing_schema_desc)}", end="")
    if total_tables:
        print(f"  ({100 * len(tables_missing_schema_desc) / total_tables:.1f}%)")
    else:
        print()
    print(f"  Tables with missing metadata desc:     {len(tables_missing_metadata_desc)}", end="")
    if total_tables:
        print(f"  ({100 * len(tables_missing_metadata_desc) / total_tables:.1f}%)")
    else:
        print()
    print(f"  Tables missing README:                 {len(tables_missing_readme)}", end="")
    if total_tables:
        print(f"  ({100 * len(tables_missing_readme) / total_tables:.1f}%)")
    else:
        print()

    if summary_only:
        return

    # --- Detail sections ---
    if datasets_missing_dm_desc:
        print()
        print("DATASETS — dataset_metadata.yaml missing description")
        print("-" * 70)
        for ds in datasets_missing_dm_desc:
            print(f"  {ds}")

    if datasets_missing_readme:
        print()
        print("DATASETS — missing README.md")
        print("-" * 70)
        for ds in datasets_missing_readme:
            print(f"  {ds}")

    if tables_missing_metadata_desc:
        print()
        print("TABLES — metadata.yaml missing description")
        print("-" * 70)
        for fqn in tables_missing_metadata_desc:
            print(f"  {fqn}")

    if tables_missing_readme:
        print()
        print("TABLES — missing README.md")
        print("-" * 70)
        for fqn in tables_missing_readme:
            print(f"  {fqn}")

    if tables_missing_schema_desc:
        print()
        print("TABLES — schema.yaml has columns with missing descriptions")
        print("-" * 70)
        for fqn, missing_fields in tables_missing_schema_desc:
            print(f"  {fqn}")
            for field in missing_fields[:10]:
                print(f"    - {field}")
            if len(missing_fields) > 10:
                print(f"    ... and {len(missing_fields) - 10} more")

    print()
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Audit bigquery-etl metadata completeness.")
    parser.add_argument("--dataset", help="Dataset name to scope audit (e.g. telemetry_derived). Omit to scan all.")
    parser.add_argument("--project", default=DEFAULT_PROJECT, help=f"GCP project directory (default: {DEFAULT_PROJECT})")
    parser.add_argument("--sql-dir", default=DEFAULT_SQL_DIR, help=f"SQL root directory (default: {DEFAULT_SQL_DIR})")
    parser.add_argument("--summary-only", action="store_true", help="Print only summary stats, not the full item list")
    args = parser.parse_args()

    project_dir = Path(args.sql_dir) / args.project
    if not project_dir.exists():
        print(f"Error: project directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    if args.dataset:
        dataset_dir = project_dir / args.dataset
        if not dataset_dir.is_dir():
            print(f"Error: dataset directory not found: {dataset_dir}", file=sys.stderr)
            sys.exit(1)
        dataset_dirs = [dataset_dir]
    else:
        dataset_dirs = sorted(d for d in project_dir.iterdir() if d.is_dir())

    results = []
    for d in dataset_dirs:
        results.append(audit_dataset(d))

    print_report(results, summary_only=args.summary_only)


if __name__ == "__main__":
    main()
