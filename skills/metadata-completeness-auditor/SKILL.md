---
name: metadata-completeness-auditor
description: Use this skill to audit bigquery-etl tables and datasets for missing metadata completeness — including missing schema column descriptions, missing metadata.yaml top-level descriptions, missing dataset_metadata.yaml descriptions, and missing README.md files at both the dataset and table level. Accepts an optional dataset name to scope the search; defaults to the full project. Outputs a structured report with item lists and summary statistics (counts and percentages).
---

# Metadata Completeness Auditor

**When to use:** Before enrichment sprints, when onboarding a new product area, or when generating a completeness report for a dataset or the full project.

**Composable with:**
- `schema-enricher` — to fill in missing column descriptions found by this audit
- `schema-readme-generator` — to create README.md files for tables identified as missing one
- `metadata-manager` — to add or update description fields in metadata.yaml files
- `base-schema-audit` — for deeper column classification after finding missing schema descriptions

## Inputs

| Input | Required | Description |
|---|---|---|
| `dataset` | No | Dataset name under `sql/moz-fx-data-shared-prod/` (e.g. `telemetry_derived`). Omit to scan all datasets. |
| `--summary-only` | No | Flag to show only summary stats without the full item listing |

**Example invocations:**
```
# Audit all datasets in the project
Use the metadata-completeness-auditor skill

# Audit a single dataset
Use the metadata-completeness-auditor skill for telemetry_derived

# Audit with summary stats only
Use the metadata-completeness-auditor skill for telemetry_derived, summary only

# Audit a dataset, then fix the issues
Use the metadata-completeness-auditor skill for firefox_desktop_derived, then use schema-readme-generator and schema-enricher to fix the gaps
```

## What the Audit Checks

The auditor inspects the following for each dataset and table directory:

| Check | Location | Flagged when |
|---|---|---|
| schema column descriptions | `<table>/schema.yaml` | Any field (including nested) has empty or absent `description` |
| metadata description | `<table>/metadata.yaml` | Top-level `description` key is absent or empty |
| dataset_metadata description | `<dataset>/dataset_metadata.yaml` | `description` key is absent or empty |
| dataset README | `<dataset>/README.md` | File does not exist |
| table README | `<table>/README.md` | File does not exist |

## Workflow

### Step 1: Run the audit script

From the `bigquery-etl` repo root, run:

```bash
# Scoped to one dataset
python scripts/audit_metadata_completeness.py --dataset <dataset_name>

# Full project scan (slow — can take a minute)
python scripts/audit_metadata_completeness.py

# Summary stats only
python scripts/audit_metadata_completeness.py --dataset <dataset_name> --summary-only
```

The script is at:
`skills/metadata-completeness-auditor/scripts/audit_metadata_completeness.py`

Copy it to the `scripts/` directory of the bigquery-etl repo before running, or run it directly with the full path.

### Step 2: Parse and present results

The script outputs:

1. **Summary block** — always shown:
   - Total datasets and tables scanned
   - Count and % of datasets missing `dataset_metadata.yaml` description
   - Count and % of datasets missing `README.md`
   - Count and % of tables missing schema column descriptions
   - Count and % of tables missing `metadata.yaml` description
   - Count and % of tables missing `README.md`

2. **Detail sections** — shown unless `--summary-only`:
   - `DATASETS — dataset_metadata.yaml missing description`
   - `DATASETS — missing README.md`
   - `TABLES — metadata.yaml missing description`
   - `TABLES — missing README.md`
   - `TABLES — schema.yaml has columns with missing descriptions` (lists up to 10 field paths per table)

### Step 3: Present findings to user

Summarize results in a clear table or bullet list:

```
## Metadata Completeness Report: <dataset_name>

### Summary
| Metric | Count | % |
|---|---|---|
| Tables scanned | 255 | — |
| Tables missing schema descriptions | 76 | 29.8% |
| Tables missing metadata description | 27 | 10.6% |
| Tables missing README | 253 | 99.2% |
| Datasets missing README | 1 | 100.0% |

### Next Steps
- Use `schema-readme-generator` to create README.md files for the 253 missing tables
- Use `schema-enricher` to fill descriptions for the 76 tables with missing column descriptions
- Use `metadata-manager` to add descriptions to the 27 metadata.yaml files missing them
```

### Step 4: Offer remediation path

After presenting the report, offer to:
- Generate READMEs for missing tables → invoke `schema-readme-generator`
- Enrich schema descriptions → invoke `schema-enricher`
- Update metadata.yaml descriptions → invoke `metadata-manager`
- Deeper column classification → invoke `base-schema-audit`

Always confirm with the user which gaps they want to address before starting remediation.

## Script Location

The audit script lives at:
```
skills/metadata-completeness-auditor/scripts/audit_metadata_completeness.py
```

Run it from the `bigquery-etl` repo root. The script auto-resolves `sql/moz-fx-data-shared-prod/` as the default project path. Pass `--sql-dir` or `--project` to override defaults.

## Output Example

```
======================================================================
METADATA COMPLETENESS AUDIT — SUMMARY
======================================================================
  Total datasets scanned:                1
  Total tables scanned:                  255

  Datasets missing dataset_metadata desc: 0  (0.0%)
  Datasets missing README:               1  (100.0%)

  Tables with missing schema descriptions: 76  (29.8%)
  Tables with missing metadata desc:     27  (10.6%)
  Tables missing README:                 253  (99.2%)

DATASETS — missing README.md
----------------------------------------------------------------------
  telemetry_derived

TABLES — metadata.yaml missing description
----------------------------------------------------------------------
  telemetry_derived.client_probe_counts_v1
  telemetry_derived.clients_probe_processes_v1
  ...

TABLES — schema.yaml has columns with missing descriptions
----------------------------------------------------------------------
  telemetry_derived.active_users_aggregates_v1
    - attribution_medium
    - attribution_source
    - city
    ...
```
