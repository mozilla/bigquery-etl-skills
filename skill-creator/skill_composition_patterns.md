# Skill Composition and Cross-Skill Invocation

**Key Pattern:** Skills can and should invoke other skills when they encounter specialized tasks outside their primary scope. This creates a composable architecture where skills work together.

## Example: metadata-manager ↔ sql-test-generator

**Problem Solved:**
When queries are modified and tests need updating, metadata-manager detected the need for fixture updates but delegated the specialized work to sql-test-generator.

**Implementation Pattern:**
```markdown
**4. If tests exist, update them:**

**IMPORTANT:** For complex test updates (new source tables, major logic changes),
use the `sql-test-generator` skill to ensure correct fixture creation.

- New source tables added? → **Use sql-test-generator skill** to add fixtures
- Tests querying production? → **STOP and use sql-test-generator skill**
```

## When to Use Cross-Skill Invocation

**Use cross-skill invocation when:**
- ✅ Specialized domain knowledge required (test fixtures, schema validation)
- ✅ Complex operations prone to errors (production queries, type inference)
- ✅ Repetitive patterns already solved by another skill
- ✅ The other skill has bundled resources (scripts, templates) specifically designed for the task

**Don't use cross-skill invocation when:**
- ❌ Simple operations the current skill can handle directly
- ❌ Creating circular dependencies between skills
- ❌ The delegation would add unnecessary complexity
- ❌ No clear specialization boundary exists

## Best Practices

1. **Document the delegation clearly** - Explain when and why to invoke another skill
2. **Provide clear triggers** - Use bold indicators like "**Use X skill**" or "**IMPORTANT: Invoke Y skill**"
3. **Include decision criteria** - Help Claude decide between self-handling vs delegation
4. **Maintain skill boundaries** - Each skill has a primary responsibility
5. **Test the integration** - Verify the invocation pattern works in practice

## Learnings from sql-test-generator Updates

**Critical Issues Documented:**

1. **Production Query Prevention:**
   - Missing fixtures cause queries to hit production BigQuery
   - Solution: Create fixtures for ALL source tables, even if they contribute minimal data
   - Detection: Thousands of rows in output, real production values, slow queries

2. **YAML Type Inference:**
   - Version numbers like "120.0" get parsed as FLOAT64 instead of STRING
   - Solution: Use "120.0.0" (extra decimal) or "120" (simple string)
   - Critical for queries using SPLIT() on version fields

3. **Empty Fixtures:**
   - Empty arrays (`[]`) cause "Schema has no fields" errors
   - Solution: Always include at least one row of data, let WHERE clauses filter if needed

4. **UNION ALL Complexity:**
   - Multiple source tables require comprehensive test approach
   - Solution: One test with ALL sources, not separate tests per source
   - Prevents missing fixtures that fall back to production

**Documentation Updates:**
- Added prominent warnings at top of Critical Requirements
- Created detailed workflow with production query detection
- Added comprehensive Common Errors section with symptoms and solutions
- Provided UNION ALL example showing all sources in one test

## Examples of Successful Skill Composition

### metadata-manager → sql-test-generator

**Scenario:** Query modified, tests need updating

**Decision logic in metadata-manager:**
```markdown
**If tests exist, determine update approach:**

Simple changes (output columns only):
- Update expect.yaml directly
- No need to invoke sql-test-generator

Complex changes (new source tables, JOINs added):
- **Invoke sql-test-generator skill**
- Ensures all source tables have fixtures
- Prevents production queries in tests
```

### query-writer → bigquery-etl-core

**Scenario:** Writing new query, need to understand project conventions

**Decision logic in query-writer:**
```markdown
**Before writing query:**
- query-writer provides SQL writing guidance
- bigquery-etl-core is always loaded, provides project structure context
- query-writer references bigquery-etl-core conventions
```

### Any skill → bigconfig-generator

**Scenario:** New table created, need Bigeye monitoring

**Decision logic:**
```markdown
**After creating new table:**
- Query and metadata created by query-writer/metadata-manager
- If monitoring needed → **Invoke bigconfig-generator skill**
- bigconfig-generator has specialized scripts for collection discovery
```

## Anti-Patterns to Avoid

**❌ Circular Dependencies:**
```markdown
# DON'T DO THIS
skill-a: "For X, invoke skill-b"
skill-b: "For X, invoke skill-a"
```

**❌ Over-delegation:**
```markdown
# DON'T DO THIS
query-writer: "To write SELECT statement, invoke sql-syntax-helper skill"
# Query-writer should handle basic SQL syntax itself
```

**❌ Unclear Boundaries:**
```markdown
# DON'T DO THIS
metadata-manager: "Sometimes use sql-test-generator, sometimes don't"
# Provide clear decision criteria instead
```

## Creating Composable Skills

When designing new skills, consider:

1. **Define clear primary responsibility:**
   - What is this skill's core domain?
   - What should it ALWAYS handle itself?

2. **Identify boundary cases:**
   - What tasks are adjacent but specialized?
   - Where does another skill's expertise begin?

3. **Document integration points:**
   - List related skills in frontmatter or overview
   - Explain "Works with X skill for Y tasks"
   - Provide decision trees for when to delegate

4. **Test the composition:**
   - Use the skill on real tasks that cross boundaries
   - Verify invocations happen at the right times
   - Ensure smooth handoffs between skills

## Documenting Skill Relationships

**In SKILL.md frontmatter/overview:**
```markdown
---
name: example-skill
description: Does X. Works with skill-a for Y tasks and skill-b for Z tasks.
---

**Composable:** Works with skill-a, skill-b, skill-c
**When to delegate:** Use skill-a for specialized task X, skill-b for task Y
```

**In workflow sections:**
```markdown
### Step 3: Handle Special Cases

**If [condition that requires specialized skill]:**
- **STOP and invoke [specialized-skill] skill**
- Reason: [why this requires specialized skill]

**Otherwise:**
- Continue with normal workflow
```

## Measuring Success

**Good skill composition achieves:**
- ✅ Clear separation of concerns
- ✅ Reduced duplication of instructions
- ✅ Consistent handling of complex edge cases
- ✅ Easier maintenance (update in one place)
- ✅ Better results on complex multi-step tasks

**Poor skill composition results in:**
- ❌ Confusion about which skill to use
- ❌ Inconsistent handling of similar tasks
- ❌ Duplication of complex logic across skills
- ❌ Circular dependencies or unclear handoffs
