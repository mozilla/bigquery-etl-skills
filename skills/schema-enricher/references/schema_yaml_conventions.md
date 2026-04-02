# Schema YAML Conventions for BigQuery ETL

## File Structure

```yaml
fields:
- name: column_name
  type: STRING        # BigQuery type
  mode: NULLABLE      # NULLABLE | REQUIRED | REPEATED
  description: >-
    Clear, human-readable description of what this field contains.
    Include units, format, or constraints where relevant.
```

## Field Types

| BigQuery Type | Use For |
|---------------|---------|
| STRING | Text values, identifiers, categories |
| INTEGER | Counts, IDs, positions |
| FLOAT | Ratios, rates, decimals |
| BOOLEAN | Flags, enabled/disabled |
| DATE | Date-only values (YYYY-MM-DD) |
| TIMESTAMP | Date+time values |
| NUMERIC | High-precision decimals (revenue, rates) |
| RECORD | Nested struct / object |

## Field Modes

- **NULLABLE** — field may be NULL (default for most fields)
- **REQUIRED** — field is always populated (partition columns, primary keys)
- **REPEATED** — array field (use with RECORD for array of structs)

## Description Quality Standards

Good descriptions:
- Are one sentence minimum
- Explain WHAT the field represents, not just restating the name
- Include units where applicable (e.g., "in milliseconds", "per session")
- Mention if the value is a count, rate, boolean flag, or dimension
- Use present tense

**Bad:** `pocket_clicks: Pocket clicks`
**Good:** `pocket_clicks: Total number of times a Pocket story was clicked on the New Tab page.`

**Bad:** `is_new_profile: Boolean`
**Good:** `is_new_profile: Whether the Firefox profile was created within the last 28 days.`

## Canonical Field Names and Aliases

Mozilla base schemas define canonical column names. If a query uses an alias (e.g., `sub_date`), the schema should use the canonical name (`submission_date`) with the corresponding description.

Common canonical names:
- `submission_date` — not `sub_date`, `date`, `ds`
- `client_id` — not `cid`, `user_id`
- `country` — full country name; not `geo` or `normalized_country` (these are aliases for this field)
- `country_code` — ISO country code; not `normalized_country_code` (alias for this field)
- `normalized_channel` — not `channel_name`

## Nested Fields (RECORD type)

```yaml
- name: metadata
  type: RECORD
  mode: NULLABLE
  description: Metadata associated with the event.
  fields:
  - name: source
    type: STRING
    mode: NULLABLE
    description: The source system that generated this record.
```

## Array Fields (REPEATED mode)

```yaml
- name: event_types
  type: STRING
  mode: REPEATED
  description: List of event types recorded in this session.
```

## Priority Order for Description Sources

The 3-tier base schema priority order (app-specific → dataset-specific → global) is defined in `column-description-finder/references/column_definition_yaml_guide.md`. Schema-enricher adds three further tiers:

4. **Upstream source schema.yaml** — for pass-through dimension columns, copy description from the source table's `schema.yaml` (locate via FROM clause in `query.sql`)
5. **Query context** — derive from what the column computes in `query.sql` (aggregation, flag, rate)
6. **Application context** — infer from column name semantics and product domain (last resort — document in result file)
