# Schema.yaml Reference Guide

## Purpose

Schema files define the BigQuery table structure with field names, types, modes, and descriptions.

## Field Structure

```yaml
fields:
  - name: field_name
    type: STRING
    mode: NULLABLE
    description: Required field description explaining purpose, units, or constraints
```

## Common Types

- `STRING` - Text data
- `INTEGER` or `INT64` - Whole numbers
- `FLOAT` or `FLOAT64` - Decimal numbers
- `BOOLEAN` - True/false values
- `DATE` - Date without time (YYYY-MM-DD)
- `TIMESTAMP` - Date and time with timezone
- `RECORD` - Nested structure (requires `fields:` sub-list)
- `NUMERIC` - High-precision decimal
- `BYTES` - Binary data

## Mode Options

- `NULLABLE` - Field can be null (most common)
- `REQUIRED` - Field must have a value
- `REPEATED` - Array of values (for arrays/lists)

## Field Ordering

**Best practices:**
- List fields in the order they appear in the query SELECT statement
- For consistency, order as: `name`, `type`, `mode`, then `description` and nested `fields`
- Keep common metadata fields first (submission_date, client_id, sample_id)

## Schema Example

```yaml
fields:
  - name: submission_date
    type: DATE
    mode: NULLABLE
    description: Date when the data was submitted
  - name: client_id
    type: STRING
    mode: NULLABLE
    description: Unique identifier for the client
  - name: n_total_events
    type: INTEGER
    mode: NULLABLE
    description: Total count of events for this client on this date
```

## Nested/Repeated Fields

**Simple repeated field:**
```yaml
- name: tags
  type: STRING
  mode: REPEATED
  description: List of tags associated with the event
```

**Record (struct) with nested fields:**
```yaml
- name: experiments
  type: RECORD
  mode: REPEATED
  description: List of active experiments for this client
  fields:
    - name: key
      type: STRING
      mode: NULLABLE
      description: Experiment identifier
    - name: value
      type: RECORD
      mode: NULLABLE
      description: Experiment enrollment details
      fields:
        - name: branch
          type: STRING
          mode: NULLABLE
          description: Experiment branch name
        - name: enrollment_id
          type: STRING
          mode: NULLABLE
          description: Unique enrollment identifier
```

## Common Telemetry Fields

Standard fields for telemetry tables: `submission_date`, `client_id`, `sample_id`, `normalized_channel`, `country`, `app_version`.

See existing tables for examples of field types and descriptions.

## Description Requirements

**Important:**
- Descriptions are **required** for all fields in new schemas
- Use `description:` field to document purpose, units, or constraints
- Legacy tables may have `require_column_descriptions: false` in metadata.yaml
- For new tables, always include descriptions even if they seem obvious

**Good descriptions:**
- "Total count of events for this client on this date"
- "ISO 8601 timestamp of when the event occurred"
- "Revenue in USD cents (divide by 100 for dollars)"
- "User's country code from geo-IP lookup (ISO 3166-1 alpha-2)"

**Poor descriptions:**
- "The count" (too vague)
- "client_id" (just repeating the field name)
- "Data" (meaningless)

## Generating Schemas

**From query output:**
```bash
./bqetl query schema update <dataset>.<table>
```

This command:
- Dry-runs the query
- Extracts the output schema
- Updates schema.yaml automatically

## Best Practices

1. **Descriptions:**
   - Always include for new schemas
   - Be specific about units, formats, constraints
   - Mention data sources or derivations
   - Note any privacy considerations

2. **Types:**
   - Use appropriate precision (INT64 vs FLOAT64)
   - Prefer DATE over STRING for dates
   - Use TIMESTAMP for date+time
   - Consider NUMERIC for exact decimal arithmetic

3. **Modes:**
   - Default to NULLABLE unless truly required
   - Use REPEATED for arrays/lists
   - REQUIRED fields should be truly non-null

4. **Organization:**
   - Group related fields together
   - Put key fields (dates, IDs) first
   - Document nested structures clearly

## Reference Examples

**Simple schema:**
- `sql/moz-fx-data-shared-prod/mozilla_vpn_derived/users_v1/schema.yaml`

**Complex schema with nested fields:**
- `sql/moz-fx-data-shared-prod/telemetry_derived/event_events_v1/schema.yaml`
