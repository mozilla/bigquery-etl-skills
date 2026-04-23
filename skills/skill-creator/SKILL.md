---
name: skill-creator
description: ALWAYS use this skill when users ask to "create a skill", "make a skill for...", "add a new skill", or similar requests. This skill guides the creation of effective skills in the bigquery-etl repository that extend Claude's capabilities with specialized knowledge for BigQuery ETL workflows, Mozilla data platform conventions, or telemetry analysis. CRITICAL - First checks for conflicts with existing skills and recommends using/updating existing skills when appropriate. Do NOT attempt to create skills without invoking this skill first.
---

# Skill Creator for BigQuery ETL

This skill provides guidance for creating effective skills tailored to the Mozilla bigquery-etl repository.

**🚨 CRITICAL FIRST STEP:** Before creating any new skill, this skill checks for conflicts with existing skills and recommends using or updating existing skills when appropriate. See **Step 0** below.

## About Skills

Skills are modular packages that extend Claude's capabilities with specialized knowledge and workflows. In bigquery-etl, they transform Claude into a specialized data engineer with Mozilla-specific expertise.

**Every skill consists of:**
```
skill-name/
├── SKILL.md (required) - Keep under 500 lines
│   ├── YAML frontmatter (name + description)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/          - Executable code for deterministic operations
    ├── references/       - Documentation loaded as needed
    └── assets/           - Templates and examples for output
```

**When to include bundled resources:**
- **Scripts**: Repetitive operations, API calls, validation logic, bqetl CLI wrappers
- **References**: Detailed documentation, conventions, complex patterns (moves detail out of SKILL.md)
- **Assets**: Query templates, metadata templates, example configurations

## Skill Creation Process

### Step 0: Check for Conflicts with Existing Skills

**CRITICAL: Before creating a new skill, check if an existing skill already covers this functionality.**

1. **Review existing skills** to understand their scope:
   - **bigquery-etl-core** - Project structure, conventions, naming patterns, schema discovery
   - **model-requirements** - Requirements gathering for new/modified data models
   - **query-writer** - SQL and Python query writing, formatting, validation
   - **metadata-manager** - Schema.yaml, metadata.yaml, dags.yaml generation and updates
   - **sql-test-generator** - Unit test fixtures for SQL queries
   - **bigconfig-generator** - Bigeye monitoring configurations for data quality
   - **column-description-finder** - Look up and audit column descriptions from base schema YAML files
   - **schema-enricher** - Enrich schema.yaml with descriptions; generates _missing_metadata.yaml
   - **schema-readme-generator** - Create or update README.md files for BigQuery ETL tables
   - **base-schema-audit** - Audit tables for missing descriptions and classify into base schema promotion targets; runs across a dataset or filtered to a table prefix
   - **glean-description-lookup** - Look up field descriptions for Mozilla Glean metrics
   - **create-pr** - Create, push, and open a draft pull request
   - **skill-creator** - Meta-skill for creating new skills

2. **Analyze the requested functionality:**
   - What specific task does the user want to accomplish?
   - Does any existing skill already handle this or a closely related task?
   - Is this a new workflow or an enhancement to an existing one?

3. **Check for conflicts or overlap:**
   - If an existing skill already covers 80%+ of the requested functionality → **Recommend updating the existing skill**
   - If the functionality spans multiple existing skills → **Recommend coordinating between existing skills**
   - If the functionality is orthogonal to existing skills → **Proceed with creating a new skill**

4. **Inform the user of findings:**
   ```
   Before creating a new skill, I checked the existing skills:

   [If conflict found]
   The functionality you described overlaps significantly with the [existing-skill] skill, which handles [description].

   You have two options:
   1. **Use the existing skill**: [Brief guidance on how to use it]
   2. **Update the existing skill**: If the current skill doesn't fully meet your needs, we can enhance it by [specific improvements]

   Which would you prefer?

   [If no conflict]
   This appears to be a new capability that doesn't conflict with existing skills. Let's proceed with creating a new skill.
   ```

5. **Only proceed to Step 1 if:**
   - User confirms they want a new skill after understanding existing options, OR
   - No significant overlap exists with current skills

### Step 1: Understand with Examples
Skip if usage patterns are already clear.

Ask user for concrete examples of how the skill will be used:
- What specific tasks will this skill help with?
- What are example requests you'd make?
- What existing workflows does this improve?

### Step 2: Plan Reusable Contents
Analyze each example to identify helpful resources:
- What scripts would automate repetitive operations?
- What references contain detailed conventions or patterns?
- What assets provide templates or examples?

### Step 3: Initialize the Skill
Skip if skill already exists.

New skills belong in the `bigquery-etl-skills` repository, not in `bigquery-etl`. From the `bigquery-etl-skills` repo root:

