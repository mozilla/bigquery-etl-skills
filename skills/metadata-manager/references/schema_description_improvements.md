# Schema Description Improvement Workflow

## Overview

When generating schema.yaml files for derived tables, use source table descriptions as a base but improve them when needed. This guide explains when and how to improve descriptions, and how to recommend updates to source tables.

## Philosophy

**Use source descriptions as foundation:**
- Maintains consistency across related tables
- Preserves institutional knowledge
- Reduces duplication of effort

**Proactively offer to add missing descriptions:**
- **When source table has NO descriptions (typically ALL fields are missing)**
- Notify user about the opportunity to improve metadata completeness
- Ask if they want to generate descriptions for the source table
- If yes: Generate descriptions for ALL fields and update source schema.yaml
- Benefits all current and future downstream tables

**Improve when it adds value:**
- Add context specific to derived table
- Clarify transformations or aggregations
- Fill gaps in source descriptions
- Simplify technical jargon for broader audience

**Recommend source updates (but don't edit without asking):**
- When source description exists but is unclear or incomplete
- When improvement is subjective or requires domain knowledge
- When source description has errors or outdated information

## Detecting Missing Descriptions

When discovering source table schemas, check for missing descriptions:

**Missing descriptions indicators:**
- `description: ""` (empty string)
- `description: null`
- `description` field is absent entirely
- Description is just the field name repeated

**Count missing descriptions:**
```bash
# Check how many fields lack descriptions
grep -c 'description: ""' schema.yaml
# Or check for missing description keys
grep -c '^  - name:' schema.yaml  # Total fields
grep -c '^    description:' schema.yaml  # Fields with descriptions
```

**Threshold for offering to add descriptions:**
- **If > 50% of fields are missing descriptions:** Offer to generate descriptions for ALL fields
- **If < 50% missing:** Recommend improvements for specific fields only

## Workflow: Asking User About Missing Descriptions

### Step 1: Detect Missing Descriptions During Discovery

When reading a source table schema:

```yaml
# Example: telemetry_derived.clients_daily_v1 schema.yaml
fields:
- name: submission_date
  type: DATE
  description: ""  # ❌ Missing

- name: client_id
  type: STRING
  description: ""  # ❌ Missing

- name: active_hours_sum
  type: FLOAT
  description: ""  # ❌ Missing
```

Count: 3 fields, 3 missing descriptions (100% missing)

### Step 2: Notify User and Ask

Present a clear notification:

```markdown
## ⚠️ Source Table Missing Descriptions

I discovered that `telemetry_derived.clients_daily_v1` has **no field descriptions** (0 out of 23 fields have descriptions).

**Opportunity for metadata completeness:**
Would you like me to generate descriptions for all 23 fields in this source table?

**Benefits:**
- Improves metadata completeness across the repository
- Benefits all downstream tables (not just this one)
- Helps future developers understand the data
- One-time effort with lasting impact

**Estimated time:** ~2-3 minutes to generate and update

**Options:**
1. ✅ Yes, generate descriptions for the source table
2. ❌ No, just proceed with the derived table
```

### Step 3: Based on User Response

**If user says YES:**
1. Read the full source table schema.yaml
2. For each field, generate a clear, informative description based on:
   - Field name
   - Field type
   - Context from similar fields in other tables
   - Knowledge of common telemetry patterns
3. Update the source table's schema.yaml with Edit tool
4. Verify the update succeeded
5. Use those new descriptions in the derived table

**If user says NO:**
1. Proceed with generating the derived table schema
2. Use basic descriptions based on field names
3. Note in output that source table could be improved later

### Step 4: Multiple Source Tables with Missing Descriptions

If multiple source tables have missing descriptions:

```markdown
## ⚠️ Multiple Source Tables Missing Descriptions

I discovered **2 source tables** with missing descriptions:

1. `telemetry_derived.clients_daily_v1` - 0/23 fields (0%)
2. `search_derived.search_clients_daily_v8` - 2/15 fields (13%)

Would you like me to generate descriptions for these source tables?

**Options:**
1. Generate for all source tables (recommended for maximum impact)
2. Generate for specific table(s) - which one(s)?
3. Skip source updates, just proceed with derived table
```

## When to Use Source Descriptions As-Is

### Good Source Descriptions (Use As-Is)

**Characteristics:**
- Clear and concise
- Explains meaning and purpose
- Includes relevant details (units, format, calculation)
- No ambiguity

**Example:**
```yaml
# Source: clients_daily_v1
- name: active_hours_sum
  description: "Total active hours for the client during the submission date, calculated as sum of active_ticks * 5 seconds / 3600. NULL if no active ticks recorded."
```

**Action:** Use as-is or with minor derived-table context:
```yaml
# Derived table schema
- name: active_hours_sum
  description: "Total active hours for the client during the submission date, calculated as sum of active_ticks * 5 seconds / 3600. Aggregated from clients_daily_v1."
```

## When to Improve Descriptions

### Scenario 1: Vague or Minimal Description

**Source description:**
```yaml
- name: search_count
  description: "Number of searches"
```

**Problems:**
- Doesn't explain scope (what types of searches?)
- Doesn't explain sources (which search engines?)
- Doesn't clarify whether it's unique or total

**Improved description:**
```yaml
- name: search_count
  description: "Total count of search interactions across all search engines (Google, Bing, DuckDuckGo, etc.) and access points (urlbar, searchbar, content). Includes both SAP and follow-on searches."
```

**Recommendation for source:**
```markdown
## Recommended Update for `telemetry_derived.clients_daily_v1`

**Field:** `search_count`

**Current description:** "Number of searches"

**Recommended description:** "Total count of search interactions across all search engines (Google, Bing, DuckDuckGo, etc.) and access points (urlbar, searchbar, content). Includes both SAP and follow-on searches."

**Rationale:** Original description lacks detail about scope and sources, making it unclear for downstream consumers.
```

### Scenario 2: Missing Units or Format

**Source description:**
```yaml
- name: subsession_length
  description: "Length of the subsession"
```

**Problems:**
- No units specified (seconds? minutes? hours?)
- No mention of NULL handling

**Improved description:**
```yaml
- name: subsession_length
  description: "Length of the subsession in seconds. NULL if subsession was not properly closed or duration could not be calculated."
```

**Recommendation for source:**
```markdown
## Recommended Update for `telemetry_derived.main_summary_v4`

**Field:** `subsession_length`

**Current description:** "Length of the subsession"

**Recommended description:** "Length of the subsession in seconds. NULL if subsession was not properly closed or duration could not be calculated."

**Rationale:** Units should be explicit to avoid confusion. NULL handling clarifies data quality expectations.
```

### Scenario 3: Technical Jargon Without Context

**Source description:**
```yaml
- name: scalar_parent_browser_engagement_total_uri_count
  description: "Accumulated URI count from histogram"
```

**Problems:**
- "Accumulated" - from where? Over what period?
- "Histogram" - which histogram?
- Doesn't explain what "URI count" represents

**Improved description:**
```yaml
- name: total_uri_count
  description: "Total number of unique URIs (web pages) visited by the client during the submission date. Accumulated from the scalar_parent_browser_engagement_total_uri_count Glean metric, which tracks page loads across all tabs and windows."
```

**Recommendation for source:**
```markdown
## Recommended Update for `firefox_desktop.metrics_v1`

**Field:** `scalar_parent_browser_engagement_total_uri_count`

**Current description:** "Accumulated URI count from histogram"

**Recommended description:** "Total number of unique URIs (web pages) visited by the client during the submission date. Tracks page loads across all tabs and windows."

**Rationale:** Original description is too technical and doesn't explain what the metric represents for non-technical users.
```

### Scenario 4: Missing Description

**Source:**
```yaml
- name: experiments
  description: ""  # or missing entirely
```

**Improved description:**
```yaml
- name: experiments
  description: "Map of active experiments the client is enrolled in, keyed by experiment slug with values containing branch assignment and enrollment metadata."
```

**Recommendation for source:**
```markdown
## Recommended Update for `telemetry.main`

**Field:** `experiments`

**Current description:** [Missing]

**Recommended description:** "Map of active experiments the client is enrolled in, keyed by experiment slug with values containing branch assignment and enrollment metadata."

**Rationale:** Field has no description. Added description based on field structure and common usage.
```

### Scenario 5: Derived-Specific Context

**Source description (already good):**
```yaml
# Source: events_v1
- name: event.name
  description: "The name of the event as defined in the Glean Event metric."
```

**Derived table adds transformation:**
```sql
-- query.sql extracts only accessibility-related events
WHERE event.category = 'accessibility'
```

**Improved description for derived table:**
```yaml
- name: event_name
  description: "The name of the accessibility event as defined in the Glean Event metric. Filtered to include only events in the 'accessibility' category."
```

**Action:** Use improved description in derived table, but **don't recommend update to source** (source description is correct for the source table's broader scope).

