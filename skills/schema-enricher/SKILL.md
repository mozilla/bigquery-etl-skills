---
name: schema-enricher
description: Use this skill to enrich schema.yaml files for BigQuery tables in the bigquery-etl repository. Handles creating schema.yaml when it doesn't exist, finding and filling missing column descriptions (from base schemas, query context, or application context), validating columns against the query, and generating a summary with recommendations for where to add new descriptions (global.yaml, <dataset_name>.yaml, or app_<name>.yaml). Works with column-description-finder skill.
---

# Schema Enricher

**Composable:** Orchestrates column-description-finder (for finding descriptions)
**When to use:** Creating a new schema.yaml, filling missing column descriptions, validating schema columns against the query output, or auditing an existing schema for completeness

## 🚨 REQUIRED READING - Start Here

**BEFORE performing any schema work, review the following:**

1. **Column description sources — note:** Base schema files (`global.yaml`, `app_<name>.yaml`, dataset-specific YAML) are fetched live from GitHub by the `column-description-finder` skill in Step 0c. Do not read these files inline — wait for the skill invocation in Step 0c.

2. **Schema YAML conventions:** READ `references/schema_yaml_conventions.md`
   - Field types, modes, description quality standards
   - Canonical field names and how aliases work

3. **Result file format:** READ `assets/missing_descriptions_template.yaml`
   - Template for capturing columns whose descriptions were derived from query context or inferred from application context (i.e., not found in a base schema)
   - Used to recommend additions to base schema files

## Workflow

### Step 0: Audit base schema coverage using `column-description-finder` ⚠️ MANDATORY — do not skip

**BEFORE looking up any column descriptions**, invoke the `column-description-finder` skill to audit base schema coverage. The skill fetches live base schema files from GitHub and uses deterministic scripts — avoiding the hallucination risk of reading files inline.

**0a — Identify the applicable schemas:**
- If `metadata.yaml` exists, check for an `app_schema:` field (e.g., `app_newtab`). If absent, proceed without an app schema flag.
- Note the dataset name for dataset-specific schema lookup.

**0b — Confirm schema.yaml and query file:**
- Check for `query.sql` and read it to understand SELECT output columns:
  - **If `query.sql` exists:** read it ✓
  - **If only `query.py` exists:** note it — Step 3 column validation will be skipped since column output cannot be reliably parsed from Python
- Check whether `schema.yaml` exists:
  - **If it exists:** proceed to Step 0c
  - **If it does not exist:** generate it first:
    ```bash
    ./bqetl query schema update <dataset>.<table>
    ```
    Then read the generated `schema.yaml` before proceeding to Step 0c.

**0c — Invoke `column-description-finder` skill:**

Run the audit script with the appropriate flags:
```bash
# With app schema:
python scripts/audit_base_schema_coverage.py <dataset>.<table> --app-schema <app_schema> --dataset-schema

# Without app schema:
python scripts/audit_base_schema_coverage.py <dataset>.<table> --dataset-schema
```

Capture the full output — it identifies:
- Columns covered by base schemas (and which file covers each)
- Columns with existing descriptions not in base schemas
- Columns with no description at all

⚠️ **Wait for the skill to complete and capture its full output before proceeding to Step 1.**

### Step 1: Categorize columns from audit output

Using the audit output from Step 0c, categorize every column:

| Column status | Source | Action |
|---|---|---|
| Covered by live base schema | audit output (column → source file) | Use the base schema description |
| Has own description | audit output | Retain existing description |
| No description (not in live schemas) | audit output | Check local base schema files first; if found → `local_only_base_schema_columns`; if not → flag for Step 2 |

**Checking local base schema files:** The `column-description-finder` audit fetches schemas live from GitHub. If a base schema file exists locally but not on GitHub main (returns 404 when WebFetched), the audit will not find descriptions from it. For columns marked "no description" by the audit:

1. Check local `bigquery_etl/schema/*.yaml` files for a match
2. If found — the description is valid but sourced from a **local-only** file. Tag the column as `local-only` and capture it in `local_only_base_schema_columns` in Step 6.
3. If not found in any local file either — flag for description fill in Step 2.

Base schema priority order applied by the audit script is defined in `column-description-finder/references/column_definition_yaml_guide.md` (app-specific → dataset-specific → global).

Proceed to Step 2 for all columns with no description in any base schema (live or local).

### Step 2: Fill missing descriptions

For each column without a current description in schema.yaml, use this priority order:

