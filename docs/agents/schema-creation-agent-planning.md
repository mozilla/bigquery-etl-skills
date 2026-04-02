# Schema Creation Agent — Project Planning & Design

**Agent:** Schema Creation Agent<br>
**Document type:** Project Planning & Design<br>
**Project:** Metadata Completeness Project<br>
**Status:** Draft<br>
**Author:** Gaurang Katre<br>
**Last updated:** 2026-04-01<br>

---

## 1. Overview

The **Schema Creation Agent** is a two-phase autonomous agent in the `bigquery-etl-skills` plugin that fully automates documentation for BigQuery tables in the Mozilla `bigquery-etl` repository. Given a target table identifier, it enriches `schema.yaml` with column descriptions and generates a rich-style `README.md` — two tasks that were previously manual and time-consuming.

The agent is powered by the `claude-opus-4-6` model and orchestrates two specialist skills:

| Skill | Phase | Role                                |
|---|---|-------------------------------------|
| `schema-enricher` | Phase 1 | Creates or enriches `schema.yaml`<br>Uses the sub-skill `column-description-finder` to search the base metadata schema for the description |
| `schema-readme-generator` | Phase 2 | Creates or updates `README.md`      |

---

## 2. Problem Statement

BigQuery tables in `bigquery-etl` frequently lack:

- **Column descriptions** in `schema.yaml` — making it hard for analysts to understand field semantics
- **README.md documentation** — leaving downstream consumers without context on grain, data flow, key metrics, or example queries

Filling these manually requires engineers to cross-reference multiple files (`query.sql`, `metadata.yaml`, `schema.yaml`, base schema YAMLs), apply consistent formatting conventions, and write SQL examples — a repetitive process prone to inconsistency and omission.

---

## 3. Goals / Non-Goals

### Goals

- Automate end-to-end schema documentation for any BigQuery table in `bigquery-etl`
- Produce `schema.yaml` with complete, accurate, contextually correct column descriptions for every field
- Produce a rich-style `README.md` following established layout conventions (emoji headings, Mermaid data flow, graduated SQL examples, metadata overview table)
- Surface non-base-schema descriptions for upstream promotion via `_missing_metadata.yaml`
- Report a clear completion summary after both phases

### Non-Goals

- Does not modify query logic (`query.sql` / `query.py`)
- Does not create or update `metadata.yaml` — expects it to be present and complete before invocation
- Does not maintain base metadata YAML files (global.yaml, app_<product>.yaml, <dataset>.yaml)
- Does not push changes to GitHub or open pull requests (in this iteration)
- Does not look up glean dictionary for missing descriptions (in this iteration)
- Does not run BigQuery queries or validate data at runtime
- Not intended for minimal-style READMEs such as UDFs and single-consumer tables

---

## 4. Scope

**In scope:**

- Tables with `query.sql` (standard incremental or full-refresh queries)
- Tables with or without an existing `schema.yaml` (generates if absent)
- Tables with or without an existing `README.md` (generates or updates)
- Any dataset in `moz-fx-data-shared-prod` following standard `bigquery-etl` directory layout

**Out of scope:**

- UDFs, static reference tables, and single-consumer tables
- Tables requiring custom DAG setup
- Multi-table batch runs (invoke agent once per table)

---

## 5. Architecture

```
User invokes: schema-creation-agent <project>.<dataset>.<table>
                            │
              ┌─────────────▼──────────────┐
              │      Phase 1 (Blocking)    │
              │      schema-enricher       │
              │                            │
              │  ┌──────────────────────┐  │
              │  │ column-description-  │  │
              │  │ finder (sub-skill)   │  │
              │  └──────────────────────┘  │
              └─────────────┬──────────────┘
                            │ schema.yaml enriched
              ┌─────────────▼──────────────┐
              │       Phase 2 (Non-        │
              │         blocking)          │
              │   schema-readme-generator  │
              └─────────────┬──────────────┘
                            │
              ┌─────────────▼──────────────┐
              │     Completion Summary     │
              └────────────────────────────┘
```

**Key structural properties:**

- Phase 1 is **blocking**: if `schema-enricher` fails, the agent stops and reports the error. `schema.yaml` must be complete before README generation can proceed.
- Phase 2 is **non-blocking**: if `schema-readme-generator` fails, the agent logs the error, skips README generation, and notes it in the completion summary.
- The agent uses the **Opus model** for stronger reasoning across multi-file synthesis tasks.

---

## 6. Inputs

