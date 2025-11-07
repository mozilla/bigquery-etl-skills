# Script Maintenance Guide

This guide covers testing, troubleshooting, and maintaining helper scripts in the metadata-manager skill.

## Helper Scripts in `scripts/`

The metadata-manager skill provides three helper scripts to improve efficiency:

### 1. **detect_teams.py** - Find GitHub teams from metadata.yaml files
- Lists all teams used across the repository
- Recommends teams for specific datasets
- Searches teams by keyword

### 2. **datahub_lineage.py** - Generate DataHub lineage query parameters
- Converts table identifiers to DataHub URNs
- Generates efficient MCP tool call parameters
- Supports upstream/downstream lineage and multiple hops

### 3. **preview_base_schema.py** - Preview base schema matches before applying
- Shows which fields would match base schemas
- Warns about description overwrites
- Recommends canonical field names for aliases
- Identifies fields missing descriptions

## Testing Scripts

**IMPORTANT: Always test scripts before using them in workflows.**

Run these tests to verify scripts are working:

```bash
# Test detect_teams.py
python3 scripts/detect_teams.py                    # List all teams
python3 scripts/detect_teams.py --dataset search   # Test dataset recommendation
python3 scripts/detect_teams.py --search revenue   # Test team search
python3 scripts/detect_teams.py --help             # Verify help works

# Test datahub_lineage.py
python3 scripts/datahub_lineage.py telemetry_derived.clients_daily_v1                  # Test basic usage
python3 scripts/datahub_lineage.py telemetry.main --direction downstream              # Test downstream
python3 scripts/datahub_lineage.py search_derived.search_clients_daily_v8 --max-hops 2  # Test max-hops
python3 scripts/datahub_lineage.py --format json telemetry.main                       # Test JSON output
python3 scripts/datahub_lineage.py --help                                            # Verify help works

# Test preview_base_schema.py
python3 scripts/preview_base_schema.py ads_derived.test_ads_bqetl_v1 --both         # Test with both schemas
python3 scripts/preview_base_schema.py relay_derived.active_subscriptions_v1        # Test global schema only
python3 scripts/preview_base_schema.py ads_derived.test_ads_bqetl_v1 --verbose      # Test verbose output
python3 scripts/preview_base_schema.py --help                                       # Verify help works
```

## When Scripts Fail

If a script fails with an error, follow this workflow:

### 1. Diagnose the Issue

Run the script manually to see the full error:
```bash
python3 scripts/script_name.py [args] 2>&1
```

Check if the error is due to:
- **Missing dependencies** (e.g., `import yaml` fails)
- **Changed file structure** (e.g., metadata.yaml format changes)
- **Invalid input format** (e.g., wrong table identifier)
- **Python syntax errors** (e.g., indentation, invalid syntax)

### 2. Auto-Update the Script

Follow these steps to fix the script:

1. **Read the script** to understand current implementation
   ```bash
   cat scripts/script_name.py
   ```

2. **Identify the failure point** from the error message
   - Look at the line number in the traceback
   - Understand what the code is trying to do

3. **Fix the issue:**
   - Update parsing logic if file formats changed
   - Add error handling for edge cases
   - Fix Python syntax or logic errors
   - Update dependencies if needed (add to requirements or imports)

4. **Test the fix** using the test commands above
   ```bash
   python3 scripts/script_name.py [test_args]
   ```

5. **Re-test all scenarios** to ensure no regressions
   - Run all test commands for that script
   - Verify edge cases still work

### 3. Document the Fix

- If the fix reveals a common issue, add it to "Common Script Issues" section below
- Update script docstring if behavior changes
- Consider adding the fix as a test case

## Common Script Issues

### detect_teams.py

**No teams found:**
- Check if metadata.yaml files have `owners` field with GitHub teams
- Team format should be: `mozilla/team_name` (not email addresses)
- Verify sql directory has metadata.yaml files

**YAML parsing errors:**
- Verify metadata.yaml files are valid YAML (proper indentation, no syntax errors)
- Check for special characters that need quoting
- Try: `python3 -c "import yaml; yaml.safe_load(open('path/to/metadata.yaml'))"`

**Permission errors:**
- Ensure script has read access to sql directory
- Try: `ls -la sql/` to check permissions

### datahub_lineage.py

**Invalid table format:**
- Ensure format is `dataset.table` or `project.dataset.table`
- Examples: `telemetry_derived.clients_daily_v1` or `moz-fx-data-shared-prod.telemetry_derived.clients_daily_v1`
- Avoid: `table` alone or `project.dataset.table.extra`

**URN construction errors:**
- Check if table identifier parsing logic needs updating
- Verify project name handling (hyphens vs underscores)
- BigQuery project format: `moz-fx-data-shared-prod`
- DataHub URN format: `urn:li:dataset:(urn:li:dataPlatform:bigquery,project.dataset.table,PROD)`

### preview_base_schema.py

**No schema.yaml found:**
- Run `./bqetl query schema update <dataset>.<table>` first to generate schema
- Verify path: `sql/moz-fx-data-shared-prod/<dataset>/<table>/schema.yaml`
- Check if query.sql exists in the table directory

**Base schema not found:**
- Check if `bigquery_etl/schema/global.yaml` exists
- Check if `bigquery_etl/schema/<dataset>.yaml` exists (for dataset-specific schemas)
- Verify you're running from the repository root

**YAML parsing errors:**
- Verify schema.yaml and base schema files are valid YAML
- Check field structure: each field needs `name`, `type`, `mode`, `description`
- Try parsing manually: `python3 -c "import yaml; yaml.safe_load(open('bigquery_etl/schema/global.yaml'))"`

**No matches found:**
- Not all fields have base schema definitions
- Check field names match exactly (case-sensitive)
- Check if aliases would match (e.g., `sub_date` → `submission_date`)
- Preview with `--verbose` to see what's being compared

## Adding New Scripts

When adding new helper scripts to this skill:

1. **Place in `scripts/` directory**
   ```bash
   touch scripts/new_script.py
   ```

2. **Add executable permissions**
   ```bash
   chmod +x scripts/new_script.py
   ```

3. **Include comprehensive docstring**
   ```python
   #!/usr/bin/env python3
   """
   Brief description of what the script does.

   Usage:
       python scripts/new_script.py [args]
       python scripts/new_script.py --help

   Examples:
       python scripts/new_script.py example_arg
   """
   ```

4. **Add test commands** to the "Testing Scripts" section above
   - Cover basic usage
   - Test edge cases
   - Verify help works

5. **Document in relevant skill sections**
   - Add to "Helper Scripts" list in SKILL.md
   - Reference in workflows where it's used
   - Update "Common Script Issues" if needed

6. **Add error handling**
   ```python
   try:
       # Main logic
   except ValueError as e:
       print(f"Error: {e}", file=sys.stderr)
       sys.exit(1)
   ```

7. **Support `--help` flag**
   ```python
   import argparse
   parser = argparse.ArgumentParser(description="...")
   ```

## Best Practices

### Script Design
- **Single responsibility:** Each script does one thing well
- **Clear input/output:** Document expected formats
- **Error messages:** Be specific about what went wrong and how to fix it
- **Exit codes:** Return 0 for success, non-zero for errors

### Error Handling
- Catch specific exceptions, not bare `except:`
- Provide actionable error messages
- Validate inputs before processing
- Fail fast with clear messages

### Testing
- Test with real repository data
- Cover edge cases (empty files, missing fields, etc.)
- Verify help text is accurate
- Test error conditions

### Documentation
- Keep docstrings up to date
- Add examples in script help
- Document assumptions (e.g., "must run from repo root")
- Reference related scripts and workflows