1. **Base schemas** — descriptions are already identified in the Step 0c audit output. Apply them directly from the audit results.

2. **Query context** — examine `query.sql` to understand what the column computes:
   - Aggregation of clicks → "Total number of clicks recorded"
   - Boolean flag → "Whether [feature] is enabled for this user"
   - Dimension from source → copy description from source schema.yaml if available

3. **Application context** — if no query context is clear, derive description from:
   - Column name semantics
   - Dataset/product area (e.g., newtab, pocket, topsites, search)
   - Related columns nearby in the schema

**⚠️ For any column whose description came from query context (item 2) or application context (item 3) — i.e., not from a base schema — capture it in `<table_name>_missing_metadata.yaml` (Step 6).**

#### Nested RECORD fields

Base schema matching covers top-level fields only (as noted in the Step 0c audit output). For nested fields within RECORD types, apply the same priority order as above — query context first, then application context. Descriptions derived from query context or application context for nested fields should also be captured in `<table_name>_missing_metadata.yaml`. Quality check (Step 4) applies to nested field descriptions as well.

### Step 3: Validate columns

Compare columns in `schema.yaml` against the query's SELECT output. Skip this step if only `query.py` exists (noted in Step 0b).

⚠️ **This command may update `schema.yaml` on disk.** Do NOT re-read `schema.yaml` after running — continue working from the field list and descriptions established in Steps 1–2. Use the command output (diff) only to identify structural additions and removals; apply those changes to your in-memory enriched schema, then write everything in Step 5.

```bash
./bqetl query schema update <dataset>.<table>
```

Review the diff to identify:
- **Columns in query but missing from schema.yaml** → add them with descriptions (check Step 0c audit output first; fall back to Step 2 priority order if not found)
- **Columns in schema.yaml but not in query** → flag for removal (confirm with user before deleting)
- **Type mismatches** → correct to match query output

### Step 4: Description quality check

Every description — whether sourced from a base schema, retained from the existing schema.yaml, or inferred from context — is verified against:

- [ ] Not empty or null
- [ ] Not a restatement of the column name
- [ ] States what the value represents (count, flag, dimension, rate)
- [ ] Consistent with data type
- [ ] Contextually accurate for the product domain

Failing descriptions are corrected automatically.

### Step 5: Write schema.yaml

Write the enriched `schema.yaml` preserving field order, names, types, and modes. Only `description:` entries are added or updated.

On write failure: attempt write to `schema_enriched_draft.yaml` in the same directory and report the alternate path.

Then read back the written file and confirm:
- [ ] All original fields are present
- [ ] Every field has a non-empty description
- [ ] No fields renamed or removed
- [ ] Field count matches pre-write count (plus any additions from Step 3)

Then validate the schema against BigQuery:
```bash
./bqetl query schema validate <dataset>.<table>
```

On verification or validation failure: report which fields are missing/incorrect and attempt automatic remediation.

### Step 6: Write `<table_name>_missing_metadata.yaml` (if non-live-base-schema descriptions were needed)

**Create this file if ANY of the following is true:**
- One or more columns required description from query context or application context (Step 2)
- One or more columns were matched from a **local-only** base schema file (Step 1)

Write to:
```
bigquery_etl/schema/missing_metadata/<table_name>_missing_metadata.yaml
```

Structure — READ `assets/missing_descriptions_template.yaml` and COPY its format. The block below is a structural preview only; if it differs from the template file, the template is authoritative:

```yaml
table: "<project>.<dataset>.<table>"
generated_date: "<YYYY-MM-DD>"

# Section 1: Columns whose descriptions came from query context or application context
# (not found in any base schema — live or local)
missing_columns:
  - name: "<column_name>"
    type: "<BigQuery type>"
    mode: "<NULLABLE|REQUIRED|REPEATED>"
    inferred_description: >-
      <Description derived from query context or application/product context.>
    inference_basis: "<column name semantics | related column | product domain | data type signal | query context>"
    recommended_target: "<global.yaml | app_<name>.yaml | <dataset_name>.yaml>"
    recommendation_reason: >-
      <Why this column belongs in the recommended target.>

# Section 2: Columns matched in LOCAL-ONLY base schema files
# (descriptions are valid but sourced from files not yet on GitHub main)
local_only_base_schema_columns:
  - name: "<column_name>"
    type: "<BigQuery type>"
    mode: "<NULLABLE|REQUIRED|REPEATED>"
    description: >-
      <Description sourced from the local-only base schema file.>
    source_file: "<app_<name>.yaml | <dataset_name>.yaml>"
    source_status: "local-only — not on GitHub main"
    recommended_action: >-
      Merge <source_file> to GitHub main to make this description authoritative.
```

