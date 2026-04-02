# README Layout Conventions for BigQuery ETL Tables

Derived from comparing 10+ README.md files across `sql/moz-fx-data-shared-prod/`.

## Repository README Styles

Two styles coexist in the repo:

| Style | Line count | Used for |
|---|---|---|
| Minimal | 4–15 lines | UDFs, static tables, simple derived tables |
| Rich | 100–170 lines | Shared datasets, newtab/ads/telemetry tables with multiple consumers |

Use the **rich style** for any table that is a shared dataset, has multiple downstream consumers, or requires analyst documentation.

## Section Order (Rich Style)

1. **H1 title** — short, human-readable table name
2. **Intro paragraph** — 1–2 sentences, no heading. State grain and what it covers.
3. `---`
4. **📌 Overview** — compact metadata table + use cases one-liner
5. `---`
6. **🗺️ Data Flow** — Mermaid flowchart
7. `---`
8. **🧠 How It Works** — numbered steps
9. `---`
10. **🧾 Key Fields** — dimension + metric sub-tables
11. `---`
12. **🧩 Example Queries** — 3 graduated SQL examples
13. `---`
14. **🔧 Implementation Notes** — 3–5 bullets
15. `---`
16. **📌 Notes & Conventions** — key field and metric semantic definitions
17. `---`
18. **🗃️ Schema & Related Tables** — schema.yaml link, upstream, downstream

**Target length:** 150–170 lines. Never exceed 170.

## Section-by-Section Rules

### Intro paragraph
- No heading, directly after H1
- State: what the table contains, at what grain, and from what source
- One sentence on what it covers (topsites/Pocket/search/etc.)

### 📌 Overview table
Merge all metadata into one compact table — do NOT use separate sections for scheduling, storage, owners, or versioning:

```markdown
| | |
|---|---|
| **Grain** | One row per `(submission_date, dimension combination)` |
| **Source** | `project.dataset.table_name` |
| **DAG** | `bqetl_<name>` · daily · incremental |
| **Partitioning** | `submission_date` *(partition filter required)* |
| **Clustering** | `field1`, `field2` |
| **Retention** | No automatic expiration / N days |
| **Owner** | owner@mozilla.com |
| **Version** | v1 (initial version) |
```

Follow with a **Use cases** one-liner using `·` as separator:
```markdown
**Use cases:** use case 1 · use case 2 · use case 3
```

### 🗺️ Data Flow
Always use a Mermaid `flowchart TD` with 3 nodes:
1. Source table(s) with fully qualified name
2. "This query" with the filter/group-by description
3. Output — "Partitioned table" with time + cluster annotation

```mermaid
flowchart TD
  A[Source description<br/>`project.dataset.table`] -->|{filter @param / date range}<br/>GROUP BY keys| B[**This query**]
  B --> C[Partitioned table<br/>time: `partition_field`<br/>cluster: `field1`, `field2`]
```

For multiple sources, add nodes A1, A2, ... all pointing to B.

### 🧠 How It Works
Always 4–5 numbered steps. Step 5 is always data inclusion/exclusions:

1. **Input** — describe source grain and what each row represents
2. **Aggregation** — SUM() for counts, COUNT(DISTINCT) for uniques, GROUP BY keys
3. **[Table-specific breakdown]** — e.g., sponsored/organic split, attribution types
4. **[Table-specific breakdown]** — e.g., search attribution, experiment metadata
5. **Data inclusion** — state explicitly whether bots, synthetic clients, or specific populations are excluded

### 🧾 Key Fields
Two sub-tables, always in this order:

**Dimensions** — Category + Fields columns. Group fields by logical category (omit rows not applicable to this table):
- Date & Geo
- Browser
- Search *(conditional — omit if no search dimensions)*
- [Product] config (e.g., Newtab config, Pocket config) *(conditional — omit if no product config fields)*
- User

**Metrics** — Category + Fields columns. Use `{field_a\|field_b\|field_c}` shorthand for related fields:
```
| Topsites | `topsite_{clicks\|impressions\|dismissals}` · `sponsored_*` · `organic_*` |
```

### 🧩 Example Queries
Always 3 examples, graduated in complexity:
1. **Basic** — simple aggregation with date filter and GROUP BY 1–2 dimensions
2. **Segmentation** — GROUP BY a user dimension (activity_segment, channel, country)
3. **Attribution/Advanced** — multi-metric with SAFE_DIVIDE, WHERE clause filtering, or JOIN

Rules:
- Use `SAFE_DIVIDE()` for any ratio/CTR calculation (never raw division)
- Include a comment line before each query: `-- N. Description`
- Use `GROUP BY 1, 2` shorthand for brevity
- Use fully qualified table name: `` `project.dataset.table` ``

### 🔧 Implementation Notes
3–5 bullets covering:
- Incremental/full-refresh pattern + `@parameter` name
- Deduplication (whether needed or why not)
- Feature flag handling (pass-through vs. coalescing)
- `SAFE_DIVIDE` reminder for downstream users
- Any NULL coalescing or special aggregation

### 📌 Notes & Conventions
Short bullet definitions for key field and metric semantics — what each field means operationally:
- `field_name` = formula used (e.g., `COUNT(DISTINCT client_id)`)
- NULL semantics for config fields
- What `sponsored_*` / `organic_*` means
- Attribution tag meanings if applicable

### 🗃️ Schema & Related Tables
Merge three things into one compact section:
```markdown
- Full field definitions: [`schema.yaml`](schema.yaml)
- **Upstream**: `project.dataset.source_table` — brief description
- **Downstream**: `mozdata` project for user-facing public views / list known consumers
```

## Conciseness Rules

| Anti-pattern | Fix |
|---|---|
| Separate sections for Scheduling, Storage, Owners, Retention, Version | Merge into Overview table |
| Separate "Schema Reference" + "Related Tables" sections | Merge into one "🗃️ Schema & Related Tables" |
| 3-line SQL queries with expanded GROUP BY list | Use `GROUP BY 1, 2` shorthand |
| Verbose "How It Works" paragraphs | Use numbered single-line steps |
| Repeated full table paths | Use full path once per example, abbreviate elsewhere |

## Information Sources

| README section | Read from |
|---|---|
| Grain, source table(s) | `query.sql` — FROM clause, GROUP BY |
| DAG, partitioning, clustering, retention, owner | `metadata.yaml` |
| Field names and types | `schema.yaml` |
| Field descriptions (for Notes & Conventions) | `schema.yaml` descriptions |
| Version | Directory name (e.g., `_v1`) |
