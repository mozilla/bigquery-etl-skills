#!/usr/bin/env python3
"""
Extract field references from a BigQuery SQL query.

Reports all column references grouped by source table, with special
handling for _live and _stable Glean tables.

Usage:
    python extract_query_fields.py path/to/query.sql
    python extract_query_fields.py path/to/query.sql --glean-only
    python extract_query_fields.py path/to/query.sql --table <app>_stable.<ping>_v1

LIMITATION: Table alias and UNNEST alias resolution is not supported.
If the query uses aliases (e.g. FROM ... AS e, CROSS JOIN UNNEST(events) AS ev),
aliased field references (e.g. e.submission_timestamp, ev.name) may appear in the
FIELD REFERENCES output as false positives (with the alias prefix intact) or may
be missing entirely if no full dotted path exists in the query. After running this
script, review the field list: remove entries whose first segment is a known alias,
and add any Glean paths that were only accessed via alias.
"""

import re
import sys
import argparse
from pathlib import Path


GLEAN_SUFFIXES = ("_live", "_stable")

# Dataset suffix patterns that indicate a table reference, not a field path
_TABLE_DATASET_SUFFIXES = (
    "_live", "_stable", "_derived", "_bi", "_external", "_raw",
)

# Known UDF/function namespaces whose dot-notation calls are not field references.
# Note: "safe" is omitted here — it is already excluded via first_segment_keywords.
_UDF_NAMESPACES = {"mozfun", "net", "st", "keys", "map", "mode"}


def read_sql(path: str) -> str:
    return Path(path).read_text()


def strip_comments(sql: str) -> str:
    """Remove single-line (--) and block (/* */) comments."""
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql


def strip_jinja(sql: str) -> str:
    """Remove Jinja2 template tags and variable expressions."""
    # Remove block tags: {% ... %}
    sql = re.sub(r"\{%-?\s*.*?-?%\}", " ", sql, flags=re.DOTALL)
    # Remove variable expressions: {{ ... }}
    sql = re.sub(r"\{\{-?\s*.*?-?\}\}", " ", sql, flags=re.DOTALL)
    return sql


def strip_string_literals(sql: str) -> str:
    """Replace single-quoted string literals with empty quotes.

    Prevents URLs and other dot-containing strings inside literals
    (e.g. 'https://newtab.firefoxchina.cn/...') from being matched
    as field references.

    Limitation: does not handle BigQuery's escaped-quote syntax ('' inside a
    string, e.g. 'it''s a test'). The regex matches only up to the first
    closing quote, leaving a stray fragment. This edge case is unlikely to
    produce valid Glean field paths and can be ignored in practice.
    """
    return re.sub(r"'[^']*'", "''", sql)