| Input | Required | Description |
|---|---|---|
| `<project>.<dataset>.<table>` | Yes | Fully qualified table identifier (e.g., `moz-fx-data-shared-prod.telemetry_derived.newtab_daily_interactions_aggregates_v1`) |
| `query.sql` | Recommended | SQL query defining table output; drives column validation and README Data Flow / How It Works sections |
| `query.py` | Alternative | Python ETL script; column validation and some README sections will be skipped |
| `metadata.yaml` | Recommended | DAG name, partition field, clustering fields, retention policy, owners; drives README Overview table |
| `schema.yaml` | Optional | Existing schema; generated via `./bqetl query schema update` if absent |

**Base schema files** (fetched live from GitHub by `column-description-finder`):

| File | Scope |
|---|---|
| `global.yaml` | Cross-product canonical field descriptions |
| `app_<name>.yaml` | Product-specific descriptions (e.g., `app_newtab.yaml`) |
| `<dataset_name>.yaml` | Dataset-specific descriptions |

---

## 7. Outputs

| File | Written by | Description |
|---|---|---|
| `sql/<project>/<dataset>/<table>/schema.yaml` | `schema-enricher` | Enriched with complete column descriptions |
| `sql/<project>/<dataset>/<table>/README.md` | `schema-readme-generator` | Rich-style documentation (150–170 lines) |
| `bigquery_etl/schema/missing_metadata/<table>_missing_metadata.yaml` | `schema-enricher` | Non-base-schema descriptions with promotion recommendations (only created if needed) |
| `bigquery_etl/schema/missing_metadata/<table>-metadata-summary.md` | `schema-enricher` | Phase-by-phase run summary (always created) |

---

## 8. Workflow

### Phase 1 — Schema Enrichment (`schema-enricher`)

1. **Step 0 — Audit base schema coverage**
   - Check `metadata.yaml` for `app_schema:` field
   - Confirm `schema.yaml` exists; generate via `./bqetl query schema update` if absent
   - Invoke `column-description-finder` to audit which columns are covered by base schemas (fetches live files from GitHub)

2. **Step 1 — Categorize columns**
   - Covered by base schema → use base schema description
   - Has existing description → retain
   - No description → flag for description fill

3. **Step 2 — Fill missing descriptions** (priority order — see Section 9)

4. **Step 3 — Validate columns** (skipped if only `query.py` exists)
   - Run `./bqetl query schema update` and review diff
   - Add columns missing from schema, flag extras, correct type mismatches

5. **Step 4 — Quality check**
   - Every description: non-empty, not a name restatement, states what the value represents, type-consistent, contextually accurate

6. **Step 5 — Write and verify `schema.yaml`**
   - Preserve field order, names, types, modes; only update `description:` entries
   - Read back written file and confirm field count, completeness, no renames
   - Run `./bqetl query schema validate <dataset>.<table>`

7. **Step 6 — Write `_missing_metadata.yaml`** (only if non-base-schema descriptions were needed)

8. **Step 7 — Write metadata summary** (`<table>-metadata-summary.md`) — always written

### Phase 2 — README Generation (`schema-readme-generator`)

1. **Step 1 — Read source files**
   - `query.sql`: FROM clause, GROUP BY dimensions, aggregated metrics, `@param` name
   - `metadata.yaml`: DAG name, partition field, clustering fields, retention, owners
   - `schema.yaml` (fully enriched from Phase 1): field names and descriptions

2. **Step 2 — Check for existing README.md**
   - Exists → read it, identify sections to update
   - Does not exist → generate from template

3. **Step 3 — Write README.md** using `assets/readme_template.md`, filling all placeholders:
   - **📌 Overview** — metadata table from `metadata.yaml` + use cases
   - **🗺️ Data Flow** — Mermaid `flowchart TD` (3 nodes: source → this query → partitioned table)
   - **🧠 How It Works** — 4–5 numbered steps; Step 5 must state data inclusion/exclusion policy
   - **🧾 Key Fields** — Dimensions and Metrics sub-tables; omit Search / [Product] config rows if not applicable
   - **🧩 Example Queries** — exactly 3, graduated (basic → segmentation → attribution/advanced)
   - **🔧 Implementation Notes** — 3–5 bullets
   - **📌 Notes & Conventions** — key field and metric semantic definitions from `schema.yaml`
   - **🗃️ Schema & Related Tables** — schema.yaml link + upstream + downstream

