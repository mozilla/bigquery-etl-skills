---
type: reference
purpose: >
  Decision tree for classifying missing column descriptions into the correct
  base schema promotion target (global.yaml, app_<product>.yaml, or
  <dataset_name>.yaml) for use in _missing_metadata.yaml recommended_target
  fields.
when_to_use: >
  Read by the base-schema-audit skill (Step 4) when classifying each missing
  column. Also consulted by schema-enricher Step 6 when populating
  recommended_target for individual tables.
---

# Base Schema Classification Guide

This guide defines the decision tree for assigning a `recommended_target` to
columns whose descriptions are missing and not found in any existing base schema.

---

## Setup

> **When invoked via `base-schema-audit` Step 4:** base schemas are already
> loaded from Step 1 — use the field names and aliases captured there.
>
> **When consulted standalone (e.g. `schema-enricher` Step 6):** load base
> schemas first:
> ```
> ls bigquery_etl/schema/*.yaml
> ```
> Read each file and note every field name and its aliases.
> Naming conventions:
> - `global.yaml` — cross-product, cross-dataset fields
> - `app_<product>.yaml` — fields specific to one product (e.g. `app_newtab.yaml`)
> - `<dataset_name>.yaml` — fields specific to one dataset (e.g. `telemetry_derived.yaml`)

---

## Decision Tree

Apply these steps in strict order — stop at the first match:

### Step 1 — Product namespace check ← always do this first

Examine whether the column belongs to a specific Firefox product or surface:
- Look for a product-specific prefix shared with other columns in the table
  (e.g. `newtab_`, `pocket_`, `suggest_`, `fxa_`, `relay_`, `monitor_`)
- Look for named UI components or product features in the column name
  (e.g. `topsite`, `wallpaper`, `weather_widget`, `list_card`, `topic_selection`)
- Check whether a corresponding `app_<product>.yaml` exists in `bigquery_etl/schema/`

**→ If product-specific: `recommended_target = app_<product>.yaml`. STOP.**

### Step 2 — Cross-dataset breadth check

Search `schema.yaml` files across ALL datasets under `sql/moz-fx-data-shared-prod/`
for this exact column name.

**→ If it appears in 2+ distinct datasets AND is generic (not product-specific):
`recommended_target = global.yaml`**

### Step 3 — Single-dataset check

**→ If it appears in only one dataset AND is generic (not product-specific):
`recommended_target = <dataset_name>.yaml`**

Use the actual dataset name (e.g. `telemetry_derived.yaml`,
`firefox_desktop_derived.yaml`, `search_derived.yaml`).

### Step 4 — Ambiguous

Flag for human review and explain why (e.g. product boundary unclear, column
straddles two products, name too generic to place confidently).

---

## Key Rule

> A column that is exclusive to one dataset is **not** automatically a
> `<dataset_name>.yaml` candidate. It must also be generic (non-product-specific)
> to qualify. Always complete Step 1 before checking dataset scope.
