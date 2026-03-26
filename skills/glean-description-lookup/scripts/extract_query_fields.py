#!/usr/bin/env python3
"""
Extract field references from a BigQuery SQL query.

Reports all column references grouped by source table, with special
handling for _live and _stable Glean tables.

Usage:
    python extract_query_fields.py path/to/query.sql
    python extract_query_fields.py path/to/query.sql --glean-only
    python extract_query_fields.py path/to/query.sql --table firefox_desktop_stable.newtab_v1
"""

import re
import sys
import argparse
from pathlib import Path


GLEAN_SUFFIXES = ("_live", "_stable")


def read_sql(path: str) -> str:
    return Path(path).read_text()


def strip_comments(sql: str) -> str:
    """Remove single-line (--) and block (/* */) comments."""
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql


def extract_source_tables(sql: str) -> list[str]:
    """Extract table references from FROM and JOIN clauses."""
    pattern = r"(?:FROM|JOIN)\s+`?([a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+)`?"
    return list(dict.fromkeys(re.findall(pattern, sql, re.IGNORECASE)))


def is_glean_table(table_ref: str) -> bool:
    """Return True if the table name ends in _live or _stable."""
    # table_ref is project.dataset.table or dataset.table
    parts = table_ref.split(".")
    dataset = parts[-2] if len(parts) >= 2 else ""
    return any(dataset.endswith(suffix) for suffix in GLEAN_SUFFIXES)


def extract_field_references(sql: str) -> list[str]:
    """
    Extract field references from the SELECT clause and WHERE/GROUP BY/ORDER BY.

    Returns dot-notation field names (e.g. client_info.client_id,
    metrics.string.newtab_locale) deduplicated and sorted.
    """
    # Match identifiers with optional dot-notation (up to 3 levels deep)
    # Excludes pure table aliases (single word after FROM/JOIN)
    pattern = r"\b([a-z_][a-z0-9_]*)(?:\.([a-z_][a-z0-9_]*))?(?:\.([a-z_][a-z0-9_]*))?\b"

    candidates = set()
    for m in re.finditer(pattern, sql, re.IGNORECASE):
        parts = [p for p in m.groups() if p]
        if len(parts) >= 2:  # Only include dotted references (field.subfield)
            candidates.add(".".join(parts))

    # Filter out SQL keywords and table aliases
    sql_keywords = {
        "select", "from", "where", "group", "by", "order", "having",
        "join", "left", "right", "inner", "outer", "on", "as", "and",
        "or", "not", "in", "is", "null", "true", "false", "case", "when",
        "then", "else", "end", "distinct", "limit", "offset", "union",
        "all", "with", "date", "timestamp", "string", "int64", "float64",
        "bool", "array", "struct", "if", "ifnull", "coalesce", "cast",
        "extract", "date_sub", "date_add", "date_trunc", "safe_divide",
        "count", "sum", "avg", "min", "max", "countif", "approx_count_distinct",
        "current_date", "current_timestamp",
    }

    filtered = sorted(
        f for f in candidates
        if not any(part.lower() in sql_keywords for part in f.split("."))
    )
    return filtered


def glean_url(table_ref: str) -> str:
    """Derive the Glean Dictionary URL from a BigQuery table reference."""
    parts = table_ref.split(".")
    dataset = parts[-2]  # e.g. firefox_desktop_stable
    table = parts[-1]    # e.g. newtab_v1

    # Strip _live or _stable suffix to get app_id
    app_id = dataset
    for suffix in GLEAN_SUFFIXES:
        if app_id.endswith(suffix):
            app_id = app_id[: -len(suffix)]
            break

    # Strip _v<N> version suffix from table name
    table_name = re.sub(r"_v\d+$", "", table)

    return f"https://dictionary.telemetry.mozilla.org/apps/{app_id}/tables/{table_name}"


def main():
    parser = argparse.ArgumentParser(description="Extract field references from a BigQuery SQL query.")
    parser.add_argument("query_sql", help="Path to query.sql")
    parser.add_argument(
        "--glean-only",
        action="store_true",
        help="Only report fields for _live/_stable (Glean) source tables",
    )
    parser.add_argument(
        "--table",
        help="Filter output to a specific source table (e.g. firefox_desktop_stable.newtab_v1)",
    )
    args = parser.parse_args()

    sql = strip_comments(read_sql(args.query_sql))
    source_tables = extract_source_tables(sql)
    field_refs = extract_field_references(sql)

    if args.glean_only:
        source_tables = [t for t in source_tables if is_glean_table(t)]

    if args.table:
        source_tables = [t for t in source_tables if args.table in t]

    if not source_tables:
        print("No matching source tables found.")
        sys.exit(0)

    print("=" * 60)
    print("SOURCE TABLES")
    print("=" * 60)
    for t in source_tables:
        glean = " [Glean]" if is_glean_table(t) else ""
        print(f"  {t}{glean}")
        if is_glean_table(t):
            print(f"    → Glean Dictionary: {glean_url(t)}")
    print()

    print("=" * 60)
    print("FIELD REFERENCES (dot-notation)")
    print("=" * 60)
    if field_refs:
        for f in field_refs:
            print(f"  {f}")
    else:
        print("  (no dotted field references found)")
    print()

    print("=" * 60)
    print("SUGGESTED WebFetch PROMPT")
    print("=" * 60)
    for t in source_tables:
        if is_glean_table(t):
            url = glean_url(t)
            fields_str = ", ".join(field_refs[:20])  # cap at 20 for prompt length
            if len(field_refs) > 20:
                fields_str += f", ... ({len(field_refs) - 20} more)"
            print(f"""
WebFetch:
  URL: {url}
  Prompt: "Extract the name, BigQuery type, mode (NULLABLE/REPEATED), and description
  for these fields only: {fields_str}.
  Return as a list with one entry per field."
""")


if __name__ == "__main__":
    main()
