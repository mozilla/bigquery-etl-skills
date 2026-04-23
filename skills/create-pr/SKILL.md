---
name: create-pr
description: Use this skill when the prompt asks to create, open, or submit a pull request in the bigquery-etl repository. Handles branch creation, staging, committing, pushing, and opening a draft PR with a structured description. Triggered by phrases like "create a PR", "open a PR", "submit a PR", "push and open a PR".
---

# create-pr

Create a pull request in the mozilla/bigquery-etl repository.

## When to Use

Invoke this skill when:
- The prompt contains "create a PR", "open a PR", "submit a PR", "push and open a PR"
- A workflow has produced files that are ready for review and need to be published

## Workflow

### Step 1: Determine Branch Name

Derive a branch name from the calling agent and table identifier:
- Format: `{agent-slug}/{table-slug}`, where `{agent-slug}` is the kebab-case name of the calling agent (e.g. `schema-creation-agent`, `query-writer`)
- If the calling agent is unknown or not applicable, use `feat` as the prefix
- `{table-slug}` is the table name with underscores replaced by hyphens, lowercase; include the dataset prefix only when needed for disambiguation
- Example: `cfs_ga4_attr_v1` in `firefox_desktop_derived` with agent `schema-creation-agent` → `schema-creation-agent/cfs-ga4-attr-v1`

Check if already on a feature branch:
```bash
git branch --show-current
```
If already on a non-`main` branch, skip branch creation. If on `main`, stash any uncommitted changes, pull latest, create the branch, then restore:
```bash
git stash
git pull origin main
git checkout -b {agent-slug}/{table-slug}
git stash pop
```

If there are no uncommitted changes, skip `git stash` and `git stash pop`.

### Step 2: Stage Generated Files

Stage only the files produced by the calling workflow. The calling agent specifies which files to stage. Stage each file explicitly — never use `git add -A` or `git add .`:

```bash
git add {file1}
git add {file2}
# ... for each file produced by the workflow
```

Omit any file that does not exist.

### Step 3: Commit

Derive the commit message from the work done by the calling workflow. Use the appropriate [conventional commit](https://www.conventionalcommits.org/) type (`feat`, `fix`, `chore`, etc.) as specified by the calling agent, defaulting to `feat` if not specified:

```bash
git commit -m "$(cat <<'EOF'
{type}({scope}): {short description of what was done}

- {one bullet per file or change}

Co-Authored-By: {model-name} <noreply@anthropic.com>
EOF
)"
```

Replace `{model-name}` with the LLM used by the calling agent, not the model running this skill. The calling agent should pass this explicitly (e.g. the value of `model:` in its frontmatter, or `$ANTHROPIC_MODEL` if set).

### Step 4: Push

```bash
git push -u origin {agent-slug}/{table-slug}
```

If the push is rejected because the branch already exists on the remote and the local branch is ahead, use `--force-with-lease`:

```bash
git push -u origin {agent-slug}/{table-slug} --force-with-lease
```

### Step 5: Open Draft PR

Check if a PR already exists for this branch:

```bash
gh pr view --json url --jq '.url' 2>/dev/null
```

If a PR already exists, skip creation and use the returned URL. Otherwise, always open as a **draft** PR. Derive the title and body from the work done by the calling workflow:

```bash
gh pr create --draft \
  --title "{type}({scope}): {short description}" \
  --body "$(cat <<'EOF'
## Summary

{brief description of what was done and why}

## Changes

- `{file1}` — {what changed and why}
- `{file2}` — {what changed and why}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Add one line per file produced by the workflow, following this format:
```
- `{file}` — {description}
```

Capture the PR number for use in Step 6 — run this regardless of whether the PR was just created or already existed:
```bash
gh pr view --json number --jq '.number'
```

### Step 6: Add Reviewers

Add all reviewers passed by the calling agent:

```bash
# for each reviewer passed by the calling agent:
gh pr edit {PR-number} --add-reviewer mozilla/{team-name}
# or for an individual:
gh pr edit {PR-number} --add-reviewer {github-username}
```

Then check the reviewers already added and add `mozilla/aero` if not among them:

```bash
gh pr view {PR-number} --json reviewRequests --jq '.reviewRequests[] | (.login // .slug)'
# if "aero" (the slug for mozilla/aero) is not in the output:
gh pr edit {PR-number} --add-reviewer mozilla/aero
```

## Output

Return to the user:
- The PR URL
- A summary of what was committed and which files were included

## Integration

This skill can be used as the final step in any agent workflow that produces files ready for review. The calling agent is responsible for completing its work before invoking this skill.