**Omit a section entirely if it has no entries.**

**`recommended_target` rules for `missing_columns`** — this is also the decision logic for choosing which base schema file to recommend:

| Condition | Target |
|---|---|
| Column useful across many datasets/products | `global.yaml` |
| Column specific to one product (newtab, pocket, ads) | `app_<product_name>.yaml` |
| Column specific to one dataset | `<dataset_name>.yaml` |

If neither condition is met, skip this step and note in the summary:
`<table_name>_missing_metadata.yaml not created — all columns matched in live base schemas`

### Step 7: Write summary markdown file ⚠️ MANDATORY — do not skip

Write a summary markdown file to:
```
bigquery_etl/schema/missing_metadata/<table_name>-metadata-summary.md
```

Use the Write tool to create this file with the following structure:

```markdown
# Schema Enricher — Metadata Summary

**Table:** `<project>.<dataset>.<table>`
**Run date:** <YYYY-MM-DD>

---

## Phase Results

| Phase (Step) | Status | Notes |
|---|---|---|
| Discovery (Step 0) | ✅/❌ | Base schemas found |
| Categorization (Step 1) | ✅/❌ | X covered, Y retained, Z flagged |
| Description Fill (Step 2) | ✅/❌ | X from base schemas, Y from query/application context |
| Column Validation (Step 3) | ✅/❌/⏭️ | X/Y match query output (or: skipped — only query.py exists) |
| Quality Check (Step 4) | ✅/❌ | X descriptions pass |
| Write (Step 5) | ✅/❌ | schema.yaml written |
| Verification (Step 5) | ✅/❌ | All fields confirmed |

---

## Base Schema Coverage

| Column | Matched Field | Source File | Source Status | Alias Used |
|---|---|---|---|---|
| <column_name> | <matched_field> | <source_file> | live | no |
| <column_name> | <canonical_name> | <source_file> | live | yes (alias: <column_name>) |
| <column_name> | <matched_field> | <source_file> | local-only | no |
| <column_name> | — | (none) | inferred | — |

---

## Local-Only Base Schema Columns

| Column | Source File | Recommended Action |
|---|---|---|
| <column_name> | <source_file> | Merge <source_file> to GitHub main |

*(Omit this section if all matched base schemas are live)*

---

## Non-Base-Schema Descriptions

| Column | Description | Inference Basis | Recommended Base Schema |
|---|---|---|---|
| <column_name> | <description> | <query context \| application context> | <global.yaml \| app_<name>.yaml \| <dataset_name>.yaml> |

*(Omit this section if no columns required inference)*

---

## Column Validation Results

_(If Step 3 was skipped because only query.py exists, write: "Column validation skipped — only query.py exists")_

- **Columns added (missing from schema):** [list or "none"]
- **Columns removed (not in query):** [list or "none"]
- **Type corrections:** [list or "none"]

---

## Output Files

- `sql/<project>/<dataset>/<table>/schema.yaml` — enriched with all X descriptions
- `bigquery_etl/schema/missing_metadata/<table_name>_missing_metadata.yaml` — Y inferred descriptions + Z local-only base schema columns
  (or: `<table_name>_missing_metadata.yaml` not created — all columns matched in live base schemas)
- `bigquery_etl/schema/missing_metadata/<table_name>-metadata-summary.md` — this summary file
```

### Step 8: Completion checklist ⚠️ VERIFY before declaring task complete

Before reporting done, confirm all required output files have been written using the Read tool or ls:

- [ ] `sql/<project>/<dataset>/<table>/schema.yaml` — every field has a non-empty description
- [ ] `bigquery_etl/schema/missing_metadata/<table_name>-metadata-summary.md` — summary markdown written
- [ ] `bigquery_etl/schema/missing_metadata/<table_name>_missing_metadata.yaml` — written if any columns required inference OR came from local-only base schemas; explicitly noted as not created if all columns matched in live base schemas

If any file is missing, create it before proceeding.

## Integration with Other Skills

| Skill | When to invoke |
|-------|----------------|
| `column-description-finder` | **Always** — invoked in Step 0c to audit base schema coverage using live GitHub schema files |

## Key Commands

```bash
# Generate schema structure from query output (Step 0b)
./bqetl query schema update <dataset>.<table>

# Validate schema against BigQuery (Step 5)
./bqetl query schema validate <dataset>.<table>
```