4. **Step 4 — Conciseness check**
   - Total line count ≤ 170
   - No separate sections for Scheduling, Storage, Owners, Retention (all in Overview table)
   - SQL examples use `GROUP BY 1, 2` shorthand
   - How It Works uses single-line numbered steps
   - How It Works Step 5 explicitly states data inclusion/exclusion policy

5. **Step 5 — Write, read back, and verify**
   - Confirm all sections present and in order
   - No `{placeholder}` tokens remain (exception: `query.py`-only tables may have partial Data Flow / How It Works)
   - Line count within target

### Completion Summary

After both phases, the agent reports:

| Phase | Result |
|---|---|
| Schema Enrichment | Fields enriched, descriptions filled per tier, validation result |
| README | Created / updated / skipped with reason |

Lists all output files written.

---

## 9. Description Priority Order

When filling a missing column description, the agent applies this strict priority:

| Priority | Source | When used |
|---|---|---|
| 1 (highest) | `app_<name>.yaml` (product-specific base schema) | Column matches a field in the app schema |
| 2 | `<dataset_name>.yaml` (dataset-specific base schema) | Column matches a field in the dataset schema |
| 3 | `global.yaml` (cross-product canonical) | Column matches a globally defined field |
| 4 | Upstream source `schema.yaml` | No base schema match; column is a pass-through dimension — copy description from source table's `schema.yaml` |
| 5 | Query context | No base schema match; description derived from what the column computes in `query.sql` |
| 6 (lowest) | Application context | No base schema match and query context is unclear; derived from column name semantics, product domain, and related columns |

Descriptions from priorities 4, 5, and 6 are captured in `_missing_metadata.yaml` for future promotion to base schemas.

---

## 10. How Base Schema and Query Context Work

### Base Schema — Three-Tier Hierarchy

Base schemas are shared YAML files defining canonical column descriptions for reuse across many tables. The `column-description-finder` skill fetches these live from GitHub on every run.

| Tier | File | Scope | Example                                                                              |
|---|---|---|--------------------------------------------------------------------------------------|
| 1 (highest) | `app_<name>.yaml` | Columns specific to one product (newtab, ads) | `app_newtab.yaml` defines fields like `pocket_enabled`                               |
| 2 | `<dataset_name>.yaml` | Columns specific to one dataset | `firefox_desktop_derived.yaml` defines fields shared across firefox_desktop_derived tables |
| 3 (lowest) | `global.yaml` | Columns shared across many products and datasets | `submission_date`, `country_code`, `channel`, `os`                                   |

**How matching works:** For each column in `schema.yaml`, the audit script checks tiers in order (app → dataset → global) using exact name and alias matching. The first tier that matches wins.

> **Example:** The column `submission_date` is defined in `global.yaml` — every table with this column receives its description automatically.

### Priority 4 — Upstream Source `schema.yaml`

When a column has no base schema match and appears to be a pass-through dimension from a source table, the agent locates that table's `schema.yaml` under `sql/` and copies the description directly.

**How it works:**
1. Parse the FROM clause of `query.sql` to identify source table(s)
2. Locate the source table directory under `sql/<project>/<dataset>/<table>/` and read its `schema.yaml`
3. If the column exists and has a description, copy it directly
4. If the upstream `schema.yaml` is absent or the column has no description there, fall through to priority 5

> **Note:** Descriptions copied from an upstream `schema.yaml` are still captured in `_missing_metadata.yaml` because they are not from a base schema file.

### Priority 5 — Query Context

When neither base schemas nor upstream `schema.yaml` provide a description, the agent examines the SQL expression in `query.sql`:

| SQL expression | Derived description |
|---|---|
| `SUM(click_count)` | Total number of clicks recorded |
| `COUNT(DISTINCT client_id)` | Number of unique clients with at least one interaction |
| `SAFE_DIVIDE(clicks, impressions)` | Click-through rate calculated as clicks divided by impressions |
| `MAX(experiment_branch)` | The experiment branch associated with this client |
| `COALESCE(pocket_enabled, FALSE)` | Whether the Pocket feature is enabled; defaults to FALSE when not set |

### Priority 6 — Application Context (Last Resort)

If the SQL expression alone does not reveal the column's meaning, the agent derives a description from column name semantics, the product domain (newtab, search, ads), and nearby related columns.

> **All priorities 4–6:** descriptions are always written to `_missing_metadata.yaml` with a recommended target file for future promotion to base schemas.

---

## 11. Developer Guide — Using the Agent

### Installation

The agent and its skills are distributed as a Claude Code plugin. Install once per machine:

