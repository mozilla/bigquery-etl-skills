---
name: base-schema-audit
description: Use this skill to audit tables for missing column descriptions and classify each missing column into the correct base schema promotion target (global.yaml, app_<product>.yaml, or <dataset_name>.yaml). Accepts a dataset name and an optional table filter — omit the filter to audit all tables in the dataset. Outputs a per-column recommended_target report for use in _missing_metadata.yaml. Composable with schema-enricher (Step 6).
---

# Base Schema Audit

**Composable:** Feeds into schema-enricher Step 6 (`_missing_metadata.yaml` `recommended_target` fields)
**When to use:** Before schema enrichment, when onboarding a new product area, or when auditing an existing dataset for base schema promotion opportunities

## Inputs

| Input | Required | Description |
|---|---|---|
| `dataset` | Yes | Dataset name under `sql/moz-fx-data-shared-prod/` (e.g. `telemetry_derived`, `firefox_desktop_derived`) |
| `table_filter` | No | Glob-style prefix to narrow scope (e.g. `newtab*`, `clients*`). Omit to audit all tables in the dataset. |

**Example invocations:**
```
# All tables in a dataset
Use the base-schema-audit skill for telemetry_derived

# Tables matching a prefix
Use the base-schema-audit skill for telemetry_derived, filter to newtab* tables

# Another dataset, no filter
Use the base-schema-audit skill for firefox_desktop_derived
```

## Workflow

### Step 1: Discover base schemas

List all available base schema files:
```bash
ls bigquery_etl/schema/*.yaml
```

Read each file and record every field name and its aliases. Note which
`app_<product>.yaml` and `<dataset_name>.yaml` files exist — this determines
which product namespaces and datasets have dedicated schema files.

### Step 2: Collect target tables

List all table directories under `sql/moz-fx-data-shared-prod/<dataset>/`.
If a `table_filter` was provided, restrict to directories whose name matches
the filter (prefix match). If no filter was provided, include all directories.

For each table directory, verify a `schema.yaml` exists. Skip directories
without one and note them in the summary.

### Step 3: Find missing descriptions per table

For each table, read `schema.yaml` and collect every field (including nested
sub-fields within RECORD types) whose `description` is empty or absent.

Then invoke the `column-description-finder` skill to audit base schema
coverage:

```bash
# With app schema (from metadata.yaml app_schema: <name>):
python scripts/audit_base_schema_coverage.py <dataset>.<table> --app-schema <app_schema> --dataset-schema --missing-only

# Without app schema:
python scripts/audit_base_schema_coverage.py <dataset>.<table> --dataset-schema --missing-only
```

Columns already covered by a base schema need no further action — exclude them
from the decision tree below.

### Step 4: Apply the promotion decision tree

**READ `references/base_schema_classification_guide.md`** for the full
decision tree. Apply it to every remaining missing column (those not covered
by any base schema).

Decision tree summary (apply in order — stop at first match):

1. **Product namespace check** — does the column name contain a product-specific
   prefix or describe a product feature? → `app_<product>.yaml`  ← **check this first**
2. **Cross-dataset breadth** — does it appear in 2+ distinct datasets and is generic?
   → `global.yaml`
3. **Single-dataset generic** — appears in only one dataset and is generic?
   → `<dataset_name>.yaml`
4. **Ambiguous** — flag for human review

### Step 5: Report results

For each table, output a table of missing columns:

| Column | Type | Mode | Step | Recommended Target | Reason |
|---|---|---|---|---|---|
| `<name>` | `<type>` | `<mode>` | 1/2/3/ambiguous | `<file>` | one-line justification |

Then output a cross-table summary:

```
Dataset: <dataset>  Tables audited: N  Tables skipped (no schema.yaml): M

Recommended target breakdown:
  app_<product>.yaml    : X columns across Y tables
  global.yaml           : X columns across Y tables
  <dataset_name>.yaml   : X columns across Y tables
  ambiguous             : X columns — human review needed

Base schema files that do not yet exist but would be needed:
  (list any app_<product>.yaml files Step 1 would require but that are absent)
```

## Integration with Other Skills

| Skill | Relationship |
|---|---|
| `column-description-finder` | Invoked in Step 3 to identify base-schema-covered columns |
| `schema-enricher` | Consumes this skill's output — `recommended_target` values populate `_missing_metadata.yaml` Step 6 |

## Key Reference

- Decision tree: `references/base_schema_classification_guide.md`