## Description Improvement Checklist

When reviewing a source description, check:

- [ ] **Clarity:** Is the meaning immediately clear to someone unfamiliar with the table?
- [ ] **Completeness:** Does it explain what, why, and how?
- [ ] **Units:** Are units specified (seconds, bytes, count, percentage, etc.)?
- [ ] **Format:** Is the data format clear (ISO date, Unix timestamp, JSON, etc.)?
- [ ] **Scope:** Is the scope clear (per-client, per-day, lifetime, etc.)?
- [ ] **NULL handling:** Is NULL behavior explained?
- [ ] **Calculation:** If calculated, is the formula or method explained?
- [ ] **Sources:** If aggregated, are the sources mentioned?

## Recommendation Format

When recommending source table updates, use this format:

```markdown
## Recommended Source Schema Updates

The following source table descriptions could be improved:

### `<project>.<dataset>.<table>`

**File:** `sql/<project>/<dataset>/<table>/schema.yaml`

**Field:** `<field_name>`

**Current description:** "<current description or [Missing]>"

**Recommended description:** "<improved description>"

**Rationale:** <explanation of why this improvement is valuable>

---

**Field:** `<another_field>`

[... repeat for each field ...]
```

## When NOT to Recommend Source Updates

**Don't recommend updates when:**