```bash
# Install the bigquery-etl-skills plugin
claude plugin install bigquery-etl-skills
```

This registers the following components with Claude Code:

| Component | Type | Installed as |
|---|---|---|
| `schema-creation-agent` | Agent | `/agents/schema-creation-agent.md` |
| `schema-enricher` | Skill | `/skills/schema-enricher/SKILL.md` |
| `schema-readme-generator` | Skill | `/skills/schema-readme-generator/SKILL.md` |
| `column-description-finder` | Skill | `/skills/column-description-finder/SKILL.md` |

After installation, verify the agent and skills are registered:

```bash
ls ~/.claude/plugins/cache/bigquery-etl-skills/bigquery-etl-skills/*/agents/
ls ~/.claude/plugins/cache/bigquery-etl-skills/bigquery-etl-skills/*/skills/
```

Expected output includes `schema-creation-agent.md` in agents and `schema-enricher`, `schema-readme-generator`, `column-description-finder` in skills.

### Prerequisites

| Prerequisite | Required? | Notes |
|---|---|---|
| `bigquery-etl-skills` plugin installed | Yes | Provides the agent and all dependent skills |
| bigquery-etl repo cloned locally | Yes | Agent reads `query.sql`, `metadata.yaml`, `schema.yaml` from disk |
| bqetl CLI installed and authenticated | Yes | Used to generate and validate `schema.yaml` |
| `query.sql` or `query.py` present | Yes | At minimum `query.py`; `query.sql` preferred for full functionality |
| `metadata.yaml` complete | Recommended | Must be present and complete before invoking the agent |
| `schema.yaml` present | Optional | Agent generates it automatically if missing |

### Step-by-Step: Invoking the Agent

1. **Identify the target table.** Fully qualified format: `<project>.<dataset>.<table_version>`. Example:
   `moz-fx-data-shared-prod.telemetry_derived.newtab_daily_interactions_aggregates_v1`

2. **Verify prerequisites.** Confirm `query.sql` (or `query.py`) and `metadata.yaml` exist and are complete before proceeding.

3. **Invoke the agent:**
   `Run schema-creation-agent for telemetry_derived.newtab_daily_interactions_aggregates_v1`

4. **Monitor Phase 1.** The agent audits base schema coverage, fills descriptions using the 6-tier priority order, validates columns, writes and verifies `schema.yaml`, then writes the summary report.

5. **Review Phase 1 outputs.** Check: fields enriched per tier, whether `_missing_metadata.yaml` was created, BigQuery validation result.

6. **Monitor Phase 2.** The agent reads the enriched `schema.yaml`, `query.sql`, and `metadata.yaml` to generate `README.md`.

7. **Review README.md.** Verify all 8 sections are present, the Mermaid diagram is correct, and 3 example queries use representative fields.

8. **Commit the output files.**

### Output Files

| File | Always created? | Description |
|---|---|---|
| `sql/<project>/<dataset>/<table>/schema.yaml` | Yes | Enriched with complete column descriptions |
| `sql/<project>/<dataset>/<table>/README.md` | Yes (if Phase 2 succeeds) | Rich-style documentation with Mermaid data flow and example queries |
| `bigquery_etl/schema/missing_metadata/<table>-metadata-summary.md` | Yes | Phase-by-phase run summary |
| `bigquery_etl/schema/missing_metadata/<table>_missing_metadata.yaml` | Only if priorities 4–6 were used | Non-base-schema descriptions with recommended promotion targets |

### Handling Common Situations

| Situation | Action |
|---|---|
| `metadata.yaml` is missing or incomplete | Ensure `metadata.yaml` is present and complete before invoking the agent |
| Only `query.py` exists (no `query.sql`) | Invoke as normal — column validation and some README sections skipped and noted in outputs |
| `schema.yaml` does not exist | Auto-generated via `./bqetl query schema update` — no manual action needed |
| Phase 1 fails | Agent stops and reports the error. Resolve the issue before re-invoking |
| Phase 2 fails | `schema.yaml` is already written. Re-invoke `schema-readme-generator` directly without re-running Phase 1 |
| BigQuery validation fails | Agent reports which fields failed. Correct discrepancies and re-run validation manually |
| `_missing_metadata.yaml` was created | Review and consider opening a PR to promote entries to the recommended base schema file |

---

## 12. Error Handling

