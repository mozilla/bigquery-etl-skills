# Skills Overview

The BigQuery ETL Skills plugin includes 7 specialized skills that work together to accelerate your workflows.

## Anatomy of a Skill

Each skill is a folder containing instructions, templates, and reference materials that Claude loads on-demand:

```
skill-name/
├── SKILL.md                    # Main skill instructions
├── assets/                     # Templates and examples
│   ├── template1.sql
│   ├── example1.py
│   └── ...
├── references/                 # Detailed reference docs
│   ├── conventions.md
│   ├── patterns.md
│   └── ...
└── scripts/                    # Helper scripts (optional)
```

### SKILL.md

The main skill file with three key parts:

**1. Frontmatter Metadata**
```yaml
---
name: skill-name
description: When Claude should invoke this skill
---
```

The `description` field is critical—it tells Claude when to automatically invoke the skill based on user requests.

**2. Instructions**

Step-by-step guidance for completing the skill's task:

- What to read first (references, templates)
- How to approach the work
- What to generate or update
- Required validations
- When to invoke other skills

**3. Coordination Points**

Explicit instructions for working with other skills:
```markdown
## Skill Coordination
- After completing X, invoke metadata-manager
- If Y is needed, invoke sql-test-generator
```

### `assets/`

Templates and examples that Claude can read and copy:

- SQL query templates
- Python script templates
- Configuration examples
- Sample input/output data

!!! note ""
    These files provide concrete patterns to follow, reducing hallucination and ensuring consistency.

### `references/`

Detailed documentation broken into focused topics:

- Conventions and standards
- Common patterns and anti-patterns
- External documentation links
- Decision trees and workflows

!!! note ""
    Breaking knowledge into smaller files helps Claude load only what's relevant for each task.

### `scripts/` (optional)

Helper scripts for validation, generation, or analysis—used when bash operations are needed during skill execution.

## Quick Links

## Quick Links

<div class="grid cards" markdown>

- :material-download: **[Installation Guide](getting-started/installation.md)**

    Get up and running in minutes

- :material-lightning-bolt: **[Quick Start](getting-started/quick-start.md)**

    Jump right in with practical examples

</div>
