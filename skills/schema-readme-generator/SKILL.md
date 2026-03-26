---
name: schema-readme-generator
description: Use this skill to create or update README.md files for BigQuery ETL tables in the mozilla bigquery-etl repository. Follows layout conventions derived from comparing README files across the repo — rich style with emoji headings, Mermaid data flow diagram, graduated example queries, and concise metadata overview table. Requires schema.yaml with complete descriptions (run schema-enricher first if needed) and metadata.yaml (run metadata-manager first if incomplete).
---

# README Generator

**Prerequisites:** Run `schema-enricher` first if schema.yaml is missing descriptions; run `metadata-manager` first if metadata.yaml is incomplete.
**When to use:** Creating or updating README.md for any shared dataset, derived table, or table with multiple downstream consumers

## 🚨 REQUIRED READING - Start Here

**BEFORE generating any README, review the following:**

1. **Layout conventions:** READ `references/layout_conventions.md`
   - Section order, conciseness rules, anti-patterns to avoid
   - Information sources (which file to read for which section)

2. **README template:** READ `assets/readme_template.md` and COPY its structure
   - Fill every `{placeholder}` from the source files
   - Do not skip or reorder sections

## Workflow

### Step 1: Read source files

Read all three files before writing anything:

```
sql/<project>/<dataset>/<table>/query.sql     → source tables, GROUP BY dimensions, metrics, @param
sql/<project>/<dataset>/<table>/metadata.yaml → DAG, partitioning, clustering, retention, owners
sql/<project>/<dataset>/<table>/schema.yaml   → field names, types, descriptions for Key Fields section
```

If only `query.py` exists (no `query.sql`): note it — the Data Flow and How It Works sections may be incomplete or require manual input. Fill what is possible from metadata.yaml and schema.yaml.

Extract and record:
- **FROM clause** — source table(s) with fully qualified name
- **GROUP BY fields** — these become Dimensions
- **Aggregated fields** — SUM/COUNT/DISTINCT targets become Metrics
- **WHERE clause** — `@param_name` for Implementation Notes
- **DAG name, partition field, cluster fields, owners** — for Overview table
- **Table version** — from directory name (e.g., `_v1`)

### Step 2: Check if README.md already exists

```bash
ls sql/<project>/<dataset>/<table>/README.md
```

- **Exists** → read it, identify sections to update or add (do not remove existing content without noting it)
- **Does not exist** → generate from template

### Step 3: Write README.md

READ `assets/readme_template.md` and fill every placeholder:

**📌 Overview table** — use metadata.yaml for DAG/partition/cluster/retention/owner; derive Version from directory name.

**🗺️ Data Flow** — Mermaid `flowchart TD` with exactly 3 nodes:
- Node A: source table(s) with short label + fully qualified name
- Node B: `**This query**` with filter and GROUP BY description
- Node C: `Partitioned table` with time and cluster annotation
- For multiple sources: A1, A2 → B

**🧠 How It Works** — 4–5 numbered steps. Step 5 MUST explicitly state data inclusion/exclusion policy:
- "All records from source are included; no exclusions applied at this layer."
- OR list specific exclusions (bots, synthetic clients, test populations)

**🧾 Key Fields** — two sub-tables (Dimensions, Metrics). Use `{a\|b\|c}` shorthand for related field families. Group dimensions by: Date & Geo, Browser, Search, [Product] config, User. Omit dimension rows not applicable to this table.

**🧩 Example Queries** — exactly 3, graduated:
1. Basic aggregation — date filter + 1–2 GROUP BY dimensions
2. Segmentation — GROUP BY a user/product dimension with SAFE_DIVIDE ratio
3. Attribution/Advanced — multi-metric, WHERE filter on a dimension, SAFE_DIVIDE

Rules:
- Always use `SAFE_DIVIDE()` for ratios — never raw division
- Use `GROUP BY 1, 2` shorthand
- Comment each: `-- N. Description`
- Fully qualified table name in FROM

**🔧 Implementation Notes** — 3–5 bullets extracted from query.sql logic.

**📌 Notes & Conventions** — bullet definitions for key fields from schema.yaml descriptions.

**🗃️ Schema & Related Tables** — one section; combine schema.yaml link + upstream + downstream.

### Step 4: Conciseness check

Before finalizing, verify:
- [ ] Total line count ≤ 170
- [ ] No separate sections for Scheduling, Storage, Owners, Retention (all in Overview table)
- [ ] No separate "Schema Reference" + "Related Tables" (merged into 🗃️)
- [ ] SQL examples use `GROUP BY 1, 2` shorthand
- [ ] How It Works uses single-line numbered steps (no multi-paragraph blocks)
- [ ] How It Works Step 5 explicitly states data inclusion/exclusion policy

If over 170 lines, trim by: shortening SQL examples, collapsing Notes & Conventions bullets, abbreviating How It Works steps.

### Step 5: Write and report

Write the README.md to:
```
sql/<project>/<dataset>/<table>/README.md
```

Then read back the written file and confirm:
- [ ] All sections from the template are present and in order
- [ ] No `{placeholder}` tokens remain unfilled (exception: if only `query.py` exists, Data Flow and How It Works may be partially filled — note which sections and why)
- [ ] Line count is within target (≤ 170)
- [ ] Mermaid block renders valid `flowchart TD` syntax

Report:
- Path written
- Line count
- Sections included
- Any placeholders left unfilled (with reason)

## Integration with Other Skills

| Skill | When to invoke |
|---|---|
| `schema-enricher` | Run first if schema.yaml is missing descriptions — needed for Notes & Conventions |
| `metadata-manager` | Run first if metadata.yaml is incomplete — needed for Overview table |

## Decision Tree: Rich vs. Minimal Style

```
Table has multiple downstream consumers OR is a shared dataset?
  → Rich style (this skill)

Table is a UDF, static reference, or simple single-consumer table?
  → Minimal style: title + ## Description with 5–10 bullet points
  → Do not use this skill for minimal style
```

## Example Invocations

```
Create a README.md for telemetry_derived.newtab_daily_interactions_aggregates_v1
Update the README.md for firefox_desktop_derived.newtab_clients_daily_v2 — add missing example queries
Generate README for ads_derived.impressions_v1
```