1. **Derived-specific context:** Your improvement only applies to the specific derived table's use case
2. **Glean Dictionary sources:** Descriptions come from Glean - update probe definitions instead
3. **External/live tables:** Can't update (not in repository)
4. **Recently updated:** Check git history - don't duplicate recent work
5. **Personal preference:** Improvement is stylistic rather than substantive

## Prioritizing Recommendations

**High priority - Always recommend:**
- Missing descriptions
- Incorrect descriptions
- Missing units or formats
- Ambiguous scope

**Medium priority - Recommend if significant:**
- Vague descriptions that could be more specific
- Technical jargon that could be simplified
- Missing context about NULL handling

**Low priority - Optional:**
- Minor wording improvements
- Stylistic changes
- Adding examples (nice-to-have)

## Tracking Recommendations

When you generate recommendations, output them in a clear section:

```markdown
# Schema Generation Summary

## Generated Schema

Created `schema.yaml` for `<project>.<dataset>.<table>`

- **Fields:** 23
- **Source tables:** telemetry_derived.clients_daily_v1, telemetry.main
- **Descriptions:** 18 from source, 5 improved

## Recommended Source Updates

I've identified 3 source table descriptions that could be improved:

### telemetry_derived.clients_daily_v1

**search_count** - Current description lacks scope and sources
**active_hours_sum** - Missing NULL handling explanation

### telemetry.main

**experiments** - Description is missing entirely

See detailed recommendations below:

[... full recommendations ...]
```

## Example: Full Workflow

### Step 1: Discover Source Schema

Query uses: `telemetry_derived.clients_daily_v1`

```bash
# Find and read source schema
cat sql/moz-fx-data-shared-prod/telemetry_derived/clients_daily_v1/schema.yaml
```

### Step 2: Extract Field Descriptions

```yaml
# Source schema excerpt
- name: active_hours_sum
  type: FLOAT
  description: "Sum of active hours"  # ⚠️ Vague

- name: search_count
  type: INTEGER
  description: "Number of searches"  # ⚠️ Lacks detail

- name: scalar_parent_browser_engagement_unique_domains_count
  type: INTEGER
  description: "Count of unique domains visited"  # ✅ Good
```

### Step 3: Generate Derived Schema with Improvements

```yaml
# Derived table schema.yaml
fields:
- name: active_hours_sum
  type: FLOAT
  mode: NULLABLE
  description: "Total active hours for the client during the submission date, calculated as sum of active_ticks * 5 seconds / 3600. NULL if no active ticks recorded."

- name: search_count
  type: INTEGER
  mode: NULLABLE
  description: "Total count of search interactions across all search engines (Google, Bing, DuckDuckGo, etc.) and access points (urlbar, searchbar, content). Includes both SAP and follow-on searches."

- name: unique_domains_count
  type: INTEGER
  mode: NULLABLE
  description: "Count of unique domains visited by the client. Based on scalar_parent_browser_engagement_unique_domains_count from clients_daily_v1."
```

### Step 4: Generate Recommendations

```markdown
## Recommended Source Schema Updates

### `moz-fx-data-shared-prod.telemetry_derived.clients_daily_v1`

**File:** `sql/moz-fx-data-shared-prod/telemetry_derived/clients_daily_v1/schema.yaml`

**Field:** `active_hours_sum`

**Current description:** "Sum of active hours"

**Recommended description:** "Total active hours for the client during the submission date, calculated as sum of active_ticks * 5 seconds / 3600. NULL if no active ticks recorded."

**Rationale:** Original description lacks calculation method and NULL handling, making it unclear how this metric is derived.

---

**Field:** `search_count`

**Current description:** "Number of searches"

**Recommended description:** "Total count of search interactions across all search engines (Google, Bing, DuckDuckGo, etc.) and access points (urlbar, searchbar, content). Includes both SAP and follow-on searches."

**Rationale:** Original description lacks scope and sources. Downstream tables would benefit from understanding what types of searches are included.
```

## Best Practices

### DO:
- ✅ Use source descriptions as base
- ✅ Add value with improvements
- ✅ Recommend updates that benefit all downstream tables
- ✅ Be specific about what's missing/wrong
- ✅ Provide clear rationale for recommendations

### DON'T:
- ❌ Rewrite descriptions from scratch without checking source
- ❌ Recommend stylistic changes without substance
- ❌ Duplicate good descriptions unnecessarily
- ❌ Recommend updates to external sources (Glean, live tables)
- ❌ Over-explain simple fields (e.g., "client_id" is self-explanatory)

## Summary

**Schema description workflow:**
1. Discover source table schemas (use priority order from `schema_discovery_guide.md`)
2. Extract source field descriptions
3. Evaluate each description using improvement checklist
4. Generate derived schema with improvements
5. Create recommendations for source tables when valuable
6. Present recommendations to user

**Goal:** Create high-quality, consistent schema documentation across all tables while identifying opportunities to improve upstream sources.
