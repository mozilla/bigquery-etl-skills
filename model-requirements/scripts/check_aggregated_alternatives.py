#!/usr/bin/env python3
"""
Check for Aggregated Table Alternatives

This script helps identify when _live or _stable tables are being used and suggests
better aggregated alternatives from _derived datasets.

Usage:
    python check_aggregated_alternatives.py <table_identifier> [<table_identifier2> ...]

Examples:
    # Single table
    python check_aggregated_alternatives.py telemetry_live.main_v5

    # Multiple tables
    python check_aggregated_alternatives.py firefox_desktop_stable.baseline_v1 telemetry_stable.events_v1

    # With project
    python check_aggregated_alternatives.py moz-fx-data-shared-prod.telemetry_live.main_v5

Output:
    - Flags tables that are _live or _stable
    - Suggests known aggregated alternatives
    - Provides DataHub lineage query parameters for finding alternatives
"""

import argparse
import json
import sys
import re
from typing import Dict, List, Tuple


# Known mappings of _live/_stable tables to better alternatives
KNOWN_ALTERNATIVES = {
    # Firefox Desktop - Main Ping
    "telemetry_live.main_v5": [
        ("telemetry_derived.clients_daily_v1", "Most common - one row per client per day, pre-aggregated metrics"),
        ("telemetry_derived.clients_last_seen_v1", "For retention analysis with 28-day history"),
        ("telemetry_derived.main_summary_v4", "Deprecated - ping-level, use clients_daily if possible"),
    ],
    "telemetry_stable.main_v4": [
        ("telemetry_derived.clients_daily_v1", "Most common - one row per client per day, pre-aggregated metrics"),
        ("telemetry_derived.clients_last_seen_v1", "For retention analysis with 28-day history"),
    ],

    # Firefox Desktop - Events
    "telemetry_live.events_v1": [
        ("telemetry_derived.events_daily_v1", "One row per client per event type per day"),
        ("telemetry_derived.event_events_v1", "Individual event records with parsed extras"),
    ],
    "telemetry_stable.events_v1": [
        ("telemetry_derived.events_daily_v1", "One row per client per event type per day"),
        ("telemetry_derived.event_events_v1", "Individual event records with parsed extras"),
    ],

    # Firefox Desktop - Baseline
    "firefox_desktop_live.baseline_v1": [
        ("firefox_desktop_derived.baseline_clients_daily_v1", "One row per client per day, aggregated baseline metrics"),
    ],
    "firefox_desktop_stable.baseline_v1": [
        ("firefox_desktop_derived.baseline_clients_daily_v1", "One row per client per day, aggregated baseline metrics"),
    ],

    # Mobile - Generic patterns (will match with regex)
    # Fenix
    "org_mozilla_fenix_stable.baseline_v1": [
        ("org_mozilla_fenix_derived.baseline_clients_daily_v1", "One row per client per day"),
    ],
    "org_mozilla_fenix_stable.metrics_v1": [
        ("org_mozilla_fenix_derived.metrics_clients_daily_v1", "One row per client per day, aggregated metrics"),
    ],
    "org_mozilla_fenix_stable.events_v1": [
        ("org_mozilla_fenix_derived.events_daily_v1", "One row per client per event type per day (if exists)"),
        ("org_mozilla_fenix_derived.events_stream_v1", "Individual event records"),
    ],

    # Firefox iOS
    "org_mozilla_firefox_stable.baseline_v1": [
        ("org_mozilla_firefox_derived.baseline_clients_daily_v1", "One row per client per day"),
    ],
    "org_mozilla_firefox_stable.metrics_v1": [
        ("org_mozilla_firefox_derived.metrics_clients_daily_v1", "One row per client per day, aggregated metrics"),
    ],

    # Focus
    "org_mozilla_focus_stable.baseline_v1": [
        ("org_mozilla_focus_derived.baseline_clients_daily_v1", "One row per client per day"),
    ],
}


def parse_table_identifier(identifier: str) -> Dict[str, str]:
    """
    Parse table identifier into components.

    Handles:
    - dataset.table
    - project.dataset.table

    Returns dict with project, dataset, table, full_name
    """
    # Remove backticks if present
    identifier = identifier.strip('`')

    parts = identifier.split('.')

    if len(parts) == 2:
        dataset, table = parts
        project = "moz-fx-data-shared-prod"
    elif len(parts) == 3:
        project, dataset, table = parts
    else:
        raise ValueError(f"Invalid table identifier: {identifier}")

    return {
        "project": project,
        "dataset": dataset,
        "table": table,
        "full_name": f"{project}.{dataset}.{table}",
        "short_name": f"{dataset}.{table}",
    }


def is_raw_table(dataset: str, table: str) -> Tuple[bool, str]:
    """
    Check if table is a raw _live or _stable table.

    Returns (is_raw, table_type) where table_type is "live", "stable", or None
    """
    if dataset.endswith("_live") or "_live." in dataset:
        return (True, "live")
    elif dataset.endswith("_stable") or "_stable." in dataset:
        return (True, "stable")

    # Check table name patterns
    if table.endswith("_live"):
        return (True, "live")
    elif table.endswith("_stable"):
        return (True, "stable")

    return (False, None)