```bash
mkdir -p skills/<skill-name>/{scripts,references,assets}
```

After creating files, register the skill in `.claude-plugin/marketplace.json` by adding `"./skills/<skill-name>"` to the `skills` array — without this the plugin will not load the new skill.

Create SKILL.md with frontmatter:
```yaml
---
name: skill-name
description: Detailed description of when and how to use this skill for BigQuery ETL tasks.
---
```

### Step 4: Edit the Skill

**Create bundled resources first** (scripts, references, assets identified in Step 2).

**Then write SKILL.md:**
- Use imperative/infinitive form (not second person)
- Keep under 500 lines - move details to references
- Add "🚨 REQUIRED READING" section for critical references
- Document integration with other skills
- Include concrete examples

**Answer these questions:**
1. What is the skill's purpose?
2. When should it be used?
3. How should Claude use it?
4. What bundled resources are available and when to use them?
5. How does it integrate with other skills?

**For detailed guidance:**
- **READ `references/explicit_instructions_pattern.md`** for how to ensure Claude reads assets and references

### Step 5: Validate the Skill

**Structure:**
- [ ] SKILL.md with proper frontmatter exists
- [ ] Under 500 lines
- [ ] Name and description are clear and specific

**Content:**
- [ ] Imperative form, not second person
- [ ] Mozilla/BigQuery ETL conventions referenced
- [ ] Integration with other skills documented
- [ ] Examples relevant to bigquery-etl

**Resources:**
- [ ] Scripts are executable
- [ ] References contain non-obvious valuable information
- [ ] No duplication between SKILL.md and references

### Step 6: Iterate

After testing, users may request improvements:
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Update SKILL.md or bundled resources
4. Test again

**Common improvements:**
- Add templates for edge cases
- Expand references with new conventions
- Add examples for complex scenarios
- Document critical failure modes prominently

## Existing BigQuery ETL Skills

**IMPORTANT: Always check these before creating a new skill (see Step 0).**

**Foundation:**
- **bigquery-etl-core** - Project structure, conventions, naming patterns, schema discovery, DataHub best practices (works with all skills)

**Construction workflows:**
- **model-requirements** - Gather requirements for new/modified data models, understand existing queries and dependencies
- **query-writer** - Write and update query.sql and query.py files, SQL formatting, query validation
- **metadata-manager** - Generate/update schema.yaml, metadata.yaml, dags.yaml files
- **sql-test-generator** - Create and update unit test fixtures for SQL queries
- **bigconfig-generator** - Create Bigeye monitoring configurations for data quality checks

**Schema workflows:**
- **column-description-finder** - Look up, audit, and manage column descriptions from base schema YAML files; audit a table's base schema coverage
- **schema-enricher** - Enrich schema.yaml files with column descriptions from base schemas, upstream sources, and query/application context; generates _missing_metadata.yaml
- **schema-readme-generator** - Create or update README.md files for BigQuery ETL tables
- **base-schema-audit** - Audit tables for missing column descriptions and classify each into the correct base schema promotion target (global.yaml, app_<product>.yaml, <dataset_name>.yaml); runs across an entire dataset or filtered to a table prefix

**Discovery:**
- **glean-description-lookup** - Look up field descriptions for Mozilla Glean metrics from the Glean Dictionary

**Deployment:**
- **create-pr** - Create, push, and open a draft pull request for completed work

**Meta:**
- **skill-creator** - Create new skills with conflict checking

## Quick Tips

1. **Leverage existing infrastructure** - bqetl CLI, ProbeInfo API, DataHub MCP
2. **Focus on Mozilla-specific knowledge** - conventions that aren't obvious
3. **Make skills composable** - reference other skills, build on bigquery-etl-core
4. **Keep SKILL.md concise** - move details to references
5. **Use scripts for token efficiency** - scripts execute without consuming context
6. **Document critical failures prominently** - add warnings at the TOP with ⚠️ indicators
7. **Make resources explicit** - use "READ `file.md`" instructions in workflows
8. **Test with real workflows** - validate on actual bigquery-etl tasks
9. **Iterate based on usage** - update documentation when issues are encountered

## Reference Documentation

For detailed guidance on specific topics, read these reference files:

- **`references/mozilla_ecosystem.md`** - Mozilla data platform tools, repositories, APIs, and configuration files for construction-focused skills beyond bigquery-etl
- **`references/skill_composition_patterns.md`** - How to create composable skills that work together, with examples and anti-patterns
- **`references/explicit_instructions_pattern.md`** - How to ensure Claude reads assets and references using standardized sections and clear directives
- **`references/potential_script_opportunities.md`** - When to use scripts in skills and high-priority script opportunities for existing skills
