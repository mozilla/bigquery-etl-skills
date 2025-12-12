#!/usr/bin/env python3
"""
DataHub Lineage Helper Script

This script queries DataHub for table lineage and returns filtered, essential information.
Use this instead of direct DataHub MCP calls to avoid verbose responses and save tokens.

Usage:
    python datahub_lineage.py <table_identifier> [--direction upstream|downstream] [--max-hops N]

Examples:
    # Get upstream tables
    python datahub_lineage.py telemetry_derived.clients_daily_v1

    # Get downstream tables
    python datahub_lineage.py telemetry.main --direction downstream

    # Get lineage 2 hops away
    python datahub_lineage.py search_derived.search_clients_daily_v8 --max-hops 2

Table identifier formats accepted:
    - dataset.table (e.g., telemetry_derived.clients_daily_v1)
    - project.dataset.table (e.g., moz-fx-data-shared-prod.telemetry_derived.clients_daily_v1)
    - Full URN (e.g., urn:li:dataset:(urn:li:dataPlatform:bigquery,...))
"""

import argparse
import json
import sys
from typing import Dict, List, Set


def parse_table_identifier(identifier: str) -> dict:
    """
    Parse various table identifier formats into components.

    Returns:
        dict with keys: project, dataset, table, urn
    """
    # Check if it's already a URN
    if identifier.startswith("urn:li:dataset:"):
        # Extract from URN format
        # urn:li:dataset:(urn:li:dataPlatform:bigquery,moz-fx-data-shared-prod.dataset.table,PROD)
        parts = identifier.split(",")
        if len(parts) >= 2:
            fqn = parts[1]  # moz-fx-data-shared-prod.dataset.table
            return parse_table_identifier(fqn)
        return {"urn": identifier, "project": None, "dataset": None, "table": None}

    # Split by dots
    parts = identifier.split(".")

    if len(parts) == 2:
        # dataset.table format (default project)
        dataset, table = parts
        project = "moz-fx-data-shared-prod"
    elif len(parts) == 3:
        # project.dataset.table format
        project, dataset, table = parts
    else:
        raise ValueError(f"Invalid table identifier format: {identifier}")

    # Construct URN
    urn = f"urn:li:dataset:(urn:li:dataPlatform:bigquery,{project}.{dataset}.{table},PROD)"

    return {
        "project": project,
        "dataset": dataset,
        "table": table,
        "urn": urn,
        "fqn": f"{project}.{dataset}.{table}"
    }


def format_lineage_result(lineage_data: dict, direction: str) -> dict:
    """
    Filter and format DataHub lineage response to essential information.

    Args:
        lineage_data: Raw response from DataHub get_lineage
        direction: "upstream" or "downstream"

    Returns:
        Filtered dict with only essential lineage info
    """
    result = {
        "direction": direction,
        "tables": []
    }

    # Extract tables from lineage response
    # DataHub lineage structure varies, adapt as needed
    if not lineage_data:
        return result

    # Parse lineage entities
    entities = lineage_data.get("entities", [])
    for entity in entities:
        urn = entity.get("urn", "")

        # Extract table name from URN
        if "bigquery" in urn and "dataset:" in urn:
            # urn:li:dataset:(urn:li:dataPlatform:bigquery,project.dataset.table,PROD)
            parts = urn.split(",")
            if len(parts) >= 2:
                fqn = parts[1]
                table_info = {
                    "urn": urn,
                    "fqn": fqn,
                    "type": entity.get("type", "dataset")
                }

                # Extract dataset and table name
                fqn_parts = fqn.split(".")
                if len(fqn_parts) >= 3:
                    table_info["project"] = fqn_parts[0]
                    table_info["dataset"] = fqn_parts[1]
                    table_info["table"] = ".".join(fqn_parts[2:])

                result["tables"].append(table_info)

    return result


def get_lineage_via_mcp(table_urn: str, direction: str = "upstream", max_hops: int = 1) -> dict:
    """
    Query DataHub via MCP tool for lineage.

    This function would be called by Claude Code using the mcp__datahub-cloud__get_lineage tool.
    For script usage, this serves as a template for the expected format.

    Args:
        table_urn: Full URN of the table
        direction: "upstream" or "downstream"
        max_hops: Number of hops (1-3)

    Returns:
        Formatted lineage result
    """
    # NOTE: This is a template. Actual MCP calls are made by Claude Code.
    # This script serves as a reference for filtering logic.

    print(f"# DataHub Lineage Query", file=sys.stderr)
    print(f"Table URN: {table_urn}", file=sys.stderr)
    print(f"Direction: {direction}", file=sys.stderr)
    print(f"Max Hops: {max_hops}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Use this information with the mcp__datahub-cloud__get_lineage tool:", file=sys.stderr)

    mcp_call = {
        "tool": "mcp__datahub-cloud__get_lineage",
        "parameters": {
            "urn": table_urn,
            "column": None,
            "upstream": direction == "upstream",
            "max_hops": max_hops,
            "filters": None
        }
    }

    return mcp_call


def main():
    parser = argparse.ArgumentParser(
        description="Query DataHub for table lineage with filtered results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "table",
        help="Table identifier (dataset.table or project.dataset.table)"
    )
    parser.add_argument(
        "--direction",
        choices=["upstream", "downstream"],
        default="upstream",
        help="Lineage direction (default: upstream)"
    )
    parser.add_argument(
        "--max-hops",
        type=int,
        default=1,
        choices=[1, 2, 3],
        help="Maximum hops for lineage (default: 1)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    try:
        # Parse table identifier
        table_info = parse_table_identifier(args.table)

        # Generate MCP call template
        mcp_call = get_lineage_via_mcp(
            table_info["urn"],
            args.direction,
            args.max_hops
        )

        if args.format == "json":
            print(json.dumps(mcp_call, indent=2))
        else:
            print(f"\n📊 Lineage Query for: {table_info['fqn']}\n")
            print(f"Direction: {args.direction}")
            print(f"Max Hops: {args.max_hops}")
            print(f"\nURN: {table_info['urn']}")
            print(f"\n🔧 MCP Tool Call:\n")
            print(json.dumps(mcp_call, indent=2))
            print("\n💡 This script provides the parameters for Claude Code to query DataHub efficiently.")
            print("   Claude Code will filter the results to show only essential lineage information.\n")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
