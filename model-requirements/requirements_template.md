# <Model Name> Requirements

## 1. Overview

<Brief, one-paragraph description of the business activity this model represents and the key value it provides.>

## 2. Useful Links / Prior Work

<Link to upstream documentation or exploration notebooks>
<Link to related dashboards or queries>

## 3. Dependencies

**Upstream:** <tables or services this model pulls from>

**Downstream:** <tables, dashboards, or ML jobs that will consume this model>

**Blocked by:** <"None" or a short list of open prerequisites>

## 4. Grain

<Explicitly state what a single row represents (for example "one row per client per submission date")>

## 5. Source Data

| Table | Join Key(s) | Filter Logic | Notes |
|-------|-------------|--------------|-------|
| `<project.dataset.table>` | `<key columns>` | `<where clauses, if any>` | <why this table is needed> |

## 6. Field Summary

| Field | Description | Type | Business Logic / Transform Notes |
|-------|-------------|------|----------------------------------|
| `<column name>` | <human-friendly meaning> | `<STRING / BOOLEAN / INT64 / DATE …>` | <any derived logic, enums, or default handling> |

## 7. Questions This Model Should Answer

1. <Example: How many installs do we get per day?>
2. <Example: Which campaigns drive the most installs?>
3. <Keep to 3-5 core questions>

## 8. Lineage Diagram

<Link to DataHub lineage or note "See DataHub: <URN>">

## 9. Data Governance

**Classification:** Bronze / Silver / Gold

**Retention Policy:** <number of days or "client-level, Shredder-configured">

**PII / Sensitive Flags:** <yes / no, with brief detail if yes>

## 10. Validation & QA

- Row counts backfill check versus source tables
- Key field null-rate thresholds
- Daily freshness expectation <e.g., lag ≤ 24 hr>

## 11. Owner & Status

| Field | Value |
|-------|-------|
| Primary Owner | @<slack-handle> |
| Reviewers | <team or individuals> |
| Version | v0 (draft) / v1 (approved) |
| Target Release Date | <YYYY-MM-DD> |

---

## Working Notes (For SQL Development)

**Grain:** <one row per ...>

**Source Tables:**
- `<table1>` - <why needed>
- `<table2>` - <why needed>

**Key Transformations:**
- <transformation 1>
- <transformation 2>

**Derived Fields:**
- `field_name` - <business logic>

**Partitioning:** <daily/hourly on field>

**Scheduling:** <DAG name or "new DAG needed">

**Blockers:** <any blockers or "None">