def extract_source_tables(sql: str) -> list[str]:
    """Extract table references from FROM and JOIN clauses.

    Handles all backtick quoting styles:
      `project.dataset.table`
      `project`.`dataset`.`table`
      `project`.dataset.table
      dataset.table  (2-part, no project prefix)
    """
    # Match any mix of backtick-quoted or bare identifiers after FROM/JOIN
    pattern = r"(?:FROM|JOIN)\s+([`a-zA-Z0-9_\-][`a-zA-Z0-9_\-\.]*)"
    results = []
    for m in re.findall(pattern, sql, re.IGNORECASE):
        clean = m.replace("`", "")
        if clean.count(".") >= 1:  # accept dataset.table or project.dataset.table
            results.append(clean)
    return list(dict.fromkeys(results))


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
    metrics.string.newtab_locale, metrics.labeled_counter.some_label.key)
    deduplicated and sorted. Supports any nesting depth.

    NOTE: Cannot identify table or UNNEST aliases. Aliased field references
    (e.g. alias.field) may appear as false positives or may be missing if
    accessed only via alias with no full Glean path present in the query.
    """
    # Match any dotted identifier sequence with 2+ parts — no depth limit.
    # Requires at least one dot so bare identifiers (table aliases, keywords) are excluded.
    pattern = r"\b([a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)+)\b"

    candidates = set()
    for m in re.finditer(pattern, sql, re.IGNORECASE):
        candidates.add(m.group(1))

    # Keywords that are never valid as the FIRST segment of a Glean field path.
    # Middle segments (e.g. "string" in metrics.string.newtab_locale) are
    # Glean metric type names and must NOT be filtered out.
    first_segment_keywords = {
        # DML / clauses
        "select", "from", "where", "group", "by", "order", "having",
        "join", "left", "right", "inner", "outer", "cross", "on", "as", "and",
        "or", "not", "in", "is", "null", "true", "false", "case", "when",
        "then", "else", "end", "distinct", "limit", "offset", "union",
        "all", "with", "qualify", "over", "partition", "rows", "range",
        "between", "like", "ilike", "exists", "lateral", "unnest",
        # Types (valid as first segment only when bare, e.g. CAST(x AS STRING))
        "int64", "float64", "numeric", "bool", "bytes",
        # Conditionals / casting
        "if", "ifnull", "nullif", "coalesce", "cast", "safe_cast",
        # Aggregation / math / analytic functions
        "count", "sum", "avg", "min", "max", "countif",
        "approx_count_distinct", "approx_quantiles", "any_value",
        "array_agg", "array_concat_agg", "string_agg",
        "abs", "ceil", "floor", "round", "trunc", "mod", "div",
        "pow", "power", "sqrt", "log", "log10", "exp", "ln",
        "greatest", "least", "sign",
        "row_number", "rank", "dense_rank", "ntile",
        "lag", "lead", "first_value", "last_value", "nth_value",
        "cumulative_dist", "percent_rank",
        # Date / time functions
        "current_date", "current_timestamp", "current_time",
        "extract", "date_sub", "date_add", "date_trunc", "date_diff",
        "timestamp_sub", "timestamp_add", "timestamp_trunc", "timestamp_diff",
        "time_trunc", "time_diff", "datetime_trunc", "datetime_diff",
        "date_from_unix_date", "unix_date",
        "format_date", "format_timestamp", "parse_date", "parse_timestamp",
        "generate_date_array", "generate_timestamp_array",
        # String functions
        "concat", "substr", "substring", "trim", "ltrim", "rtrim",
        "lower", "upper", "length", "replace", "split", "starts_with",
        "ends_with", "contains_substr", "instr", "lpad", "rpad",
        "regexp_replace", "regexp_extract", "regexp_extract_all",
        "regexp_contains", "regexp_instr",
        "to_base64", "from_base64", "to_hex", "from_hex",
        # JSON / array functions
        "json_extract", "json_extract_scalar", "json_extract_array",
        "json_query", "json_value", "json_value_array",
        "to_json_string", "parse_json", "json_type",
        "array_length", "array_concat", "array_reverse",
        "array_to_string", "generate_array",
        # Misc
        "safe_divide", "ieee_divide",
        "farm_fingerprint", "md5", "sha256", "sha512",
        "generate_uuid", "session_user", "error",
        "interval", "day", "week", "month", "year", "hour", "minute", "second",
        "microsecond", "millisecond",
    }

    def _is_table_ref(f: str) -> bool:
        """Return True if any segment looks like a dataset suffix (table reference)."""
        return any(
            seg.lower().endswith(suffix)
            for seg in f.split(".")
            for suffix in _TABLE_DATASET_SUFFIXES
        )

    filtered = sorted(
        f for f in candidates
        if f.split(".")[0].lower() not in first_segment_keywords  # first segment not a keyword
        and f.split(".")[0].lower() not in _UDF_NAMESPACES        # not a UDF namespace
        and not _is_table_ref(f)                                   # not a table reference
    )
    return filtered


def glean_url(table_ref: str) -> str:
    """Derive the Glean Dictionary URL from a BigQuery table reference."""
    parts = table_ref.split(".")
    dataset = parts[-2]  # e.g. <app>_stable
    table = parts[-1]    # e.g. <ping>_v1

    # Strip _live or _stable suffix to get app_id (dictionary URL form, underscores)
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
        help="Filter output to a specific source table (e.g. <app>_stable.<ping>_v1)",
    )
    parser.add_argument(
        "--max-fields",
        type=int,
        default=25,
        help="Maximum number of fields to include in the suggested WebFetch prompt (default: 25)",
    )
    args = parser.parse_args()

    raw_sql = read_sql(args.query_sql)
    sql = strip_string_literals(strip_jinja(strip_comments(raw_sql)))
    source_tables = extract_source_tables(sql)
    field_refs = extract_field_references(sql)

    if args.glean_only:
        source_tables = [t for t in source_tables if is_glean_table(t)]

    if args.table:
        source_tables = [
            t for t in source_tables
            if t == args.table or t.endswith("." + args.table)
        ]

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
    print("FIELD REFERENCES (dot-notation, full paths only)")
    print("=" * 60)
    if field_refs:
        for f in field_refs:
            print(f"  {f}")
    else:
        print("  (no dotted field references found)")
    print()

    print("⚠️  ALIAS LIMITATION: The script cannot identify table or UNNEST aliases.")
    print("   Aliased fields may appear above as false positives (e.g.")
    print("   e.submission_timestamp with alias 'e' intact) OR may be missing")
    print("   if accessed only via alias. Review the field list:")
    print("   - Remove entries whose first segment is a known alias")
    print("   - Add any Glean paths missing due to alias-only access")
    print()

    print("=" * 60)
    print("SUGGESTED WebFetch PROMPT")
    print("=" * 60)
    for t in source_tables:
        if is_glean_table(t):
            url = glean_url(t)
            prompt_fields = field_refs[: args.max_fields]
            fields_str = ", ".join(prompt_fields)
            truncated = len(field_refs) > args.max_fields
            if truncated:
                omitted = len(field_refs) - args.max_fields
                print(
                    f"⚠️  WARNING: {len(field_refs)} fields found. The suggested WebFetch prompt "
                    f"is limited to the first {args.max_fields} fields "
                    f"({omitted} field(s) not included in the prompt below). "
                    f"The full list is printed above in FIELD REFERENCES. "
                    f"Use --max-fields to expand the suggested prompt.",
                    file=sys.stderr,
                )
            print(f"""
WebFetch:
  URL: {url}
  Prompt: "Extract the name, BigQuery type, mode (NULLABLE/REPEATED), and description
  for these fields only: {fields_str}.
  Return as a list with one entry per field."
""")


if __name__ == "__main__":
    main()
