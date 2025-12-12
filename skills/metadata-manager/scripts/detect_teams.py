#!/usr/bin/env python3
"""
Detect GitHub teams used in metadata.yaml files across the repository.

Usage:
    python scripts/detect_teams.py                     # List all teams
    python scripts/detect_teams.py --dataset ads       # Recommend teams for 'ads' dataset
    python scripts/detect_teams.py --search vpn        # Search teams containing 'vpn'
"""

import argparse
import sys
from pathlib import Path
from collections import defaultdict
import yaml


def find_metadata_files(sql_dir):
    """Find all metadata.yaml files in the sql directory."""
    return list(Path(sql_dir).rglob("metadata.yaml"))


def extract_teams_from_metadata(metadata_file):
    """Extract GitHub teams from a metadata.yaml file."""
    try:
        with open(metadata_file) as f:
            metadata = yaml.safe_load(f)

        if not metadata or "owners" not in metadata:
            return []

        owners = metadata["owners"]
        if not isinstance(owners, list):
            return []

        # Extract GitHub teams (format: mozilla/team_name or org/team_name)
        teams = []
        for owner in owners:
            if isinstance(owner, str) and "/" in owner and "@" not in owner:
                teams.append(owner)

        return teams
    except Exception as e:
        print(f"Warning: Could not parse {metadata_file}: {e}", file=sys.stderr)
        return []


def get_dataset_from_path(metadata_file, sql_dir):
    """Extract dataset name from metadata file path."""
    try:
        # Path structure: sql/project/dataset/table/metadata.yaml
        relative_path = metadata_file.relative_to(sql_dir)
        parts = relative_path.parts
        if len(parts) >= 3:
            return parts[1]  # dataset is the second part after project
        return None
    except Exception:
        return None


def collect_all_teams(sql_dir):
    """Collect all teams and their associated datasets."""
    metadata_files = find_metadata_files(sql_dir)

    teams_to_datasets = defaultdict(set)
    datasets_to_teams = defaultdict(set)

    for metadata_file in metadata_files:
        teams = extract_teams_from_metadata(metadata_file)
        dataset = get_dataset_from_path(metadata_file, sql_dir)

        for team in teams:
            if dataset:
                teams_to_datasets[team].add(dataset)
                datasets_to_teams[dataset].add(team)

    return teams_to_datasets, datasets_to_teams


def list_all_teams(teams_to_datasets):
    """List all teams found in metadata files."""
    print("GitHub teams found in metadata.yaml files:\n")

    if not teams_to_datasets:
        print("No GitHub teams found.")
        return

    # Sort teams alphabetically
    for team in sorted(teams_to_datasets.keys()):
        datasets = sorted(teams_to_datasets[team])
        dataset_list = ", ".join(datasets[:5])
        if len(datasets) > 5:
            dataset_list += f", ... ({len(datasets)} total)"
        print(f"  {team}")
        print(f"    Datasets: {dataset_list}\n")


def recommend_teams_for_dataset(dataset_query, teams_to_datasets, datasets_to_teams):
    """Recommend teams based on dataset name or keyword."""
    print(f"Recommended teams for '{dataset_query}':\n")

    # Direct dataset match
    matching_datasets = [d for d in datasets_to_teams if dataset_query.lower() in d.lower()]

    if matching_datasets:
        all_teams = set()
        for dataset in matching_datasets:
            all_teams.update(datasets_to_teams[dataset])

        if all_teams:
            print("Teams managing similar datasets:")
            for team in sorted(all_teams):
                print(f"  {team}")
            print()
        else:
            print("No teams found managing similar datasets.\n")
    else:
        # Search in team names
        matching_teams = [t for t in teams_to_datasets if dataset_query.lower() in t.lower()]

        if matching_teams:
            print("Teams with matching names:")
            for team in sorted(matching_teams):
                print(f"  {team}")
            print()
        else:
            print(f"No teams found matching '{dataset_query}'.")
            print("\nTip: Try a broader search term or list all teams with no arguments.\n")


def search_teams(search_term, teams_to_datasets):
    """Search for teams containing a specific term."""
    print(f"Teams matching '{search_term}':\n")

    matching_teams = [t for t in teams_to_datasets if search_term.lower() in t.lower()]

    if matching_teams:
        for team in sorted(matching_teams):
            datasets = sorted(teams_to_datasets[team])
            dataset_list = ", ".join(datasets[:5])
            if len(datasets) > 5:
                dataset_list += f", ... ({len(datasets)} total)"
            print(f"  {team}")
            print(f"    Datasets: {dataset_list}\n")
    else:
        print(f"No teams found matching '{search_term}'.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Detect GitHub teams from metadata.yaml files"
    )
    parser.add_argument(
        "--dataset",
        help="Recommend teams for a specific dataset or keyword"
    )
    parser.add_argument(
        "--search",
        help="Search for teams containing a specific term"
    )
    parser.add_argument(
        "--sql-dir",
        default="sql",
        help="Path to sql directory (default: sql)"
    )

    args = parser.parse_args()

    # Find sql directory
    sql_dir = Path(args.sql_dir)
    if not sql_dir.exists():
        print(f"Error: SQL directory not found: {sql_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect all teams
    teams_to_datasets, datasets_to_teams = collect_all_teams(sql_dir)

    # Execute requested action
    if args.dataset:
        recommend_teams_for_dataset(args.dataset, teams_to_datasets, datasets_to_teams)
    elif args.search:
        search_teams(args.search, teams_to_datasets)
    else:
        list_all_teams(teams_to_datasets)


if __name__ == "__main__":
    main()
