# Schema Creation Agent — Project Planning & Design

**Agent:** Schema Creation Agent<br>
**Document type:** Project Planning & Design<br>
**Project:** Metadata Completeness Project<br>
**Status:** Draft<br>
**Author:** Gaurang Katre<br>
**Last updated:** 2026-03-24<br>

---

## 1. Overview

The **Schema Creation Agent** is a two-phase autonomous agent in the `bigquery-etl-skills` plugin that fully automates documentation for BigQuery tables in the Mozilla `bigquery-etl` repository. Given a target table identifier, it enriches `schema.yaml` with column descriptions and generates a rich-style `README.md` — two tasks that were previously manual and time-consuming.

The agent is powered by the `claude-opus-4-6` model and orchestrates two specialist skills:

| Skill | Phase | Role |
|---|---|---|
| `schema-enricher` | Phase 1 | Creates or enriches `schema.yaml` |
| `schema-readme-generator` | Phase 2 | Creates or updates `README.md` |

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
- Does not create or update `metadata.yaml` but expects it to be available
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
| Schema Enrichment | Fields enriched, inferences, validation result |
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
| 4 | Query context | No base schema match; description derived from what the column computes in `query.sql` |
| 5 (lowest) | Application context | No base schema match and query context is unclear; derived from column name semantics, product domain, and related columns |

Descriptions from priorities 4 and 5 are captured in `_missing_metadata.yaml` for future promotion to base schemas.

---

## 10. Error Handling

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

## 11. Integration with Skills

| Component | Relationship |
|---|---|
| `schema-enricher` | Phase 1 skill — full schema enrichment workflow |
| `schema-readme-generator` | Phase 2 skill — README generation workflow |
| `etl-orchestrator` | Broader 7-phase ETL agent that may invoke `schema-creation-agent` as part of a larger pipeline |

---

## 12. Key Design Decisions

**D1 — Two-phase blocking architecture**
Phase 1 (schema enrichment) must complete before Phase 2 (README generation) begins. The README's Notes & Conventions section depends on fully enriched `schema.yaml` descriptions. A failed Phase 1 makes a high-quality README impossible.

**D2 — Non-blocking Phase 2**
README generation failure should not invalidate schema enrichment work. The `schema.yaml` output is the higher-value artifact; README can be regenerated independently.

**D3 — Opus model**
Schema enrichment requires reading and synthesising multiple files (query SQL, three tiers of base schemas, existing schema). The higher reasoning capacity of Opus reduces hallucination risk for description quality and column matching.

**D4 — Column-description-finder fetches live files**
Base schema files are fetched live from GitHub (not read inline) to avoid stale local copies and to reduce hallucination risk in column matching. This is mandatory — the audit script uses deterministic matching.

**D5 — Non-base-schema descriptions are captured, not silently applied**
Descriptions derived from query context or application context are written to `_missing_metadata.yaml` with recommended promotion targets. This creates an auditable record and enables gradual expansion of the base schema coverage, reducing the need for inference over time.

---

## 13. File Conventions

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

## 14. Open Questions & Future Work

| # | Question / Item | Notes                                                                                                 |
|---|---|-------------------------------------------------------------------------------------------------------|
| OQ-1 | Batch mode | Should the agent accept a dataset name and process all tables in one run?                             |
| OQ-2 | Minimal README support | Should the agent detect single-consumer tables and switch to minimal style automatically?             |
| OQ-3 | GitHub PR creation | Should the agent open a PR with the generated files after completion?                                 |
| OQ-4 | Base schema promotion workflow | Should `_missing_metadata.yaml` feed an automated PR to `global.yaml` or `app_<name>.yaml`?           |
| OQ-5 | `query.py` column extraction | Can AST (Abstract Syntax Tree) parsing recover SELECT output columns from Python ETL scripts to enable column validation? |
| OQ-6 | Downstream consumer detection | Can the agent read the `bigquery-etl` DAG graph to auto-populate the README Downstream section?       |

---

## 15. General Feedback

| Name       | Emoji | Comments      |
|------------|-------|---------------|
|            |       |               |
|            |       |               |

---

## 16. Revision History

| Version | Date       | Author        | Changes   |
|---------|------------|---------------|-----------|
| 0.1 | 2026-03-24 | Gaurang Katre | Initial draft |