def get_known_alternatives(short_name: str, table_info: Dict[str, str]) -> List[Tuple[str, str]]:
    """
    Get known alternatives from the mapping.

    Returns list of (table_name, description) tuples
    """
    # Direct match
    if short_name in KNOWN_ALTERNATIVES:
        return KNOWN_ALTERNATIVES[short_name]

    # Try pattern matching for mobile products
    dataset = table_info["dataset"]
    table = table_info["table"]

    # Generic mobile pattern: {product}_stable.{ping_type}_v1
    if dataset.endswith("_stable"):
        product = dataset.replace("_stable", "")
        derived_dataset = f"{product}_derived"

        if table == "baseline_v1":
            return [(f"{derived_dataset}.baseline_clients_daily_v1", "One row per client per day")]
        elif table == "metrics_v1":
            return [(f"{derived_dataset}.metrics_clients_daily_v1", "One row per client per day, aggregated metrics")]
        elif table == "events_v1":
            return [
                (f"{derived_dataset}.events_daily_v1", "One row per client per event type per day (if exists)"),
                (f"{derived_dataset}.events_stream_v1", "Individual event records"),
            ]

    return []


def generate_lineage_query_params(table_info: Dict[str, str]) -> Dict:
    """
    Generate DataHub lineage query parameters.
    """
    full_name = table_info["full_name"]
    urn = f"urn:li:dataset:(urn:li:dataPlatform:bigquery,{full_name},PROD)"

    return {
        "tool": "mcp__datahub-cloud__get_lineage",
        "parameters": {
            "urn": urn,
            "column": None,
            "upstream": False,  # Look downstream for derived tables
            "max_hops": 1,
            "filters": None
        }
    }


def check_table(table_identifier: str) -> Dict:
    """
    Check a single table and return analysis.
    """
    try:
        table_info = parse_table_identifier(table_identifier)
    except ValueError as e:
        return {
            "error": str(e),
            "table": table_identifier
        }

    is_raw, table_type = is_raw_table(table_info["dataset"], table_info["table"])

    result = {
        "table": table_identifier,
        "parsed": table_info,
        "is_raw": is_raw,
        "table_type": table_type,
    }

    if is_raw:
        # Get known alternatives
        alternatives = get_known_alternatives(table_info["short_name"], table_info)
        result["known_alternatives"] = alternatives

        # Generate lineage query
        result["lineage_query"] = generate_lineage_query_params(table_info)

    return result


def format_output(results: List[Dict], output_format: str = "text") -> str:
    """
    Format results for output.
    """
    if output_format == "json":
        return json.dumps(results, indent=2)

    # Text format
    output = []

    for result in results:
        if "error" in result:
            output.append(f"❌ Error: {result['error']}")
            output.append("")
            continue

        table = result["table"]
        is_raw = result["is_raw"]
        table_type = result.get("table_type")

        if not is_raw:
            output.append(f"✅ {table}")
            output.append(f"   This is already an optimized table (not _live or _stable)")
            output.append("")
            continue

        # Raw table found
        output.append(f"⚠️  {table}")
        output.append(f"   Type: _{table_type} table (raw ingestion)")
        output.append("")

        # Known alternatives
        alternatives = result.get("known_alternatives", [])
        if alternatives:
            output.append("   📊 Suggested Alternatives:")
            for alt_table, description in alternatives:
                output.append(f"      • {alt_table}")
                output.append(f"        {description}")
            output.append("")
        else:
            output.append("   ℹ️  No known alternatives in lookup table")
            output.append("")

        # Lineage query
        output.append("   🔍 To find more alternatives, query DataHub lineage:")
        lineage = result.get("lineage_query", {})
        output.append(f"      Tool: {lineage.get('tool')}")
        output.append(f"      URN: {lineage.get('parameters', {}).get('urn')}")
        output.append(f"      Direction: downstream (look for _derived tables)")
        output.append("")

        # Benefits reminder
        output.append("   💡 Benefits of using aggregated alternatives:")
        output.append("      • Faster queries (pre-aggregated)")
        output.append("      • Lower cost (less data scanned)")
        output.append("      • Deduplicated (no duplicate pings)")
        output.append("      • Better documented and tested")
        output.append("")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Check for aggregated alternatives to _live/_stable tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "tables",
        nargs="+",
        help="Table identifiers to check (dataset.table or project.dataset.table)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    # Check each table
    results = []
    for table in args.tables:
        result = check_table(table)
        results.append(result)

    # Output results
    output = format_output(results, args.format)
    print(output)

    # Exit code: 1 if any raw tables found, 0 otherwise
    any_raw = any(r.get("is_raw", False) for r in results if "error" not in r)
    sys.exit(1 if any_raw else 0)


if __name__ == "__main__":
    main()