| Error | Handling |
|---|---|
| `schema-enricher` fails | Report error to user and stop — schema enrichment is a prerequisite for README generation |
| `schema-readme-generator` fails | Log error, skip README generation, note in completion summary |
| `schema.yaml` missing | Auto-generate via `./bqetl query schema update`; proceed |
| `query.py` only (no `query.sql`) | Column validation skipped; README Data Flow and How It Works may be partially filled; noted in outputs |
| `metadata.yaml` absent | README DAG/partitioning/owners sections noted as incomplete |
| Write failure for `schema.yaml` | Attempt write to `schema_enriched_draft.yaml`; report alternate path |
| BigQuery validation failure | Report which fields failed and attempt automatic remediation |

---

## 13. Integration with Skills

| Component | Relationship |
|---|---|
| `schema-enricher` | Phase 1 skill — full schema enrichment workflow |
| `column-description-finder` | Sub-skill invoked by `schema-enricher` in Step 0c — audits base schema coverage by fetching live files from GitHub |
| `schema-readme-generator` | Phase 2 skill — README generation workflow |

---

## 14. Key Design Decisions

**D1 — Two-phase blocking architecture**
Phase 1 (schema enrichment) must complete before Phase 2 (README generation) begins. The README's Notes & Conventions section depends on fully enriched `schema.yaml` descriptions. A failed Phase 1 makes a high-quality README impossible.

**D2 — Non-blocking Phase 2**
README generation failure should not invalidate schema enrichment work. The `schema.yaml` output is the higher-value artifact; README can be regenerated independently.

**D3 — Opus model**
Schema enrichment requires reading and synthesising multiple files (query SQL, three tiers of base schemas, existing schema). The higher reasoning capacity of Opus reduces hallucination risk for description quality and column matching.

**D4 — Column-description-finder fetches live files**
Base schema files are fetched live from GitHub (not read inline) to avoid stale local copies and to reduce hallucination risk in column matching. This is mandatory — the audit script uses deterministic matching.

**D5 — Non-base-schema descriptions are captured, not silently applied**
Descriptions derived from upstream source schema.yaml, query context, or application context are written to `_missing_metadata.yaml` with recommended promotion targets. This creates an auditable record and enables gradual expansion of the base schema coverage, reducing the need for inference over time.

---

## 15. File Conventions

### Directory layout (per table)

```
sql/<project>/<dataset>/<table>/
├── query.sql              # or query.py
├── metadata.yaml
├── schema.yaml            # enriched by Phase 1
└── README.md              # generated by Phase 2
```

### Summary and missing metadata (repo-level)

```
bigquery_etl/schema/missing_metadata/
├── <table_name>_missing_metadata.yaml
└── <table_name>-metadata-summary.md
```

### Naming conventions

| File | Convention |
|---|---|
| Missing metadata | `<table_name>_missing_metadata.yaml` (underscores) |
| Metadata summary | `<table_name>-metadata-summary.md` (hyphens) |
| App base schema | `app_<product_name>.yaml` |
| Dataset base schema | `<dataset_name>.yaml` |

---

## 16. Open Questions & Future Work

| # | Question / Item | Notes                                                                                                 |
|---|---|-------------------------------------------------------------------------------------------------------|
| OQ-1 | Batch mode | Should the agent accept a dataset name and process all tables in one run?                             |
| OQ-2 | Minimal README support | Should the agent detect single-consumer tables and switch to minimal style automatically?             |
| OQ-3 | GitHub PR creation | Should the agent open a PR with the generated files after completion?                                 |
| OQ-4 | Base schema promotion workflow | Should `_missing_metadata.yaml` feed an automated PR to `global.yaml` or `app_<name>.yaml`?           |
| OQ-5 | `query.py` column extraction | Can AST (Abstract Syntax Tree) parsing recover SELECT output columns from Python ETL scripts to enable column validation? |
| OQ-6 | Downstream consumer detection | Can the agent read the `bigquery-etl` DAG graph to auto-populate the README Downstream section?       |

---

## 17. General Feedback

| Name       | Emoji | Comments      |
|------------|-------|---------------|
|            |       |               |
|            |       |               |

---

## 18. Revision History

| Version | Date       | Author        | Changes                                                                                                                                                                                                   |
|---------|------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.1 | 2026-03-24 | Gaurang Katre | Initial draft                                                                                                                                                                                             |
| 0.2 | 2026-04-01 | Gaurang Katre | Added sections 10 and 11 (How Base Schema and Query Context Work; Developer Guide)<br>Promoted upstream source schema.yaml to Priority 4 and renumbered query context to P5 and application context to P6 |
