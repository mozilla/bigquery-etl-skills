# Test Update Workflow

## When Updating Existing Queries

When modifying an existing query.sql file, follow these steps to maintain consistency with existing tests.

## Skill Integration

The query-writer skill handles updating query.sql files and coordinates downstream updates. When queries are modified:
- **query-writer** updates the query.sql file
- **metadata-manager** is invoked to update schema.yaml if output structure changed
- **sql-test-generator** is invoked for complex test fixture creation (new source tables, JOINs)
- Simple test updates like editing expect.yaml can be done directly without invoking another skill

## Step-by-Step Process

### 1. Check for Existing Tests

```bash
ls tests/sql/<project>/<dataset>/<table>/
```

### 2. Update the query.sql File

Make your changes to the query.

### 3. Update schema.yaml if Output Structure Changed

```bash
./bqetl query schema update <dataset>.<table>
```

- Review the changes to ensure they match your expectations
- Add descriptions for any new fields
- If the command fails, fix query syntax errors first

### 4. If Tests Exist, Update Them

**IMPORTANT:** For complex test updates (new source tables, major logic changes), use the `sql-test-generator` skill to ensure correct fixture creation and prevent production queries.

#### Check What Changed

- **New source tables added?** → **Use sql-test-generator skill** to add fixtures properly to ALL existing tests
- **Source tables removed?** → Remove their fixtures from tests
- **Output schema changed?** → Update expect.yaml in tests
- **Logic changed?** → Review and update test data/expectations

#### Run Tests

```bash
pytest tests/sql/<project>/<dataset>/<table>/ -v
```

#### If Tests Fail

- ✅ **Expected failures** (schema/logic changes): Update expect.yaml to match new output
- ✅ **Missing fixtures**: **Use sql-test-generator skill** to add fixture files for any new source tables
- ❌ **Unexpected failures**: Your query changes may have introduced bugs
- ❌ **Production queries** (thousands of rows): **STOP and use sql-test-generator skill** to add missing fixtures for all source tables

#### Update Test Fixtures When Query Changes

- **Added new WHERE filter?** → Test data may need adjustment to pass the filter
- **Added new JOIN?** → **Use sql-test-generator skill** to add fixture for the joined table to ALL tests
- **Changed aggregation logic?** → Update expected counts/values in expect.yaml
- **Added new output fields?** → Add them to expect.yaml (omit if NULL)

### 5. Consider Adding New Test Scenarios

If you:
- Added complex new logic that needs validation → **Use sql-test-generator skill** to create new tests
- Added edge cases that should be tested
- Changed behavior that affects multiple code paths

## Example Workflow: Adding a New JOIN

```bash
# 1. You modify query.sql to join with telemetry.events
# 2. Update schema (if output changed)
./bqetl query schema update dataset.table

# 3. Use sql-test-generator skill to add fixtures for the new table
#    The skill will:
#    - Identify all existing test directories
#    - Create moz-fx-data-shared-prod.telemetry.events.yaml in each test
#    - Use proper data types and structure
#    - Prevent production queries

# 4. Run tests and update expect.yaml if needed
pytest tests/sql/moz-fx-data-shared-prod/<dataset>/<table>/ -v

# 5. Fix any failures by updating fixtures/expectations
```

## When to Invoke sql-test-generator Skill

- ✅ Adding new source tables (JOINs, new FROM clauses, UNION sources)
- ✅ Tests are querying production (thousands of rows in output)
- ✅ Creating new test scenarios for new logic
- ✅ Unsure about proper fixture structure or naming
- ❌ Simple expect.yaml updates (just edit the file directly)
- ❌ Removing old fixtures (just delete the files)

## Best Practice

Always run tests after query changes, even if you think they should still pass. Tests catch unexpected side effects.

## Quick Reference: Query Modification Checklist

**Before modifying:**
- [ ] Check if tests exist: `ls tests/sql/<project>/<dataset>/<table>/`
- [ ] Note what source tables the current query uses: `grep -E "FROM|JOIN" query.sql`

**After modifying:**
- [ ] Update schema: `./bqetl query schema update <dataset>.<table>`
- [ ] Add descriptions for any new fields in schema.yaml
- [ ] Identify what changed in the query:
  - [ ] New source tables added?
  - [ ] Source tables removed?
  - [ ] Output schema changed?
  - [ ] Query logic changed?

**If tests exist:**
- [ ] **If new source tables added:** Invoke `sql-test-generator` skill to add fixtures to ALL test directories
- [ ] Remove fixtures for any removed source tables (delete files)
- [ ] Run tests: `pytest tests/sql/<project>/<dataset>/<table>/ -v`
- [ ] Update expect.yaml if output schema or values changed
- [ ] **If tests query production (thousands of rows):** Invoke `sql-test-generator` skill to add missing fixtures
- [ ] **If adding new test scenarios:** Invoke `sql-test-generator` skill to create proper tests

**Common issues:**
- ❌ Test returns thousands of rows → Missing fixture for a source table
- ❌ Test fails on schema mismatch → Update expect.yaml with new fields
- ❌ Test fails on value mismatch → Update test data or expectations to match new logic
- ✅ All tests pass → Query changes are validated!
