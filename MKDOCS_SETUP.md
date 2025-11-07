# MkDocs Documentation Setup

This document explains the MkDocs setup for BigQuery ETL Skills documentation.

## What's Been Set Up

### 1. MkDocs Configuration

**File:** `mkdocs.yml`

- Material theme with dark/light mode
- Navigation structure for all skills and examples
- Search functionality
- Code highlighting
- GitHub integration

### 2. Documentation Structure

```
docs/
├── index.md                          ✅ Homepage
├── getting-started/
│   ├── installation.md              ✅ Installation guide
│   ├── quick-start.md               ✅ Quick start examples
│   └── using-skills.md              ✅ How to use skills
├── skills/
│   ├── overview.md                  ✅ Skills overview
│   ├── bigquery-etl-core.md         🚧 Placeholder
│   ├── model-requirements.md        🚧 Placeholder
│   ├── query-writer.md              🚧 Placeholder
│   ├── metadata-manager.md          🚧 Placeholder
│   ├── sql-test-generator.md        🚧 Placeholder
│   ├── bigconfig-generator.md       🚧 Placeholder
│   └── skill-creator.md             🚧 Placeholder
├── examples/
│   ├── workflows.md                 ✅ Common workflows
│   ├── creating-queries.md          🚧 Placeholder
│   ├── updating-queries.md          🚧 Placeholder
│   ├── generating-tests.md          🚧 Placeholder
│   └── adding-monitoring.md         🚧 Placeholder
├── contributing/
│   ├── guidelines.md                ✅ Contribution guidelines
│   └── testing.md                   ✅ Testing guidelines
└── reference/
    ├── changelog.md                 ✅ Changelog
    └── versions.md                  ✅ Version history
```

### 3. GitHub Actions Workflow

**File:** `.github/workflows/deploy-docs.yml`

Automatically deploys documentation to GitHub Pages on push to main.

### 4. Dependencies

**File:** `requirements.txt`

- mkdocs
- mkdocs-material
- pymdown-extensions

## Testing Locally

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Serve Documentation Locally

```bash
mkdocs serve
```

Then visit: http://127.0.0.1:8000

### Build Documentation

```bash
mkdocs build
```

This creates a `site/` directory with static HTML.

## Deploying to GitHub Pages

### First-Time Setup

1. Ensure GitHub Pages is enabled for the repository:
   - Go to repository Settings > Pages
   - Source should be "Deploy from a branch"
   - Branch should be "gh-pages"

2. Push changes to trigger the workflow:
   ```bash
   git push origin main
   ```

3. The GitHub Action will automatically build and deploy

### Manual Deployment

If needed, you can manually deploy:

```bash
mkdocs gh-deploy
```

## What Still Needs to Be Done

### High Priority

1. **Individual Skill Pages** (7 pages)
   - Extract content from each skill's SKILL.md
   - Create structured documentation with:
     - Overview
     - When to use
     - Key features
     - Examples
     - Reference to bundled resources

2. **Example Pages** (4 pages)
   - Create detailed walkthroughs for:
     - Creating new queries
     - Updating existing queries
     - Generating tests
     - Adding monitoring

### Medium Priority

3. **Skill Assets Documentation**
   - Document templates and examples from each skill's assets/
   - Link from skill pages to relevant assets

4. **Reference Documentation**
   - Create pages for key reference files
   - Link from relevant sections

### Low Priority

5. **Search Optimization**
   - Add meta descriptions
   - Improve heading structure
   - Add tags/keywords

6. **Visual Enhancements**
   - Add diagrams (workflow diagrams already included)
   - Add screenshots where helpful
   - Create visual guides

## Updating Documentation

### Adding a New Page

1. Create the markdown file in `docs/`
2. Add it to the nav in `mkdocs.yml`
3. Test locally with `mkdocs serve`
4. Commit and push

### Updating Existing Pages

1. Edit the markdown file
2. Test locally
3. Commit and push (auto-deploys)

### Updating Navigation

Edit the `nav:` section in `mkdocs.yml`

## Tips

- Use admonitions for notes, warnings, tips:
  ```markdown
  !!! note "Title"
      Content here
  ```

- Add code blocks with syntax highlighting:
  ````markdown
  ```python
  code here
  ```
  ````

- Link between pages:
  ```markdown
  [Link text](../other-page.md)
  ```

- Add images:
  ```markdown
  ![Alt text](../images/image.png)
  ```

## GitHub Pages URL

Once deployed, documentation will be available at:

**https://mozilla.github.io/bigquery-etl-skills/**

## Maintenance

- Keep documentation in sync with skill changes
- Update examples when workflows change
- Review and update periodically for accuracy
- Monitor GitHub Actions for build failures
