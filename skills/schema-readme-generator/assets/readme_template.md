# {Table Friendly Name}

{1–2 sentence intro: what the table contains, at what grain, from what source, and what it covers.}

---

## 📌 Overview

| | |
|---|---|
| **Grain** | One row per `({partition_field}, {dimension combination})` |
| **Source** | `{project}.{source_dataset}.{source_table}` |
| **DAG** | `{dag_name}` · {schedule} · {incremental/full-refresh} |
| **Partitioning** | `{partition_field}` *(partition filter required)* |
| **Clustering** | `{cluster_field_1}`, `{cluster_field_2}` |
| **Retention** | {No automatic expiration / N days} |
| **Owner** | {owner@mozilla.com} |
| **Version** | {v1 (initial version) / vN — changes from vN-1} |

**Use cases:** {use case 1} · {use case 2} · {use case 3}

---

## 🗺️ Data Flow

```mermaid
flowchart TD
  A[{Source description}<br/>`{project}.{source_dataset}.{source_table}`] -->|{filter @param / date range}<br/>GROUP BY {key dimensions}| B[**This query**]
  B --> C[Partitioned table<br/>time: `{partition_field}`<br/>cluster: `{cluster_field_1}`, `{cluster_field_2}`]
```

---

## 🧠 How It Works

1. **Input** — `{source_table}` has one row per {source grain description}.
2. **Aggregation** — {dimension fields} pass through as GROUP BY keys. Counts use `SUM()`; unique entities use `COUNT(DISTINCT)`.
3. **{Special breakdown 1}** — {description, e.g., sponsored/organic split}.
4. **{Special breakdown 2}** — {description, e.g., search attribution types}.
5. **Data inclusion** — {explicit statement: "All records from source are included; no bot/synthetic exclusions applied" OR list specific exclusions}.

---

## 🧾 Key Fields

### Dimensions

| Category | Fields |
|---|---|
| Date & Geo | `{partition_field}`, `country_code` |
| Browser | `channel`, `browser_version`, `os` |
| Search | `{search_field_1}`, `{search_field_2}` |
| {Product} config | `{config_field_1}`, `{config_field_2}` |
| User | `{user_field_1}`, `{user_field_2}` |

### Metrics

| Category | Fields |
|---|---|
| {Metric category 1} | `{field_a}`, `{field_b}`, `{field_c}` |
| {Metric category 2} | `{field_{a\|b\|c}}` · `sponsored_*` · `organic_*` |

---

## 🧩 Example Queries

```sql
-- 1. {Basic aggregation description}
SELECT
  {partition_field},
  SUM({metric_field}) AS {metric_alias}
FROM `{project}.{dataset}.{table}`
WHERE {partition_field} >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY 1
ORDER BY 1 DESC;
```

```sql
-- 2. {Segmentation description}
SELECT
  {partition_field},
  {segment_dimension},
  SUM({metric_field}) AS {metric_alias},
  SAFE_DIVIDE(SUM({numerator}), SUM({denominator})) AS {rate_alias}
FROM `{project}.{dataset}.{table}`
WHERE {partition_field} = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
GROUP BY 1, 2
ORDER BY {metric_alias} DESC;
```

```sql
-- 3. {Attribution/Advanced description}
SELECT
  {partition_field},
  {dimension},
  SUM({metric_a}) AS {alias_a},
  SUM({metric_b}) AS {alias_b},
  SAFE_DIVIDE(SUM({numerator}), SUM({denominator})) AS {rate_alias}
FROM `{project}.{dataset}.{table}`
WHERE {partition_field} >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND {filter_dimension} = '{filter_value}'
GROUP BY 1, 2
ORDER BY 1 DESC, {alias_a} DESC;
```

---

## 🔧 Implementation Notes

- {Incremental: filtered by `@{param_name}` parameter; one partition written per run. / Full-refresh: entire table rewritten on each run.}
- {Deduplication note: "No deduplication needed — source is already event-level" OR "Deduplication applied via ..."}
- {Feature flag note: "Feature flag dimensions are passed through as-is; no coalescing applied."}
- `SAFE_DIVIDE` recommended for ratio calculations to avoid division-by-zero.
- {Any other implementation detail specific to this table.}

---

## 📌 Notes & Conventions

- `{count_field}` = `COUNT(DISTINCT {id_field})` — {what qualifies, e.g., "unique clients with ≥1 interaction"}.
- `{visit_field}` = `COUNT(DISTINCT {visit_id})` — {what qualifies}.
- {`sponsored_*` / `organic_*` = paid vs. non-paid surface breakdown — if applicable.}
- {`tagged_*` = attribution meaning — if applicable.}
- NULL in {config fields} = {what NULL means for this table}.

---

## 🗃️ Schema & Related Tables

- Full field definitions: [`schema.yaml`](schema.yaml)
- **Upstream**: `{project}.{source_dataset}.{source_table}` — {brief description}
- **Downstream**: {`mozdata` project for user-facing public views / list known consumers}
