#!/usr/bin/env python3
"""Compare schema.yaml data types against actual BigQuery table schemas."""

import sys
from pathlib import Path

import yaml
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# Canonical type aliases — BQ API and YAML use different names for the same type
TYPE_ALIASES = {
    "INT64": "INTEGER",
    "BOOL": "BOOLEAN",
    "FLOAT64": "FLOAT",
    "INTEGER": "INTEGER",
    "BOOLEAN": "BOOLEAN",
    "FLOAT": "FLOAT",
}


def normalize_type(t: str) -> str:
    return TYPE_ALIASES.get(t.upper(), t.upper())


def flatten_fields(fields: list, prefix: str = "") -> dict:
    """Recursively flatten nested fields into dotted paths."""
    result = {}
    for field in fields:
        path = f"{prefix}.{field['name']}" if prefix else field["name"]
        result[path] = field
        if field.get("type", "").upper() == "RECORD" and "fields" in field:
            result.update(flatten_fields(field["fields"], path))
    return result


def compare_schema(yaml_path: Path, client: bigquery.Client) -> list:
    """
    Compare schema.yaml against BigQuery. Returns list of mismatch dicts.
    Path format: sql/<project>/<dataset>/<table>/schema.yaml
    """
    parts = yaml_path.parts
    try:
        sql_idx = parts.index("sql")
        project, dataset, table = parts[sql_idx + 1], parts[sql_idx + 2], parts[sql_idx + 3]
    except (ValueError, IndexError):
        return [{"error": f"Cannot parse table path from {yaml_path}"}]

    table_id = f"{project}.{dataset}.{table}"

    with open(yaml_path) as f:
        yaml_schema = yaml.safe_load(f)

    if not yaml_schema or "fields" not in yaml_schema:
        return [{"error": f"{yaml_path}: invalid or empty schema.yaml"}]

    try:
        bq_table = client.get_table(table_id)
    except NotFound:
        return [{"warning": f"{table_id}: table not found in BigQuery"}]
    except Exception as e:
        return [{"error": f"{table_id}: {e}"}]

    bq_fields = [field.to_api_repr() for field in bq_table.schema]

    yaml_flat = flatten_fields(yaml_schema["fields"])
    bq_flat = flatten_fields(bq_fields)

    mismatches = []

    for field_path, yaml_field in yaml_flat.items():
        if field_path not in bq_flat:
            mismatches.append({
                "table": table_id,
                "field": field_path,
                "issue": "missing_in_bq",
                "yaml_type": yaml_field.get("type"),
                "bq_type": None,
            })
            continue

        bq_field = bq_flat[field_path]
        yaml_type = normalize_type(yaml_field.get("type", ""))
        bq_type = normalize_type(bq_field.get("type", ""))
        yaml_mode = yaml_field.get("mode", "NULLABLE").upper()
        bq_mode = bq_field.get("mode", "NULLABLE").upper()

        if yaml_type != bq_type:
            mismatches.append({
                "table": table_id,
                "field": field_path,
                "issue": "type_mismatch",
                "yaml_type": yaml_type,
                "bq_type": bq_type,
            })

        if yaml_mode != bq_mode:
            mismatches.append({
                "table": table_id,
                "field": field_path,
                "issue": "mode_mismatch",
                "yaml_mode": yaml_mode,
                "bq_mode": bq_mode,
            })

    for field_path in bq_flat:
        if field_path not in yaml_flat:
            mismatches.append({
                "table": table_id,
                "field": field_path,
                "issue": "missing_in_yaml",
                "yaml_type": None,
                "bq_type": bq_flat[field_path].get("type"),
            })

    return mismatches


def print_mismatch(m: dict):
    if "error" in m:
        print(f"ERROR       {m['error']}")
    elif "warning" in m:
        print(f"WARNING     {m['warning']}")
    elif m["issue"] == "type_mismatch":
        print(f"TYPE        {m['table']} | {m['field']}: yaml={m['yaml_type']} bq={m['bq_type']}")
    elif m["issue"] == "mode_mismatch":
        print(f"MODE        {m['table']} | {m['field']}: yaml={m['yaml_mode']} bq={m['bq_mode']}")
    elif m["issue"] == "missing_in_bq":
        print(f"NOT_IN_BQ   {m['table']} | {m['field']} (yaml type: {m['yaml_type']})")
    elif m["issue"] == "missing_in_yaml":
        print(f"NOT_IN_YAML {m['table']} | {m['field']} (bq type: {m['bq_type']})")


def main(sql_dir: str = "sql", project_filter=None, dataset_filter=None, table_filter=None):
    client = bigquery.Client()
    search_path = Path(sql_dir)

    # Narrow the search path as specifically as possible to avoid unnecessary glob
    if project_filter and dataset_filter and table_filter:
        schema_files = list((search_path / project_filter / dataset_filter / table_filter).glob("schema.yaml"))
    elif project_filter and dataset_filter:
        schema_files = list((search_path / project_filter / dataset_filter).rglob("schema.yaml"))
    elif project_filter:
        schema_files = list((search_path / project_filter).rglob("schema.yaml"))
    else:
        schema_files = list(search_path.rglob("schema.yaml"))

    # Apply table filter as substring match when not used in path narrowing
    if table_filter and not (project_filter and dataset_filter):
        schema_files = [f for f in schema_files if table_filter in f.parts[-2]]

    print(f"Found {len(schema_files)} schema.yaml file(s)\n")

    all_mismatches = []
    for schema_file in sorted(schema_files):
        mismatches = compare_schema(schema_file, client)
        all_mismatches.extend(mismatches)
        for m in mismatches:
            print_mismatch(m)

    type_mismatches = [m for m in all_mismatches if m.get("issue") == "type_mismatch"]
    print(f"\nTotal type mismatches: {len(type_mismatches)}")
    print(f"Total issues:          {len(all_mismatches)}")
    return 1 if type_mismatches else 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare schema.yaml data types against BigQuery table schemas."
    )
    parser.add_argument("--project", help="Filter by GCP project (e.g. moz-fx-data-shared-prod)")
    parser.add_argument("--dataset", help="Filter by dataset (e.g. accounts_backend_derived)")
    parser.add_argument("--table", help="Filter by table name or substring (e.g. monitoring_db_counts_v1)")
    parser.add_argument("--sql-dir", default="sql", help="Path to sql/ directory (default: sql)")
    args = parser.parse_args()

    sys.exit(main(
        sql_dir=args.sql_dir,
        project_filter=args.project,
        dataset_filter=args.dataset,
        table_filter=args.table,
    ))
