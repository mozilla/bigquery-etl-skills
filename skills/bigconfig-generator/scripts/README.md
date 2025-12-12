# Bigconfig Generator Scripts

This directory contains utility scripts for the bigconfig-generator skill.

## extract_collections.py

Scans the repository for existing bigconfig.yml files and extracts:
- Collection names
- Notification channels (Slack, email)
- Usage frequency by dataset/product

**Output:** `../references/existing_collections.md`

### Usage

```bash
# From repository root
python3 .claude/skills/bigconfig-generator/scripts/extract_collections.py
```

### When to Run

- After significant changes to bigconfig files in the repository
- When onboarding new team members (to show current conventions)
- Periodically (monthly) to keep reference data current
- Before creating monitoring for new datasets

### What It Does

1. Recursively scans `sql/` directory for all `bigconfig.yml` files
2. Parses YAML to extract collection metadata
3. Aggregates data:
   - Counts usage per collection
   - Groups by dataset
   - Extracts notification channels
4. Generates markdown reference file with:
   - Most common collections
   - Collections by dataset
   - Guidance for choosing appropriate collections

### Benefits

- **Consistency:** Helps Claude suggest existing collections rather than creating new ones
- **Discovery:** Shows what collections and channels are already configured
- **Guidance:** Provides context-aware recommendations based on dataset/team
