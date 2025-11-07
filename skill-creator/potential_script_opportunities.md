# Script Opportunities for BigQuery ETL Skills

This document provides guidance on when to add scripts to skills and identifies high-priority script opportunities.

## When to Use Scripts

Add scripts when:
- ✅ Operation is deterministic and needs to be exactly right
- ✅ External API calls with specific handling required
- ✅ Token-expensive operations (large file processing)
- ✅ Operations Claude tends to rewrite with subtle variations
- ✅ Wrapping CLI tools with validation/error handling

Avoid scripts when:
- ❌ Simple operations Claude handles reliably
- ❌ Tasks requiring flexible reasoning and context adaptation
- ❌ One-off operations unlikely to be repeated

## High-Priority Script Opportunities

### 1. sql-test-generator: `scripts/detect_source_tables.py`

**Purpose:** Extract ALL source table references from query.sql

**Why needed:**
- Claude may miss tables in complex queries (subqueries, CTEs, UNION)
- Inconsistent extraction across different query patterns
- Missing fixtures cause production queries in tests

**Implementation approach:**
- Parse SQL with sqlparse library for accurate AST analysis
- Handle Jinja template variables and conditionals
- Extract ALL table references (FROM, JOIN, UNION, subqueries)
- Output checklist format for fixture creation

**Expected impact:** Prevents production query accidents from missed fixtures

---

### 2. sql-test-generator: `scripts/fetch_table_schema.py`

**Purpose:** Fetch minimal table schema from DataHub using token-efficient patterns

**Why needed:**
- DataHub `get_entity` returns 50K+ tokens and frequently fails
- Manual filtering of response to extract only column names/types
- Repeated pattern across multiple uses

**Implementation approach:**
- Use `get_lineage(max_hops=0)` instead of `get_entity`
- Filter response to ONLY column names and types
- Return clean, structured JSON

**Expected impact:** Prevents token limit exceeded errors, faster schema lookups

---

### 3. metadata-manager: `scripts/validate_schema_sync.py`

**Purpose:** Validate schema.yaml matches query.sql output structure

**Why needed:**
- Schema drift between query output and schema.yaml
- No automated check that descriptions exist for all fields

**Implementation approach:**
- Dry-run query with `./bqetl query schema update --dry-run`
- Compare extracted schema vs existing schema.yaml
- Check all fields have descriptions

**Expected impact:** Catches schema drift before deployment

---

## Implementation Checklist

For each script to add:

- [ ] Create script file with proper shebang and docstring
- [ ] Make executable: `chmod +x scripts/script_name.py`
- [ ] Add dependencies to requirements.txt (if needed)
- [ ] Update SKILL.md to reference script in workflow
- [ ] Test script with real examples
- [ ] Add error handling and helpful error messages
- [ ] Document script usage with examples

## Future Opportunities

Additional scripts to consider when needs arise:

- `query-writer/scripts/render_and_validate.py` - Combined render + validate + format check
- `bigconfig-generator/scripts/validate_bigconfig.py` - Enhanced validation with clearer errors
- `bigquery-etl-core/scripts/discover_metrics.py` - Query ProbeInfo API for metrics
- `metadata-manager/scripts/suggest_dag.py` - Recommend DAG based on dataset patterns

## Related Documentation

- Main skill-creator SKILL.md - "When to Use Scripts" section
- `../bigquery-etl-core/references/datahub_best_practices.md` - Token-efficient DataHub patterns
- Individual skill SKILL.md files for integration points
